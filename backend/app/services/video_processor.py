from pathlib import Path
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import cv2
from typing import Dict, Optional
import logging
import time
from datetime import datetime
import uuid
import subprocess
import shutil

from app.services.audio_analyzer import AudioAnalyzer
from app.services.disclosure_detector import DisclosureDetector

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Complete video analysis pipeline"""

    def __init__(self, use_llm: bool = False):
        """
        Initialize video processor with all required models

        Args:
            use_llm: Whether to use LLM for disclosure detection
        """
        logger.info("Initializing Video Processor")

        # CLIP for logo/brand detection
        logger.info("Loading CLIP model")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Brand list (can be expanded)
        self.brands = [
            "Winline", "1xBet", "Fonbet", "Betboom", "Leon",
            "Nike", "Adidas", "Apple", "Samsung", "Coca-Cola",
            "McDonald's", "KFC", "Burger King", "Pepsi", "Sprite"
        ]

        # Initialize sub-analyzers
        self.audio_analyzer = AudioAnalyzer(model_size="tiny")
        self.disclosure_detector = DisclosureDetector(use_llm=use_llm)

        # Output directories
        self.raw_dir = Path("../data/raw")
        self.processed_dir = Path("../data/processed")
        self.raw_dir.mkdir(exist_ok=True, parents=True)
        self.processed_dir.mkdir(exist_ok=True, parents=True)

        logger.info("Video Processor initialized successfully")

    def download_video(self, url: str) -> Optional[Path]:
        """
        Download video from URL using yt-dlp

        Args:
            url: Video URL

        Returns:
            Path to downloaded video or None
        """
        try:
            video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
            video_path = self.raw_dir / f"{video_id}.mp4"

            logger.info(f"Downloading video from: {url}")

            cmd = [
                "yt-dlp",
                "-o", str(video_path),
                "--retries", "3",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                url
            ]

            # Add cookies for Telegram
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode != 0:
                logger.error(f"yt-dlp error: {result.stderr}")
                return None

            if not video_path.exists():
                logger.error("Video file not found after download")
                return None

            logger.info(f"Video downloaded: {video_path}")
            return video_path

        except Exception as e:
            logger.error(f"Video download failed: {str(e)}")
            return None

    def get_video_metadata(self, video_path: Path) -> Dict[str, any]:
        """Extract video metadata"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            duration = frame_count / fps if fps > 0 else 0

            return {
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "file_size": video_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {}

    def detect_logos(self, video_path: Path) -> Dict[str, any]:
        """
        Detect brand logos in video frames using CLIP

        Args:
            video_path: Path to video file

        Returns:
            Detection results with scores and detected brands
        """
        try:
            logger.info("Starting logo detection")
            cap = cv2.VideoCapture(str(video_path))

            frames = []
            frame_numbers = []
            timestamps = []

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            sample_interval = max(1, int(fps * 2))  # Sample every 2 seconds

            while cap.isOpened() and len(frames) < 30:  # Max 30 frames
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % sample_interval == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    frames.append(pil_image)
                    frame_numbers.append(frame_count)
                    timestamps.append(frame_count / fps if fps > 0 else 0)

                frame_count += 1

            cap.release()

            if not frames:
                logger.warning("No frames extracted for logo detection")
                return {"score": 0.0, "detected_brands": [], "frame_count": 0}

            # Run CLIP inference
            inputs = self.clip_processor(
                text=self.brands,
                images=frames,
                return_tensors="pt",
                padding=True
            )

            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1)

            # Analyze results
            detected_brands = []
            max_scores = []

            for idx, frame_probs in enumerate(probs):
                max_prob, max_idx = frame_probs.max(dim=0)
                max_scores.append(max_prob.item())

                if max_prob.item() > 0.25:  # Threshold
                    brand = self.brands[max_idx.item()]
                    detected_brands.append({
                        "name": brand,
                        "confidence": max_prob.item(),
                        "frame": frame_numbers[idx],
                        "timestamp": timestamps[idx]
                    })

            # Calculate overall score
            avg_score = sum(max_scores) / len(max_scores) if max_scores else 0.0
            visual_score = min(1.0, avg_score * 1.5)  # Amplify signal

            # Group by brand
            brand_detections = {}
            for det in detected_brands:
                brand = det["name"]
                if brand not in brand_detections:
                    brand_detections[brand] = {
                        "name": brand,
                        "confidence": det["confidence"],
                        "timestamps": [det["timestamp"]]
                    }
                else:
                    brand_detections[brand]["timestamps"].append(det["timestamp"])
                    brand_detections[brand]["confidence"] = max(
                        brand_detections[brand]["confidence"],
                        det["confidence"]
                    )

            logger.info(f"Logo detection complete. Score: {visual_score:.2f}")

            return {
                "score": visual_score,
                "detected_brands": list(brand_detections.values()),
                "frame_count": len(frames),
                "detections": detected_brands
            }

        except Exception as e:
            logger.error(f"Logo detection failed: {str(e)}")
            return {"score": 0.0, "detected_brands": [], "frame_count": 0}

    async def process(self, file=None, url: str = None) -> Dict[str, any]:
        """
        Complete video processing pipeline

        Args:
            file: Uploaded file
            url: Video URL

        Returns:
            Complete analysis results
        """
        start_time = time.time()
        video_path = None

        try:
            # Get video file
            if file:
                # Save uploaded file
                video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
                video_path = self.raw_dir / f"{video_id}.mp4"

                with open(video_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                source = "file"
                source_url = None

            elif url:
                video_path = self.download_video(url)
                if not video_path:
                    raise Exception("Video download failed")
                source = "url"
                source_url = url

            else:
                raise Exception("No video file or URL provided")

            logger.info(f"Processing video: {video_path}")

            # Extract metadata
            metadata = self.get_video_metadata(video_path)

            # Run parallel analysis
            logger.info("Running visual analysis")
            visual_result = self.detect_logos(video_path)

            logger.info("Running audio analysis")
            audio_result = self.audio_analyzer.analyze(video_path)

            logger.info("Running disclosure detection")
            disclosure_result = self.disclosure_detector.analyze(
                text=audio_result.get("transcript", ""),
                description=""
            )

            # Calculate final scores
            visual_score = visual_result["score"]
            audio_score = audio_result["score"]
            text_score = audio_score  # Same as audio for now
            disclosure_score = disclosure_result["score"]

            # Weighted final score
            confidence_score = (
                visual_score * 0.3 +
                audio_score * 0.3 +
                text_score * 0.2 +
                disclosure_score * 0.2
            )

            has_advertising = confidence_score > 0.5

            processing_time = time.time() - start_time

            result = {
                "video_id": video_path.stem,
                "status": "completed",
                "has_advertising": has_advertising,
                "confidence_score": confidence_score,

                # Detailed scores
                "visual_score": visual_score,
                "audio_score": audio_score,
                "text_score": text_score,
                "disclosure_score": disclosure_score,

                # Detections
                "detected_brands": visual_result["detected_brands"],
                "detected_keywords": audio_result["keywords"],
                "transcript": audio_result["transcript"],
                "disclosure_text": disclosure_result.get("markers", []),

                # Metadata
                "source": source,
                "source_url": source_url,
                "duration": metadata.get("duration", 0),
                "processing_time": processing_time,
                "file_path": str(video_path)
            }

            logger.info(f"Analysis complete. Result: {has_advertising}, Score: {confidence_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            processing_time = time.time() - start_time

            return {
                "video_id": video_path.stem if video_path else "unknown",
                "status": "failed",
                "error": str(e),
                "processing_time": processing_time
            }