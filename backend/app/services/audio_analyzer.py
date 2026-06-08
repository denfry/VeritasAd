from faster_whisper import WhisperModel
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import shutil
import logging

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyze audio from videos for advertising detection"""

    def __init__(self, model_size: str = "tiny"):
        """
        Initialize Whisper model for audio transcription using ModelManager
        """
        from app.services.model_manager import model_manager
        self.model = model_manager.get_whisper()
        if self.model is None:
            logger.warning("Audio transcription disabled because Whisper failed to load")

        # Optional MFCC+KNN acoustic classifier (loaded lazily on first use).
        self._knn_model = None
        self._knn_loaded = False

        # Advertising keywords (Russian). Kept ad-specific on purpose: generic
        # shopping-vlog words ("купить", "деньги") are deliberately excluded so
        # organic shopping footage is not flagged. Substrings are matched, so
        # stems ("гарант", "аромат") catch inflected forms and Whisper typos.
        self.ad_keywords = [
            # disclosure / CTA stems
            "реклама", "промокод", "скидка", "акция", "спонсор",
            "партнер", "бонус", "кэшбек", "купон", "распродажа",
            "предложение", "установить", "скачать", "зарегистрир",
            "приложени", "сайт", "ссылка", "описани", "переход",
            "эксклюзивно", "официальн", "оригинальн",
            # commerce / marketplace
            "магазин", "доставка", "заказывай", "маркетплейс", "артикул",
            "гарантия", "гарант", "ассортимент", "новинка", "коллекция",
            "вайлдберриз", "вайлбер", "wildberries", "озон", "ozon",
            # product categories that head these integrations
            "смартфон", "гаджет", "телефон", "наушник",
            "духи", "парфюм", "аромат", "косметик", "набор", "подарок",
            "ударопрочн", "аккумулятор", "мегапиксел",
            # bookmakers / banks (legacy)
            "винлайн", "winline", "букмекер", "ставка", "коэффициент",
            "фрибет", "freebet", "депозит", "вывод",
            "альфа", "альфабанк", "alfa bank", "alfabank",
        ]

    def _resolve_ffmpeg_executable(self) -> Optional[str]:
        """Find an ffmpeg executable, preferring the system binary and then an embedded fallback."""
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg

        try:
            from imageio_ffmpeg import get_ffmpeg_exe

            bundled_ffmpeg = get_ffmpeg_exe()
            if bundled_ffmpeg and Path(bundled_ffmpeg).exists():
                return bundled_ffmpeg
        except Exception as exc:
            logger.debug("Bundled ffmpeg fallback unavailable", error=str(exc))

        return None

    def extract_audio(self, video_path: Path) -> Optional[Path]:
        """
        Extract audio from video file

        Args:
            video_path: Path to video file

        Returns:
            Path to extracted audio file or None on error
        """
        try:
            audio_path = video_path.with_suffix(".wav")
            ffmpeg_executable = self._resolve_ffmpeg_executable()
            if not ffmpeg_executable:
                logger.error("ffmpeg executable not found")
                return None

            # Use ffmpeg to extract audio
            cmd = [
                ffmpeg_executable, "-i", str(video_path),
                "-vn",  # No video
                "-acodec", "pcm_s16le",  # PCM codec
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",  # Mono
                "-y",  # Overwrite
                str(audio_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None

            return audio_path

        except Exception as e:
            logger.error(f"Audio extraction failed: {str(e)}")
            return None

    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper

        Args:
            audio_path: Path to audio file

        Returns:
            Transcription results with text and segments
        """
        try:
            if self.model is None:
                return {"text": "", "segments": [], "language": "unknown"}

            logger.info(f"Transcribing audio: {audio_path}")

            segments, info = self.model.transcribe(
                str(audio_path),
                language=None,
                task="transcribe",
            )

            transcript = []
            segment_list = []
            for segment in segments:
                transcript.append(segment.text)
                segment_list.append(
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                    }
                )

            return {
                "text": " ".join(transcript).strip(),
                "segments": segment_list,
                "language": info.language or "unknown",
            }

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {"text": "", "segments": [], "language": "unknown"}

    def detect_ad_keywords(self, text: str) -> Dict[str, Any]:
        """
        Detect advertising keywords in text

        Args:
            text: Transcribed text

        Returns:
            Dictionary with detected keywords and score
        """
        text_lower = text.lower()
        detected = []

        for keyword in self.ad_keywords:
            if keyword in text_lower:
                # Count occurrences
                count = text_lower.count(keyword)
                detected.append({
                    "keyword": keyword,
                    "count": count
                })

        # Calculate advertising score
        score = min(1.0, len(detected) * 0.15)  # Max 1.0

        return {
            "detected_keywords": detected,
            "score": score,
            "total_keywords": len(detected)
        }

    def extract_mfcc_windows(self, audio_path: Path) -> "np.ndarray":
        """Extract MFCC feature vectors over sliding windows.

        Per thesis sec. 3.2: 40 MFCC coefficients computed on a 2-second window
        with 50% overlap (1-second hop) at 16 kHz. Each window is reduced to a
        fixed-length vector by mean-pooling the coefficients over time.

        Returns:
            A 2D array of shape (n_windows, n_mfcc); empty array on failure.
        """
        try:
            import librosa

            y, sr = librosa.load(str(audio_path), sr=settings.AUDIO_SAMPLE_RATE)
            if y is None or len(y) == 0:
                return np.empty((0, settings.AUDIO_MFCC_COUNT))

            window_len = int(settings.AUDIO_WINDOW_SECONDS * sr)
            hop = max(1, int(window_len * (1.0 - settings.AUDIO_WINDOW_OVERLAP)))
            if window_len <= 0:
                return np.empty((0, settings.AUDIO_MFCC_COUNT))

            features: List[np.ndarray] = []
            for start in range(0, max(1, len(y) - window_len + 1), hop):
                segment = y[start:start + window_len]
                if len(segment) < window_len // 2:
                    break
                mfcc = librosa.feature.mfcc(
                    y=segment, sr=sr, n_mfcc=settings.AUDIO_MFCC_COUNT
                )
                features.append(mfcc.mean(axis=1))

            if not features:
                return np.empty((0, settings.AUDIO_MFCC_COUNT))
            return np.vstack(features)
        except Exception as e:
            logger.warning(f"MFCC extraction failed: {e}")
            return np.empty((0, settings.AUDIO_MFCC_COUNT))

    def _load_knn(self):
        """Lazily load the trained KNN classifier from disk (if available)."""
        if self._knn_loaded:
            return self._knn_model
        self._knn_loaded = True
        model_path = settings.AUDIO_KNN_MODEL_PATH
        if not model_path:
            return None
        path = Path(model_path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[3] / model_path
        if not path.exists():
            logger.info("Audio KNN model not found at %s; using keyword fallback", path)
            return None
        try:
            import joblib

            self._knn_model = joblib.load(path)
            logger.info("Audio KNN model loaded from %s", path)
        except Exception as e:
            logger.warning(f"Failed to load audio KNN model: {e}")
            self._knn_model = None
        return self._knn_model

    def detect_ad_acoustics(self, audio_path: Path) -> Dict[str, Any]:
        """Acoustic ad probability via MFCC + KNN (k=5).

        Returns the mean predicted ad-probability across windows and the
        per-window probabilities. Returns ``available=False`` when no trained
        model is present so callers can fall back to keyword detection.
        """
        knn = self._load_knn()
        if knn is None:
            return {"available": False, "score": 0.0, "window_probabilities": []}

        features = self.extract_mfcc_windows(audio_path)
        if features.shape[0] == 0:
            return {"available": True, "score": 0.0, "window_probabilities": []}

        try:
            # Probability of the positive ("ad") class for each window.
            if hasattr(knn, "predict_proba"):
                classes = list(getattr(knn, "classes_", [0, 1]))
                ad_index = classes.index(1) if 1 in classes else len(classes) - 1
                probs = knn.predict_proba(features)[:, ad_index]
            else:
                probs = knn.predict(features).astype(float)
            window_probs = [float(p) for p in probs]
            score = float(np.mean(window_probs)) if window_probs else 0.0
            return {
                "available": True,
                "score": min(1.0, max(0.0, score)),
                "window_probabilities": window_probs,
            }
        except Exception as e:
            logger.warning(f"Audio KNN inference failed: {e}")
            return {"available": False, "score": 0.0, "window_probabilities": []}

    def analyze(self, video_path: Path) -> Dict[str, Any]:
        """
        Complete audio analysis pipeline

        Args:
            video_path: Path to video file

        Returns:
            Complete analysis results
        """
        try:
            if self.model is None:
                return {
                    "transcript": "",
                    "keywords": [],
                    "score": 0.0,
                    "error": "Whisper model unavailable",
                }

            # Extract audio
            audio_path = self.extract_audio(video_path)
            if not audio_path or not audio_path.exists():
                logger.warning("Audio extraction failed, skipping audio analysis")
                return {
                    "transcript": "",
                    "keywords": [],
                    "score": 0.0,
                    "error": "Audio extraction failed"
                }

            # Transcribe
            transcription = self.transcribe(audio_path)

            # Detect keywords
            keyword_analysis = self.detect_ad_keywords(transcription["text"])

            # Acoustic MFCC + KNN probability (optional model).
            acoustic = self.detect_ad_acoustics(audio_path)

            # Clean up audio file
            try:
                audio_path.unlink()
            except Exception:
                pass

            keyword_score = keyword_analysis["score"]
            if acoustic.get("available"):
                # Combine keyword evidence with acoustic ad-probability; the
                # acoustic channel cannot lower a strong keyword signal.
                combined_score = max(keyword_score, float(acoustic.get("score", 0.0)))
            else:
                combined_score = keyword_score

            return {
                "transcript": transcription["text"],
                "keywords": [k["keyword"] for k in keyword_analysis["detected_keywords"]],
                "keyword_details": keyword_analysis["detected_keywords"],
                "score": min(1.0, combined_score),
                "keyword_score": keyword_score,
                "acoustic_score": float(acoustic.get("score", 0.0)),
                "acoustic_available": bool(acoustic.get("available", False)),
                "segments": transcription["segments"]
            }

        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            return {
                "transcript": "",
                "keywords": [],
                "score": 0.0,
                "error": str(e)
            }
