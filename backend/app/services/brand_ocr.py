"""
Brand OCR service for detecting brand names from video frames.

Uses Tesseract 5 (LSTM engine, ``--oem 3 --psm 6``) for text extraction with an
OpenCV preprocessing pipeline (CLAHE contrast equalisation + Non-Local Means
denoising + Otsu binarisation) and fuzzy brand matching by Levenshtein ratio
(> 0.85), as described in the thesis (sec. 3.2 "Текстовый канал / OCR").

If Tesseract is not available on the host, the service degrades gracefully to
EasyOCR (if installed) and finally to returning no detections.
"""
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Fuzzy match threshold per thesis (Levenshtein ratio > 0.85).
FUZZY_MATCH_THRESHOLD = 0.85

# Generic on-screen text that is NOT a brand (UI chrome, social CTAs, filler).
# Used to keep arbitrary-brand discovery from surfacing junk tokens.
OCR_DISCOVERY_STOPWORDS = {
    # social / UI
    "subscribe", "подписаться", "подписка", "подпишись", "like", "лайк",
    "канал", "видео", "смотреть", "далее", "продолжение", "плейлист",
    "комментарии", "поделиться", "share", "follow", "watch", "video",
    "channel", "live", "новости", "выпуск", "сезон", "серия", "эпизод",
    # commerce / disclosure (not a brand by themselves)
    "реклама", "promo", "промокод", "скидка", "sale", "купить", "купи", "заказать",
    "закажи", "успей", "успейте", "жми", "магазин", "доставка", "цена", "цены",
    "рублей", "руб", "артикул", "набор", "подарок", "official", "официальный",
    "новинка", "акция", "только", "сейчас", "хит", "топ",
    # generic words / connectors
    "привет", "спасибо", "сегодня", "день", "время", "money", "the", "and",
    "you", "your", "for", "with", "это", "как", "что", "так", "все", "наш",
}
# Tesseract configuration: LSTM-only engine (oem 3), uniform block of text (psm 6).
TESSERACT_CONFIG = "--oem 3 --psm 6"
TESSERACT_LANG = "rus+eng"


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
        self._engine = None  # "tesseract" | "easyocr" | "none"
        self._reader = None  # EasyOCR fallback reader

        # Arbitrary-brand discovery thresholds (read from settings with defaults).
        try:
            from app.core.config import settings
            self.discovery_enabled = bool(getattr(settings, "OCR_DISCOVERY_ENABLED", True))
            self.discovery_min_frames = int(getattr(settings, "OCR_DISCOVERY_MIN_FRAMES", 2))
            self.discovery_min_conf = float(getattr(settings, "OCR_DISCOVERY_MIN_OCR_CONF", 0.45))
            self.discovery_strong_conf = float(getattr(settings, "OCR_DISCOVERY_STRONG_CONF", 0.85))
        except Exception:
            self.discovery_enabled = True
            self.discovery_min_frames = 2
            self.discovery_min_conf = 0.45
            self.discovery_strong_conf = 0.85

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison: lowercase, remove special chars."""
        import re
        return re.sub(r'[^a-z0-9а-я]', '', text.lower())

    @staticmethod
    def _levenshtein_ratio(a: str, b: str) -> float:
        """Levenshtein similarity ratio in [0, 1].

        Prefers the ``python-Levenshtein`` package; falls back to the stdlib
        ``difflib.SequenceMatcher`` when it is not installed.
        """
        if not a or not b:
            return 0.0
        try:
            import Levenshtein  # type: ignore

            return Levenshtein.ratio(a, b)
        except ImportError:
            from difflib import SequenceMatcher

            return SequenceMatcher(None, a, b).ratio()

    @property
    def engine(self) -> str:
        """Resolve and cache the active OCR engine."""
        if self._engine is None:
            self._engine = self._init_engine()
        return self._engine

    def _init_engine(self) -> str:
        # Prefer Tesseract 5 (thesis requirement).
        try:
            import pytesseract  # noqa: F401

            # Probe the binary; raises if tesseract is not on PATH.
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR engine initialized")
            return "tesseract"
        except Exception as exc:
            logger.warning("Tesseract unavailable (%s); trying EasyOCR fallback", exc)

        try:
            import easyocr

            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
            logger.info("EasyOCR fallback initialized")
            return "easyocr"
        except Exception as exc:
            logger.warning("No OCR engine available: %s", exc)
            return "none"

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        """OpenCV preprocessing: grayscale -> CLAHE -> NLM denoise -> Otsu.

        Improves OCR on stylised overlays and low-contrast frames.
        """
        img = np.array(image)
        if img.ndim == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img

        # Contrast Limited Adaptive Histogram Equalisation.
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(gray)

        # Non-Local Means denoising.
        denoised = cv2.fastNlMeansDenoising(equalized, h=10)

        # Otsu binarisation.
        _, binary = cv2.threshold(
            denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary

    def extract_text_from_frame(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract text from a single frame.
        """
        engine = self.engine
        if engine == "none":
            return []

        try:
            if engine == "tesseract":
                return self._extract_tesseract(image)
            return self._extract_easyocr(image)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return []

    def _extract_tesseract(self, image: Image.Image) -> List[Dict[str, Any]]:
        import pytesseract

        processed = self._preprocess(image)
        data = pytesseract.image_to_data(
            processed,
            lang=TESSERACT_LANG,
            config=TESSERACT_CONFIG,
            output_type=pytesseract.Output.DICT,
        )

        extracted: List[Dict[str, Any]] = []
        for text, conf in zip(data.get("text", []), data.get("conf", [])):
            text = (text or "").strip()
            try:
                confidence = float(conf) / 100.0
            except (TypeError, ValueError):
                confidence = 0.0
            if len(text) > 1 and confidence > 0:
                extracted.append({"text": text, "confidence": confidence, "bbox": None})
        return extracted

    def _extract_easyocr(self, image: Image.Image) -> List[Dict[str, Any]]:
        img_array = np.array(image)
        results = self._reader.readtext(
            img_array,
            min_size=10,
            text_threshold=0.4,
            link_threshold=0.4,
        )
        extracted: List[Dict[str, Any]] = []
        for bbox, text, confidence in results:
            if len(text.strip()) > 1:
                extracted.append(
                    {"text": text.strip(), "confidence": confidence, "bbox": bbox}
                )
        return extracted

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
        if len(text.split()) < 5:
            for n_brand, original_brand in self.normalized_brands.items():
                if len(n_brand) < 3:
                    continue  # Skip too short brands for substring
                if n_brand in normalized_text:
                    return True, original_brand, 0.9

        # 3. Fuzzy match by Levenshtein ratio (> 0.85), per thesis.
        best_brand = ""
        best_ratio = 0.0
        for n_brand, original_brand in self.normalized_brands.items():
            if len(n_brand) < 3:
                continue
            ratio = self._levenshtein_ratio(normalized_text, n_brand)
            if ratio > best_ratio:
                best_ratio = ratio
                best_brand = original_brand
        if best_ratio >= FUZZY_MATCH_THRESHOLD:
            return True, best_brand, float(best_ratio)

        return False, "", 0.0

    def _brand_candidates(self, text: str) -> List[str]:
        """Generate brand-name candidates from a single OCR text region.

        Yields the whole short region (to keep multi-word brands like
        "Cuba Buba" intact) plus individual word tokens.
        """
        cleaned = " ".join((text or "").split())
        if not cleaned:
            return []
        candidates: List[str] = []
        words = cleaned.split(" ")
        if 1 <= len(words) <= 3 and len(cleaned) <= 30:
            candidates.append(cleaned)
        for w in words:
            w = w.strip("«»\"'.,:;!?()[]—-")
            if w:
                candidates.append(w)
        # de-duplicate, preserve order
        return list(dict.fromkeys(candidates))

    def _looks_like_brand(self, candidate: str) -> bool:
        """Heuristic gate for arbitrary-brand discovery.

        Brand overlays are capitalised, alphabetic and not generic UI/commerce
        words. This keeps discovery from surfacing ordinary lowercase words,
        numbers, URLs and social CTAs.
        """
        norm = self._normalize(candidate)
        if len(norm) < 3:
            return False
        # Strip punctuation from each word so "Артикул:"/"СКИДКА!" still match the
        # stopword list. Reject if any constituent word is a generic stopword.
        parts = [re.sub(r"[^a-zа-я0-9]", "", p) for p in candidate.lower().split()]
        parts = [p for p in parts if p]
        if any(p in OCR_DISCOVERY_STOPWORDS for p in parts):
            return False
        if any(tok in candidate.lower() for tok in ("http", "www", ".com", ".ru", "@")):
            return False
        letters = sum(ch.isalpha() for ch in candidate)
        if letters < 3 or letters < len(self._normalize(candidate)) * 0.6:
            return False  # mostly digits/symbols
        # Brand overlays carry at least one capital letter (TitleCase / ALLCAPS).
        if not any(ch.isupper() for ch in candidate):
            return False
        return True

    def extract_brands_from_frames(
        self,
        frames: List[Image.Image],
        frame_timestamps: List[float],
    ) -> Dict[str, Any]:
        """
        Extract brand names from multiple frames.

        Two paths run together:
        * **Known brands** — OCR text matched against the configured brand list.
        * **Discovered brands** — arbitrary on-screen text (any brand, not in the
          list) promoted when it persists across frames or is read with very high
          confidence. This is what enables detection of brands we do not know in
          advance.
        """
        if not frames or self.engine == "none":
            return {"score": 0.0, "detected_brands": [], "text_regions": []}

        detected_brands_map: Dict[str, Any] = {}
        # norm token -> {"display", "timestamps": [...], "confs": [...]}
        candidate_map: Dict[str, Any] = {}

        for frame, timestamp in zip(frames, frame_timestamps):
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
                            "occurrences": 1,
                        }
                    else:
                        entry = detected_brands_map[brand_name]
                        entry["timestamps"].append(timestamp)
                        entry["confidence"] = max(entry["confidence"], final_conf)
                        entry["frame_count"] += 1
                        entry["occurrences"] += 1
                    continue

                # Arbitrary-brand discovery on unmatched text.
                if not self.discovery_enabled:
                    continue
                for cand in self._brand_candidates(text):
                    if not self._looks_like_brand(cand):
                        continue
                    norm = self._normalize(cand)
                    bucket = candidate_map.setdefault(
                        norm, {"display": cand, "timestamps": [], "confs": []}
                    )
                    bucket["timestamps"].append(timestamp)
                    bucket["confs"].append(ocr_conf)

        final_brands = list(detected_brands_map.values())

        # Collect qualifying discovered candidates.
        discovered: List[Dict[str, Any]] = []
        for norm, bucket in candidate_map.items():
            if norm in self.normalized_brands:
                continue  # already covered as a known brand
            uniq_ts = sorted(set(bucket["timestamps"]))
            avg_conf = sum(bucket["confs"]) / len(bucket["confs"]) if bucket["confs"] else 0.0
            max_conf = max(bucket["confs"]) if bucket["confs"] else 0.0
            persistent = len(uniq_ts) >= self.discovery_min_frames and avg_conf >= self.discovery_min_conf
            strong_single = max_conf >= self.discovery_strong_conf
            if not (persistent or strong_single):
                continue
            confidence = min(0.85, 0.5 + 0.07 * (len(uniq_ts) - 1)) if persistent else 0.5
            discovered.append(
                {
                    "name": bucket["display"],
                    "confidence": round(confidence, 4),
                    "timestamps": uniq_ts,
                    "source": "ocr_discovered",
                    "frame_count": len(uniq_ts),
                    "occurrences": len(bucket["timestamps"]),
                    "is_discovered": True,
                    "_words": set(bucket["display"].lower().split()),
                }
            )

        # De-duplicate: drop a candidate whose words are fully contained in a
        # longer multi-word discovered brand (keep "Cuba Buba", drop "Cuba"/"Buba").
        discovered.sort(key=lambda b: (-len(b["_words"]), -len(b["name"])))
        kept: List[Dict[str, Any]] = []
        for cand in discovered:
            if any(cand["_words"] < other["_words"] for other in kept):
                continue
            kept.append(cand)
        for cand in kept:
            cand.pop("_words", None)
            final_brands.append(cand)

        return {
            "score": min(1.0, len(final_brands) * 0.3),
            "detected_brands": final_brands,
        }

    # Legacy method for backward compatibility if needed.
    def analyze(self, video_path: Path) -> Dict[str, Any]:
        return {}
