"""
Brand OCR service for detecting brand names from video frames.
Uses EasyOCR for text extraction and NER for company name detection.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class BrandOCR:
    """
    OCR-based brand detection service.
    Extracts text from video frames and identifies potential brand names using a known brand database.
    """

    def __init__(self, known_brands: List[str] = None, languages: List[str] = None):
        """
        Initialize OCR service.
        
        Args:
            known_brands: List of known brand names to search for
            languages: List of languages for OCR (default: ['ru', 'en'])
        """
        self.languages = languages or ['ru', 'en']
        self.known_brands = known_brands or []
        # Create a normalized set for fast lookup O(1)
        self.normalized_brands = {self._normalize(b): b for b in self.known_brands}
        self._reader = None

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison: lowercase, remove special chars."""
        import re
        return re.sub(r'[^a-z0-9а-я]', '', text.lower())

    @property
    def reader(self):
        """Lazy load OCR reader to avoid import errors."""
        if self._reader is None:
            try:
                import easyocr
                self._reader = easyocr.Reader(
                    self.languages,
                    gpu=False,  # Set to True if CUDA available
                    verbose=False
                )
                logger.info("EasyOCR initialized successfully")
            except ImportError:
                logger.warning("EasyOCR not installed. Install with: pip install easyocr")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                return None
        return self._reader

    def extract_text_from_frame(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract text from a single frame using EasyOCR.
        """
        if not self.reader:
            return []
        
        try:
            img_array = np.array(image)
            results = self.reader.readtext(
                img_array,
                min_size=10,
                text_threshold=0.4, # Lower threshold to catch stylized fonts
                link_threshold=0.4,
            )
            
            extracted = []
            for bbox, text, confidence in results:
                if len(text.strip()) > 1:
                    extracted.append({
                        "text": text.strip(),
                        "confidence": confidence,
                        "bbox": bbox,
                    })
            return extracted
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return []

    def match_brand(self, text: str) -> Tuple[bool, str, float]:
        """
        Check if extracted text matches a known brand.
        Returns: (is_match, brand_name, confidence_modifier)
        """
        if not text:
            return False, "", 0.0

        normalized_text = self._normalize(text)
        if not normalized_text:
            return False, "", 0.0

        # 1. Exact match (normalized)
        if normalized_text in self.normalized_brands:
            return True, self.normalized_brands[normalized_text], 1.0

        # 2. Substring match (if text is short enough to not be a full sentence)
        # e.g. "Bank Tinkoff" -> matches "Tinkoff"
        if len(text.split()) < 5:
            for n_brand, original_brand in self.normalized_brands.items():
                if len(n_brand) < 3: continue # Skip too short brands for substring
                if n_brand in normalized_text:
                    return True, original_brand, 0.9

        return False, "", 0.0

    def extract_brands_from_frames(
        self,
        frames: List[Image.Image],
        frame_timestamps: List[float],
    ) -> Dict[str, Any]:
        """
        Extract potential brand names from multiple frames.
        """
        if not frames or not self.reader:
            return {"score": 0.0, "detected_brands": [], "text_regions": []}
        
        detected_brands_map = {}
        
        for idx, (frame, timestamp) in enumerate(zip(frames, frame_timestamps)):
            text_regions = self.extract_text_from_frame(frame)
            
            for region in text_regions:
                text = region["text"]
                ocr_conf = region["confidence"]
                
                is_match, brand_name, match_conf = self.match_brand(text)
                
                if is_match:
                    final_conf = ocr_conf * match_conf
                    
                    if brand_name not in detected_brands_map:
                        detected_brands_map[brand_name] = {
                            "name": brand_name,
                            "confidence": final_conf,
                            "timestamps": [timestamp],
                            "source": "ocr",
                            "frame_count": 1,
                            "occurrences": 1
                        }
                    else:
                        entry = detected_brands_map[brand_name]
                        entry["timestamps"].append(timestamp)
                        entry["confidence"] = max(entry["confidence"], final_conf)
                        entry["frame_count"] += 1
                        entry["occurrences"] += 1

        final_brands = list(detected_brands_map.values())
        return {
            "score": min(1.0, len(final_brands) * 0.3), # High confidence if text found
            "detected_brands": final_brands,
        }

    # Legacy method for backward compatibility if needed, but we mostly use extract_brands_from_frames
    def analyze(self, video_path: Path) -> Dict[str, Any]:
        return {}
