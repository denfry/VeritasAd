from pathlib import Path
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class DisclosureDetector:
    """Detect advertising disclosure markers in text"""

    def __init__(self, use_llm: bool = False):
        """
        Initialize disclosure detector

        Args:
            use_llm: Whether to use LLM for advanced detection (requires GPU)
        """
        self.use_llm = use_llm
        self.llm_model = None

        if use_llm:
            try:
                from models.llm.inference import DisclosureLLM
                logger.info("Loading LLM for disclosure detection")
                self.llm_model = DisclosureLLM()
                logger.info("LLM loaded successfully")
            except Exception as e:
                logger.warning(f"LLM loading failed, using rule-based detection: {str(e)}")
                self.use_llm = False

        # Disclosure patterns (Russian)
        self.disclosure_patterns = [
            r"#@5:;0<0",
            r"#@5:",
            r"#ad",
            r"@5:;0<[0K]",
            r"A?>=A>@(?:8@C5BAO|8@>20=[0K]?|A:89 :>=B5=B)",
            r"@5:;0<=[0K][9O5]\s+(?:8=B53@0F8O|?>AB|2845>|:>=B5=B)",
            r"?0@B=5@(?:A:89|A:0O)?\s+(?:<0B5@80;|?>AB|2845>)",
            r":><<5@G5A:[0K>5][9O5]?\s+(?:A>B@C4=8G5AB2>|8=B53@0F8O)",
            r"?@8\s+?>445@6:5",
            r"?@><>(?::F8O|-?<0B5@80;)",
            r">?;0G5=(?:=K9|=0O)\s+(?:@5:;0<0|8=B53@0F8O|@07<5I5=85)",
        ]

        # Compile patterns
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.disclosure_patterns]

    def detect_rule_based(self, text: str) -> Dict[str, any]:
        """
        Rule-based disclosure detection using regex patterns

        Args:
            text: Text to analyze

        Returns:
            Detection results
        """
        if not text:
            return {
                "has_disclosure": False,
                "confidence": 0.0,
                "markers": [],
                "method": "rule-based"
            }

        detected_markers = []

        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                detected_markers.extend(matches)

        has_disclosure = len(detected_markers) > 0
        confidence = min(1.0, len(detected_markers) * 0.4)  # Each marker adds 0.4

        return {
            "has_disclosure": has_disclosure,
            "confidence": confidence,
            "markers": list(set(detected_markers)),  # Remove duplicates
            "method": "rule-based",
            "total_markers": len(detected_markers)
        }

    def detect_llm(self, text: str) -> Dict[str, any]:
        """
        LLM-based disclosure detection using fine-tuned model

        Args:
            text: Text to analyze

        Returns:
            Detection results
        """
        try:
            if not self.llm_model:
                logger.warning("LLM not available, falling back to rule-based")
                return self.detect_rule_based(text)

            # Use LLM for prediction
            result = self.llm_model.predict(text)

            return {
                "has_disclosure": result.get("disclosure", False),
                "confidence": 0.9 if result.get("disclosure") else 0.1,
                "markers": [],
                "method": "llm",
                "raw_output": result.get("raw", "")
            }

        except Exception as e:
            logger.error(f"LLM detection failed: {str(e)}")
            return self.detect_rule_based(text)

    def analyze(self, text: str, description: str = "") -> Dict[str, any]:
        """
        Complete disclosure analysis

        Args:
            text: Main text (transcript, post content, etc.)
            description: Additional text (video description, caption, etc.)

        Returns:
            Complete detection results
        """
        # Combine texts
        combined_text = f"{text}\n{description}"

        # Use LLM if available, otherwise rule-based
        if self.use_llm and self.llm_model:
            result = self.detect_llm(combined_text)
        else:
            result = self.detect_rule_based(combined_text)

        # Also check with rules for extra validation
        rule_result = self.detect_rule_based(combined_text)

        # Combine results
        final_confidence = max(result["confidence"], rule_result["confidence"])
        has_disclosure = result["has_disclosure"] or rule_result["has_disclosure"]

        return {
            "has_disclosure": has_disclosure,
            "confidence": final_confidence,
            "score": final_confidence,
            "markers": rule_result["markers"],
            "method": result["method"],
            "details": {
                "llm_result": result if self.use_llm else None,
                "rule_result": rule_result
            }
        }

    def extract_disclosure_text(self, text: str) -> Optional[str]:
        """
        Extract the specific disclosure text from content

        Args:
            text: Text to search

        Returns:
            Extracted disclosure text or None
        """
        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                # Extract surrounding context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                return text[start:end].strip()

        return None
