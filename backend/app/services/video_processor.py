from pathlib import Path
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import cv2
from typing import Dict, Optional, Callable, Awaitable, List, Any, Set
import logging
import time
from datetime import datetime
import uuid
import subprocess
import shutil
import asyncio
import re
import sys

from app.services.audio_analyzer import AudioAnalyzer
from app.services.disclosure_detector import DisclosureDetector
from app.services.brand_ocr import BrandOCR
from app.services.cloud_brand_detector import CloudBrandDetector
from app.core.config import settings
from app.utils.ad_classification import classify_advertising

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Complete video analysis pipeline"""

    def __init__(self, use_llm: bool = False, custom_brands: List[str] = None):
        """
        Initialize video processor with all required models

        Args:
            use_llm: Whether to use LLM for disclosure detection
            custom_brands: Optional list of custom brand names to detect
        """
        logger.info("Initializing Video Processor")

        # CLIP for logo/brand detection
        logger.info(f"Loading CLIP model: {settings.CLIP_MODEL}")
        self.clip_model = CLIPModel.from_pretrained(settings.CLIP_MODEL)
        self.clip_processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL)

        # Load brand aliases from config
        self.brand_aliases = settings.get_brand_aliases()
        
        # Create reverse alias mapping (alias -> brand)
        self.alias_to_brand = {}
        if settings.ENABLE_BRAND_ALIASES and self.brand_aliases:
            for brand, aliases in self.brand_aliases.items():
                for alias in aliases:
                    self.alias_to_brand[alias.lower()] = brand

        # Extended brand list with categories
        default_brands = [
            # Bookmakers (Р‘СѓРєРјРµРєРµСЂС‹)
            "Winline", "1xBet", "Fonbet", "Betboom", "Leon", "Melbet",
            "Parimatch", "Baltbet", "Betcity", "Olimp", "Marathonbet",
            "Pinnacle", "William Hill", "Bet365", "Unibet", "888sport",
            
            # Banks (Р‘Р°РЅРєРё)
            "Alfa Bank", "Alfabank", "РђР»СЊС„Р° Р‘Р°РЅРє", "РђР»СЊС„Р°-Р‘Р°РЅРє", "Alfa",
            "Sberbank", "РЎР±РµСЂР±Р°РЅРє", "РЎР±РµСЂ", "Tinkoff", "РўРёРЅСЊРєРѕС„С„", "T-Bank",
            "VTB", "Р’РўР‘", "Gazprombank", "Р“Р°Р·РїСЂРѕРјР±Р°РЅРє", "Rosbank", "Р РѕСЃР±Р°РЅРє",
            "Raiffeisen", "Р Р°Р№С„С„Р°Р№Р·РµРЅ", "Otkritie", "РћС‚РєСЂС‹С‚РёРµ", "Sovcombank",
            "РЎРѕРІРєРѕРјР±Р°РЅРє", "MKB", "РњРўРЎ Р‘Р°РЅРє", "Ak Bars", "РђРљ Р‘РђР РЎ",
            
            # Technology (РўРµС…РЅРѕР»РѕРіРёРё)
            "Apple", "Samsung", "Xiaomi", "Huawei", "Honor", "OnePlus",
            "Google", "Microsoft", "Intel", "AMD", "NVIDIA", "ASUS",
            "Lenovo", "HP", "Dell", "Acer", "LG", "Sony", "Panasonic",
            
            # Telecom (РўРµР»РµРєРѕРј)
            "MTS", "РњРўРЎ", "Beeline", "Р‘РёР»Р°Р№РЅ", "MegaFon", "РњРµРіР°Р¤РѕРЅ",
            "Tele2", "Р РѕСЃС‚РµР»РµРєРѕРј", "Rostelecom", "Yota",
            
            # Food & Restaurants (Р•РґР° Рё СЂРµСЃС‚РѕСЂР°РЅС‹)
            "McDonald's", "KFC", "Burger King", "Rostic's", "Р’РєСѓСЃРЅРѕ Рё С‚РѕС‡РєР°",
            "Dodo Pizza", "Р”РѕРґРѕ РџРёС†С†Р°", "Papa John's", "Pizza Hut",
            "Subway", "Starbucks", "Dunkin'", "Baskin Robbins",
            
            # Beverages (РќР°РїРёС‚РєРё)
            "Coca-Cola", "Pepsi", "Sprite", "Fanta", "7UP", "Dr Pepper",
            "Red Bull", "Monster", "Rockstar", "Nescafe", "Jacobs",
            "Lipton", "Nestea", "Gatorade", "Powerade",
            
            # Clothing & Sport (РћРґРµР¶РґР° Рё СЃРїРѕСЂС‚)
            "Nike", "Adidas", "Puma", "Reebok", "New Balance", "Under Armour",
            "Zara", "H&M", "Uniqlo", "Gap", "Levi's", "Gucci", "Louis Vuitton",
            "Chanel", "Prada", "Hermes", "Dior", "Versace",
            
            # Marketplaces & E-commerce (РњР°СЂРєРµС‚РїР»РµР№СЃС‹)
            "Wildberries", "Ozon", "Yandex Market", "AliExpress", "Amazon",
            "eBay", "Lamoda", "Svyaznoy", "Eldorado", "M.Video", "Citilink",
            "DNS", "Holodilnik",
            
            # Energy & Gas (Р­РЅРµСЂРіРµС‚РёРєР° Рё РіР°Р·)
            "Gazprom", "Р“Р°Р·РїСЂРѕРј", "Lukoil", "Р›СѓРєРѕР№Р»", "Rosneft", "Р РѕСЃРЅРµС„С‚СЊ",
            "Novatek", "РќРћР’РђРўР­Рљ", "Surgutneftegas", "РЎСѓСЂРіСѓС‚РЅРµС„С‚РµРіР°Р·",
            
            # Airlines (РђРІРёР°РєРѕРјРїР°РЅРёРё)
            "Aeroflot", "РђСЌСЂРѕС„Р»РѕС‚", "S7 Airlines", "S7", "Utair", "Р®С‚СЌР№СЂ",
            "Ural Airlines", "РЈСЂР°Р»СЊСЃРєРёРµ РђРІРёР°Р»РёРЅРёРё", "Pobeda", "РџРѕР±РµРґР°",
            "Rossiya", "Р РѕСЃСЃРёСЏ",
            
            # Gaming (РРіСЂС‹)
            "PlayStation", "Xbox", "Nintendo", "Steam", "Epic Games",
            "Origin", "Uplay", "GOG", "Twitch", "Discord",
            
            # Education (РћР±СЂР°Р·РѕРІР°РЅРёРµ)
            "Skillbox", "GeekBrains", "РЇРЅРґРµРєСЃ РџСЂР°РєС‚РёРєСѓРј", "Netology",
            "SkillFactory", "Stepik", "Coursera", "Udemy", "edX",
            
            # Other Russian brands
            "Yandex", "РЇРЅРґРµРєСЃ", "VK", "Р’РљРѕРЅС‚Р°РєС‚Рµ", "Mail.ru", "Odnoklassniki",
            "Avito", "Youla", "Drom", "Auto.ru", "Kolesa",
            "Magnit", "РњР°РіРЅРёС‚", "Pyaterochka", "РџСЏС‚С‘СЂРѕС‡РєР°", "Perekrestok",
            "Lenta", "Р›РµРЅС‚Р°", "Auchan", "РђС€Р°РЅ", "Metro", "РњРµС‚СЂРѕ",
        ]
        
        # Add custom brands from config
        config_brands = settings.get_default_brands()
        if config_brands:
            default_brands.extend(config_brands)
        
        # Add user-provided custom brands
        if custom_brands:
            default_brands.extend(custom_brands)
        
        # Remove duplicates while preserving order
        self.brands = list(dict.fromkeys(default_brands))
        self.brand_name_map = {brand.lower(): brand for brand in self.brands}
        for canonical, aliases in self.brand_aliases.items():
            self.brand_name_map[canonical.lower()] = canonical
            for alias in aliases:
                self.brand_name_map[alias.lower()] = canonical

        self.brand_clip_prompts: List[str] = []
        self.clip_prompt_to_brand: Dict[str, str] = {}
        for brand in self.brands:
            prompt = f"logo of {brand}"
            self.brand_clip_prompts.append(prompt)
            self.clip_prompt_to_brand[prompt] = brand
        
        # Zero-shot prompts for detecting any brand/logo (not in our list)
        # These are used as FALLBACK only - specific brands are preferred
        self.zero_shot_prompts = [
            "company logo",
            "brand name", 
            "trademark",
            "corporate logo",
            "product logo",
            "brand logo",
            "С‚РѕСЂРіРѕРІР°СЏ РјР°СЂРєР°",
            "Р»РѕРіРѕС‚РёРї РєРѕРјРїР°РЅРёРё",
            "С„РёСЂРјРµРЅРЅС‹Р№ Р·РЅР°Рє",
            "СЂРµРєР»Р°РјРЅС‹Р№ Р±Р°РЅРЅРµСЂ",
            "advertising banner",
            "sponsor logo",
        ]

        self.generic_labels: Set[str] = {
            "brand",
            "бренд",
            "company logo",
            "логотип компании",
            "sponsor logo",
            "логотип спонсора",
            "brand logo",
            "corporate logo",
            "trademark",
            "brand name",
            "product logo",
            "advertising banner",
            "рекламный баннер",
            "торговая марка",
            "фирменный знак",
        }
        # Initialize sub-analyzers
        self.audio_analyzer = AudioAnalyzer(model_size=settings.WHISPER_MODEL)
        self.disclosure_detector = DisclosureDetector(use_llm=use_llm)
        self.brand_ocr = BrandOCR(known_brands=self.brands) if settings.ENABLE_BRAND_OCR else None
        self.cloud_brand_detector = CloudBrandDetector()

        # Detection settings from config
        self.detection_threshold = settings.BRAND_DETECTION_THRESHOLD
        self.max_frames = settings.BRAND_MAX_FRAMES
        self.frame_interval = settings.BRAND_FRAME_INTERVAL

        # Output directories
        self.raw_dir = settings.upload_path
        self.processed_dir = settings.data_path / "processed"
        self.raw_dir.mkdir(exist_ok=True, parents=True)
        self.processed_dir.mkdir(exist_ok=True, parents=True)

        logger.info(f"Video Processor initialized with {len(self.brands)} brands")

    def download_video(
        self,
        url: str,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None,
    ) -> Optional[Path]:
        """
        Download video from URL using yt-dlp with optimized settings

        Args:
            url: Video URL
            progress_callback: Async callback function(progress: int, message: str) for progress updates

        Returns:
            Path to downloaded video or None
        """
        def emit_progress(progress: int, message: str) -> None:
            if not progress_callback:
                return
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(progress_callback(progress, message))
            except RuntimeError:
                asyncio.run(progress_callback(progress, message))

        try:
            video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
            video_path = self.raw_dir / f"{video_id}.mp4"

            logger.info(f"Downloading video from: {url}")
            start_time = time.time()

            # Report initial progress (downloading started)
            emit_progress(5, "Downloading video")

            cmd = [
                sys.executable,
                "-m",
                "yt_dlp",
                "-o", str(video_path),
                "--retries", str(settings.DOWNLOAD_RETRIES),
                "--retry-sleep", "2",
                "--extractor-retries", "3",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--concurrent-fragments", str(settings.DOWNLOAD_CONCURRENT_FRAGMENTS),
                "--fragment-retries", str(settings.DOWNLOAD_FRAGMENT_RETRIES),
                "--socket-timeout", str(settings.DOWNLOAD_SOCKET_TIMEOUT),
                "--no-playlist",
                "--geo-bypass",
                "--no-check-certificates",
                "--no-warnings",
                "--newline",  # Print progress on new lines for easier parsing
            ]

            # Use aria2c as external downloader if enabled
            if settings.USE_ARIA2C:
                cmd += [
                    "--external-downloader", "aria2c",
                    "--external-downloader-args",
                    f"aria2c: -x {settings.DOWNLOAD_CONCURRENT_FRAGMENTS} -s {settings.DOWNLOAD_CONCURRENT_FRAGMENTS} -k 1M",
                ]

            # Add cookies for Telegram
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]

            if "youtu.be" in url or "youtube.com" in url:
                cmd += [
                    "--extractor-args",
                    "youtube:player_client=android,web",
                    "--user-agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                ]
            cmd.append(url)

            # Run subprocess and capture output for progress parsing
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Parse progress from yt-dlp output
            download_progress = 0
            output_lines = []

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    output_lines.append(line)
                    # Parse download percentage from yt-dlp output
                    # Matches patterns like "[download]  45.3% of  10.50MiB"
                    match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
                    if match:
                        current_progress = float(match.group(1))
                        # Map download progress (0-100%) to task progress (5-15%)
                        mapped_progress = 5 + int((current_progress / 100) * 10)
                        if mapped_progress > download_progress:
                            download_progress = mapped_progress
                            emit_progress(download_progress, "Downloading video")

            result = subprocess.CompletedProcess(
                cmd,
                process.returncode,
                ''.join(output_lines),
                ''
            )

            if result.returncode != 0:
                output_tail = "\n".join("".join(output_lines).strip().splitlines()[-8:])
                raise RuntimeError(f"yt-dlp failed with code {result.returncode}: {output_tail}")

            if not video_path.exists():
                raise RuntimeError("yt-dlp completed but video file was not created")

            # Report download complete
            emit_progress(15, "Processing video file")

            download_time = time.time() - start_time
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            speed_mbps = round(file_size_mb / download_time if download_time > 0 else 0, 2)
            logger.info(
                f"Video downloaded successfully - path={video_path}, time={round(download_time, 2)}s, "
                f"size={round(file_size_mb, 2)}MB, speed={speed_mbps}MB/s"
            )
            return video_path

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Video download timeout after {settings.DOWNLOAD_TIMEOUT}s")
        except Exception as e:
            logger.error(f"Video download failed: {str(e)}")
            raise

    async def get_video_metadata(self, video_path: Path) -> Dict[str, any]:
        """Extract video metadata (async wrapper for sync opencv calls)"""
        try:
            def _extract_metadata():
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
            
            # Р’С‹РїРѕР»РЅСЏРµРј РІ executor РґР»СЏ РЅРµР±Р»РѕРєРёСЂСѓСЋС‰РµРіРѕ I/O
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _extract_metadata)
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {}

    def detect_logos(self, video_path: Path) -> Dict[str, any]:
        """
        Detect brand logos in video frames using hybrid approach:
        1. CLIP with known brand list
        2. Zero-shot CLIP for unknown brands/logos
        3. OCR for text-based brand detection (optional)

        Args:
            video_path: Path to video file

        Returns:
            Detection results with scores and detected brands
        """
        try:
            logger.info("Starting logo detection")
            cap = cv2.VideoCapture(str(video_path))

            frames: List[Image.Image] = []
            timestamps: List[float] = []

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0

            # Requirement: long videos should be sampled at ~1 fps.
            if duration < 120:
                sample_interval = max(1, int(fps * 0.5))
                max_frames = min(self.max_frames, 180)
            elif duration < 600:
                sample_interval = max(1, int(fps * 1.0))
                max_frames = min(self.max_frames, 120)
            else:
                sample_interval = max(1, int(fps * 1.0))
                max_frames = min(self.max_frames, 300)

            sample_step_seconds = sample_interval / fps if fps > 0 else 1.0
            logger.info(
                f"Adaptive sampling: duration={duration:.1f}s, interval={sample_interval} frames, max_frames={max_frames}"
            )

            frame_count = 0
            while cap.isOpened() and len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % sample_interval == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(frame_rgb))
                    timestamps.append(frame_count / fps if fps > 0 else 0.0)

                frame_count += 1

            cap.release()

            if not frames:
                logger.warning("No frames extracted for logo detection")
                return {"score": 0.0, "detected_brands": [], "frame_count": 0}

            raw_detections: List[Dict[str, Any]] = []
            all_scores: List[float] = []

            logger.info(f"Running CLIP detection with {len(self.brand_clip_prompts)} brand prompts")
            known_brands_result = self._detect_with_clip(
                frames,
                self.brand_clip_prompts,
                timestamps,
                "known",
                prompt_to_brand=self.clip_prompt_to_brand,
            )
            raw_detections.extend(known_brands_result.get("detected_brands", []))
            all_scores.extend(known_brands_result.get("max_scores", []))

            if self.cloud_brand_detector.is_enabled():
                logger.info("Running cloud provider brand detection")
                cloud_result = self.cloud_brand_detector.detect_brands(frames, timestamps, max_frames=20)
                raw_detections.extend(cloud_result.get("detected_brands", []))

            if settings.ENABLE_BRAND_OCR and self.brand_ocr:
                logger.info("Running OCR-based brand detection")
                ocr_result = self.brand_ocr.extract_brands_from_frames(frames, timestamps)
                raw_detections.extend(ocr_result.get("detected_brands", []))

            if settings.ENABLE_ZERO_SHOT and not raw_detections:
                logger.info("Running zero-shot fallback because no brand detections were found")
                zero_shot_result = self._detect_with_clip(
                    frames,
                    self.zero_shot_prompts,
                    timestamps,
                    "zero_shot",
                )
                raw_detections.extend(zero_shot_result.get("detected_brands", []))
                all_scores.extend(zero_shot_result.get("max_scores", []))

            aggregated = self._aggregate_brand_detections(raw_detections, sample_step_seconds=sample_step_seconds)
            if not aggregated and raw_detections:
                fallback_conf = max(float(det.get("confidence", 0.0)) for det in raw_detections)
                aggregated = [{
                    "name": f"Unknown brand (confidence: {fallback_conf:.0%})",
                    "confidence": fallback_conf,
                    "timestamps": sorted({
                        float(ts)
                        for det in raw_detections
                        for ts in det.get("timestamps", [det.get("timestamp", 0.0)])
                    }),
                    "frame_count": sum(int(det.get("frame_count", 1)) for det in raw_detections),
                    "detections": sum(int(det.get("frame_count", 1)) for det in raw_detections),
                    "total_exposure_seconds": 0.0,
                    "source": "fallback",
                    "is_unknown": True,
                }]

            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
            visual_score = min(1.0, avg_score * 1.3)
            if aggregated:
                visual_score = min(1.0, max(visual_score, max(det["confidence"] for det in aggregated)))

            logger.info(
                "Logo detection complete. Score: %.2f, Brands found: %s",
                visual_score,
                len(aggregated),
            )

            return {
                "score": visual_score,
                "detected_brands": aggregated,
                "frame_count": len(frames),
                "detections": aggregated,
                "max_scores": all_scores,
            }
        except Exception as e:
            logger.error(f"Logo detection failed: {str(e)}")
            return {"score": 0.0, "detected_brands": [], "frame_count": 0}

    def _is_generic_label(self, brand_name: str) -> bool:
        normalized = " ".join((brand_name or "").strip().lower().split())
        return not normalized or normalized in self.generic_labels

    def _normalize_brand_name(self, brand_name: str) -> Optional[str]:
        if not brand_name:
            return None
        cleaned = " ".join(str(brand_name).strip().split())
        if self._is_generic_label(cleaned):
            return None

        by_alias = self._resolve_brand_alias(cleaned)
        lowered = by_alias.lower()
        if lowered in self.brand_name_map:
            return self.brand_name_map[lowered]

        return by_alias

    def _calc_exposure_seconds(self, timestamps: List[float], sample_step_seconds: float) -> float:
        if not timestamps:
            return 0.0
        unique_sorted = sorted(set(timestamps))
        if len(unique_sorted) == 1:
            return max(sample_step_seconds, 0.2)

        exposure = 0.0
        cluster_start = unique_sorted[0]
        prev = unique_sorted[0]
        gap_threshold = max(sample_step_seconds * 1.5, 1.0)

        for ts in unique_sorted[1:]:
            if ts - prev <= gap_threshold:
                prev = ts
                continue
            exposure += max(sample_step_seconds, prev - cluster_start + sample_step_seconds)
            cluster_start = ts
            prev = ts

        exposure += max(sample_step_seconds, prev - cluster_start + sample_step_seconds)
        return round(exposure, 2)

    def _aggregate_brand_detections(
        self,
        raw_detections: List[Dict[str, Any]],
        *,
        sample_step_seconds: float,
    ) -> List[Dict[str, Any]]:
        aggregated: Dict[str, Dict[str, Any]] = {}
        unknown_candidates: List[float] = []

        for det in raw_detections:
            name = str(det.get("name", "")).strip()
            confidence = float(det.get("confidence", 0.0))
            timestamps = det.get("timestamps") or [det.get("timestamp", 0.0)]
            timestamps = [float(ts) for ts in timestamps]
            source = str(det.get("source", "known"))
            frame_count = int(det.get("frame_count", max(1, len(timestamps))))

            normalized = self._normalize_brand_name(name)
            if not normalized:
                unknown_candidates.append(confidence)
                continue

            if normalized not in aggregated:
                aggregated[normalized] = {
                    "name": normalized,
                    "confidence": confidence,
                    "timestamps": timestamps[:],
                    "source": source,
                    "frame_count": frame_count,
                    "detections": frame_count,
                    "is_unknown": False,
                }
            else:
                current = aggregated[normalized]
                current["confidence"] = max(float(current["confidence"]), confidence)
                current["timestamps"].extend(timestamps)
                current["frame_count"] = int(current["frame_count"]) + frame_count
                current["detections"] = int(current["detections"]) + frame_count
                current["source"] = f"{current['source']},{source}" if source not in str(current["source"]) else current["source"]

        final_list: List[Dict[str, Any]] = []
        min_confidence = float(settings.BRAND_MIN_CONFIDENCE_DISPLAY)
        for item in aggregated.values():
            item["timestamps"] = sorted(set(float(ts) for ts in item["timestamps"]))
            item["total_exposure_seconds"] = self._calc_exposure_seconds(
                item["timestamps"],
                sample_step_seconds=max(sample_step_seconds, 0.2),
            )
            if float(item["confidence"]) >= min_confidence:
                final_list.append(item)

        if not final_list and unknown_candidates:
            conf = max(unknown_candidates)
            final_list.append(
                {
                    "name": f"Unknown brand (confidence: {conf:.0%})",
                    "confidence": conf,
                    "timestamps": [],
                    "source": "fallback",
                    "frame_count": 1,
                    "detections": 1,
                    "total_exposure_seconds": 0.0,
                    "is_unknown": True,
                }
            )

        final_list.sort(key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
        return final_list

    def _resolve_brand_alias(self, brand_name: str) -> str:
        """
        Resolve brand alias to canonical brand name.
        
        Args:
            brand_name: Detected brand name (may be alias)
            
        Returns:
            Canonical brand name or original if no alias found
        """
        if not settings.ENABLE_BRAND_ALIASES or not self.alias_to_brand:
            return brand_name
        
        # Check if the brand name matches any alias
        brand_lower = brand_name.lower()
        return self.alias_to_brand.get(brand_lower, brand_name)

    def _detect_with_clip(
        self,
        frames: list,
        text_prompts: list,
        timestamps: list,
        detection_type: str = "known",
        prompt_to_brand: Optional[Dict[str, str]] = None,
    ) -> Dict[str, any]:
        """
        Run CLIP detection with custom text prompts.

        Args:
            frames: List of PIL Image frames
            text_prompts: List of text prompts (brand names or zero-shot prompts)
            timestamps: List of timestamps for each frame
            detection_type: Type of detection ("known" or "zero_shot")

        Returns:
            Detection results
        """
        if not frames or not text_prompts:
            return {"score": 0.0, "detected_brands": [], "max_scores": []}

        try:
            # Run CLIP inference in batches to avoid OOM
            batch_size = 16
            all_frame_probs = []

            for i in range(0, len(frames), batch_size):
                batch_frames = frames[i:i + batch_size]
                inputs = self.clip_processor(
                    text=text_prompts,
                    images=batch_frames,
                    return_tensors="pt",
                    padding=True
                )

                with torch.no_grad():
                    outputs = self.clip_model(**inputs)
                    probs = outputs.logits_per_image.softmax(dim=1)
                    all_frame_probs.append(probs)

            # Concatenate all batches
            if all_frame_probs:
                all_probs = torch.cat(all_frame_probs, dim=0)
            else:
                return {"score": 0.0, "detected_brands": [], "max_scores": []}

            # Analyze results
            detected_brands = []
            max_scores = []

            for idx, frame_probs in enumerate(all_probs):
                max_prob, max_idx = frame_probs.max(dim=0)
                max_scores.append(max_prob.item())

                if max_prob.item() > self.detection_threshold:
                    selected_prompt = text_prompts[max_idx.item()]
                    brand = prompt_to_brand.get(selected_prompt, selected_prompt) if prompt_to_brand else selected_prompt
                    detected_brands.append({
                        "name": brand,
                        "confidence": max_prob.item(),
                        "timestamp": timestamps[idx],
                        "source": detection_type,
                    })

            # Group by brand/prompts
            brand_detections = {}
            for det in detected_brands:
                brand = det["name"]
                
                if brand not in brand_detections:
                    brand_detections[brand] = {
                        "name": brand,
                        "confidence": det["confidence"],
                        "timestamps": [det["timestamp"]],
                        "source": detection_type,
                        "frame_count": 1,
                    }
                else:
                    brand_detections[brand]["timestamps"].append(det["timestamp"])
                    brand_detections[brand]["confidence"] = max(
                        brand_detections[brand]["confidence"],
                        det["confidence"]
                    )
                    brand_detections[brand]["frame_count"] += 1

            return {
                "score": sum(max_scores) / len(max_scores) if max_scores else 0.0,
                "detected_brands": list(brand_detections.values()),
                "max_scores": max_scores,
            }

        except Exception as e:
            logger.error(f"CLIP detection failed: {str(e)}")
            return {"score": 0.0, "detected_brands": [], "max_scores": []}

    def detect_brands_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect brands in text content using the configured brand list.
        
        Args:
            text: Text to analyze (e.g. post description, caption)
            
        Returns:
            List of detected brands with confidence scores
        """
        if not text:
            return []

        detected = []
        text_lower = text.lower()
        
        # Check for each brand in the text
        for brand in self.brands:
            brand_lower = brand.lower()
            # Simple keyword matching with boundaries to avoid partial word matches
            # e.g. avoid matching "Apple" in "Pineapple" if possible, but strict regex might be too slow for 500 brands
            # For now, simple inclusion with basic boundary check is faster and often sufficient
            
            # Check canonical name
            if brand_lower in text_lower:
                # Basic boundary check
                pattern = r'(?<!\w)' + re.escape(brand_lower) + r'(?!\w)'
                if re.search(pattern, text_lower):
                    detected.append({
                        "name": brand,
                        "confidence": 1.0, # High confidence for text match
                        "source": "text_content",
                        "occurrences": len(re.findall(pattern, text_lower))
                    })
                    continue

            # Check aliases
            if settings.ENABLE_BRAND_ALIASES and self.brand_aliases:
                for alias in self.brand_aliases.get(brand, []):
                    alias_lower = alias.lower()
                    pattern = r'(?<!\w)' + re.escape(alias_lower) + r'(?!\w)'
                    if re.search(pattern, text_lower):
                        detected.append({
                            "name": brand, # Return canonical name
                            "confidence": 1.0,
                            "source": "text_content (alias)",
                            "occurrences": len(re.findall(pattern, text_lower))
                        })
                        break # Found the brand via alias, move to next brand

        return detected

    async def process(
        self,
        file=None,
        url: str = None,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None,
    ) -> Dict[str, any]:
        """
        Complete video processing pipeline

        Args:
            file: Uploaded file
            url: Video URL
            progress_callback: Async callback function(progress: int, message: str) for progress updates

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
                video_path = self.download_video(url, progress_callback=progress_callback)
                if not video_path:
                    raise Exception(f"Video download returned no file for URL: {url}")
                source = "url"
                source_url = url

            else:
                raise Exception("No video file or URL provided")

            logger.info(f"Processing video: {video_path}")

            # Extract metadata (С‚РµРїРµСЂСЊ СЃ await)
            metadata = await self.get_video_metadata(video_path)

            # Run analysis - СЃРёРЅС…СЂРѕРЅРЅС‹Рµ РјРµС‚РѕРґС‹ РІС‹РїРѕР»РЅСЏРµРј РІ executor
            logger.info("Running visual analysis")
            loop = asyncio.get_event_loop()
            visual_result = await loop.run_in_executor(
                None, self.detect_logos, video_path
            )

            logger.info("Running audio analysis")
            audio_result = await loop.run_in_executor(
                None, self.audio_analyzer.analyze, video_path
            )

            logger.info("Running disclosure detection")
            transcript = audio_result.get("transcript", "")
            disclosure_result = await loop.run_in_executor(
                None, 
                lambda: self.disclosure_detector.analyze(text=transcript, description="")
            )

            # Calculate final scores
            visual_score = visual_result["score"]
            audio_score = audio_result["score"]
            text_score = audio_score  # Same as audio for now
            disclosure_score = disclosure_result["score"]
            disclosure_markers = disclosure_result.get("markers", [])
            
            # Combine detected brands from visual, OCR, and context discovery
            all_detected_brands = visual_result.get("detected_brands", [])
            
            # Add contextually discovered brands (from text near erid/promo)
            discovered_brands = disclosure_result.get("discovered_brands", [])
            for db in discovered_brands:
                # Only add if not already detected visually (avoid duplicates)
                if not any(v.get("name", "").lower() == db["name"].lower() for v in all_detected_brands):
                    all_detected_brands.append({
                        "name": db["name"],
                        "confidence": db["confidence"],
                        "source": db["source"],
                        "is_discovered": True
                    })

            # Weighted final score
            confidence_score = (
                visual_score * 0.3 +
                audio_score * 0.3 +
                text_score * 0.2 +
                disclosure_score * 0.2
            )

            has_disclosure = disclosure_result.get("has_disclosure", False) or bool(disclosure_markers)
            has_advertising = confidence_score > 0.4 or has_disclosure

            classification = classify_advertising(
                has_advertising=has_advertising,
                disclosure_markers=disclosure_markers,
                detected_brands=all_detected_brands,
                detected_keywords=audio_result.get("keywords", []),
            )

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
                "detected_brands": all_detected_brands,
                "detected_keywords": audio_result["keywords"],
                "transcript": audio_result["transcript"],
                "disclosure_text": disclosure_markers,
                "erids": disclosure_result.get("erids", []),
                "promo_codes": disclosure_result.get("promo_codes", []),
                "ad_classification": classification["classification"],
                "ad_reason": classification["reason"],

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

