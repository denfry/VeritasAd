import whisper
import torch
from pathlib import Path
from typing import Dict, Optional
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
        logger.info(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Advertising keywords (Russian)
        self.ad_keywords = [
            "@5:;0<0", "?@><>:>4", "A:84:0", "0:F8O", "A?>=A>@",
            "?0@B=5@", "1>=CA", ":MH15:", ":C?>=", "@0A?@>4060",
            "?@54;>65=85", "CAB0=>28BL", "A:0G0BL", "70@538AB@8@",
            "?@8;>65=8", "A09B", "AAK;:0", ">?8A0=8", "?5@5E>4",
            "28=;09=", "winline", "1C:<5:5@", "AB02:", ":>MDD8F85=B",
            "D@815B", "freebet", "45?>78B", "2K2>4"
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

    def transcribe(self, audio_path: Path) -> Dict[str, any]:
        """
        Transcribe audio using Whisper

        Args:
            audio_path: Path to audio file

        Returns:
            Transcription results with text and segments
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")

            result = self.model.transcribe(
                str(audio_path),
                language="ru",
                task="transcribe",
                fp16=False if self.device == "cpu" else True
            )

            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result.get("language", "ru")
            }

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {"text": "", "segments": [], "language": "ru"}

    def detect_ad_keywords(self, text: str) -> Dict[str, any]:
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

    def analyze(self, video_path: Path) -> Dict[str, any]:
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
