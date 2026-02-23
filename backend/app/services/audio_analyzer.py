from faster_whisper import WhisperModel
import torch
from pathlib import Path
from typing import Dict, Optional, Any
import subprocess
import logging

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyze audio from videos for advertising detection"""

    def __init__(self, model_size: str = "tiny"):
        """
        Initialize Whisper model for audio transcription

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if self.device == "cuda" else "int8"
        logger.info(f"Loading Whisper model: {model_size} ({self.device}, {compute_type})")
        self.model = WhisperModel(model_size, device=self.device, compute_type=compute_type)

        # Advertising keywords (Russian)
        self.ad_keywords = [
            "реклама", "промокод", "скидка", "акция", "спонсор",
            "партнер", "бонус", "кэшбек", "купон", "распродажа",
            "предложение", "установить", "скачать", "зарегистрир",
            "приложени", "сайт", "ссылка", "описани", "переход",
            "винлайн", "winline", "букмекер", "ставка", "коэффициент",
            "фрибет", "freebet", "депозит", "вывод",
            "альфа", "альфабанк", "alfa bank", "alfabank",
        ]

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

            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg", "-i", str(video_path),
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

    def analyze(self, video_path: Path) -> Dict[str, Any]:
        """
        Complete audio analysis pipeline

        Args:
            video_path: Path to video file

        Returns:
            Complete analysis results
        """
        try:
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

            # Clean up audio file
            try:
                audio_path.unlink()
            except:
                pass

            return {
                "transcript": transcription["text"],
                "keywords": [k["keyword"] for k in keyword_analysis["detected_keywords"]],
                "keyword_details": keyword_analysis["detected_keywords"],
                "score": keyword_analysis["score"],
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