from pathlib import Path
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class DisclosureDetector:
    """Detect advertising disclosure markers in text and extract potential brand names."""

    def __init__(self, use_llm: bool = False):
        """
        Initialize disclosure detector
        """
        self.use_llm = use_llm
        self.llm_model = None

        # Disclosure patterns (RU/EN)
        self.disclosure_patterns = [
            r"#ad\b",
            r"#advertisement\b",
            r"#sponsored\b",
            r"#promo\b",
            r"(?P<erid_marker>\berid\b[:\s-]*)(?P<erid_code>[a-z0-9-]{6,})",
            r"\berid\b",
            r"#реклама\b",
            r"\bреклама\b",
            r"на\s+правах\s+рекламы",
            r"\bрекламн\w+\b",
            r"\bспонсор(ство)?\b",
            r"\bпартнер(ство|ский)?\b",
            r"\bпромо(код|акция)?\b",
            r"\bpaid\s+partnership\b",
            r"\bcontains\s+paid\s+promotion\b",
        ]

        # Promo code patterns
        self.promo_patterns = [
            r"(?i)(?:промокод|код|скидка|купон|code|promo)[:\s-]+(?P<code>[A-Z0-9А-Я]{3,15})",
            r"(?i)промокод\s+на\s+\d+%\s+[:\s-]+(?P<code>[A-Z0-9А-Я]{3,15})",
        ]

        # Call-to-action patterns
        self.cta_patterns = [
            r'переходите\s+по\s+ссылке',
            r'ссылка\s+в\s+(описании|профиле|шапке|комментариях)',
            r'узнайте\s+подробнее\s+по\s+ссылке',
            r'заказывайте\s+прямо\s+сейчас',
            r'переходите\s+на\s+сайт',
            r'регистрация\s+по\s+ссылке',
            r'получите\s+бонус\s+по\s+ссылке',
            r'промокод\s+в\s+(описании|профиле)',
            r'click\s+the\s+link',
            r'link\s+in\s+(bio|description)',
            r'visit\s+our\s+website',
            r'sign\s+up\s+now',
            r'get\s+yours\s+now',
            r'shop\s+now',
            r'order\s+now',
            r'download\s+now',
            r'install\s+now',
        ]

        # Compile patterns
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.disclosure_patterns]
        self.compiled_cta_patterns = [re.compile(p, re.IGNORECASE) for p in self.cta_patterns]
        self.compiled_promo_patterns = [re.compile(p) for p in self.promo_patterns]

    def extract_potential_brands(self, text: str, matches: list) -> list:
        """
        Extract potential brand names from the context surrounding detected markers.
        """
        discovered_brands = []
        
        for match_text in matches:
            # Find the position of the marker in the original text
            try:
                # We search for the marker with some padding
                match_idx = text.lower().find(match_text.lower())
                if match_idx == -1: continue

                # Look for capitalized words near the marker (100 chars before/after)
                start = max(0, match_idx - 150)
                end = min(len(text), match_idx + 150)
                context = text[start:end]

                # Pattern for potential brands: 
                # - Word starting with Capital letter 
                # - Not the very first word of a sentence (unless it's a known brand)
                # - Not common stop words
                # - Can be in quotes
                potential = re.findall(r'[«"\'\s]([A-ZА-Я][a-zа-яA-ZА-Я0-9]{2,})[»"\'\s]', context)
                for p in potential:
                    # Filter out блогерские ники (often all caps or mixed case near promo codes)
                    # This is naive but better than nothing
                    if len(p) < 15 and p.lower() not in ["реклама", "промокод", "ссылка", "сайт"]:
                        discovered_brands.append({
                            "name": p,
                            "confidence": 0.6,
                            "source": "contextual_discovery",
                            "marker": match_text
                        })
            except Exception as e:
                logger.debug(f"Error extracting context: {e}")
                
        return discovered_brands

    def detect_rule_based(self, text: str) -> Dict[str, any]:
        """
        Rule-based disclosure detection using regex patterns
        """
        if not text:
            return {
                "has_disclosure": False,
                "confidence": 0.0,
                "markers": [],
                "cta_matches": [],
                "erids": [],
                "promo_codes": [],
                "discovered_brands": [],
                "method": "rule-based"
            }

        detected_markers = []
        cta_matches = []
        erids = []
        promo_codes = []

        # 1. Check disclosure patterns & erids
        for pattern in self.compiled_patterns:
            for match in pattern.finditer(text):
                m_text = match.group(0)
                detected_markers.append(m_text)
                
                # If it's an erid with code, extract it
                if "erid" in m_text.lower() and len(m_text) > 10:
                    erids.append(m_text)

        # 2. Check CTA patterns
        for pattern in self.compiled_cta_patterns:
            matches = pattern.findall(text)
            if matches:
                cta_matches.extend(matches)

        # 3. Check Promo patterns
        for pattern in self.compiled_promo_patterns:
            for match in pattern.finditer(text):
                promo_codes.append(match.group("code"))

        # 4. Discovery: Try to find brands near markers
        discovered = self.extract_potential_brands(text, detected_markers + cta_matches)

        has_disclosure = len(detected_markers) > 0
        has_cta = len(cta_matches) > 0
        
        # Increase confidence if we have multiple signals
        confidence = min(1.0, 
            len(detected_markers) * 0.4 + 
            len(cta_matches) * 0.2 + 
            len(erids) * 0.5 +
            len(promo_codes) * 0.3
        )

        return {
            "has_disclosure": has_disclosure or bool(erids),
            "has_cta": has_cta,
            "confidence": confidence,
            "markers": list(set(detected_markers)),
            "cta_matches": list(set(cta_matches)),
            "erids": list(set(erids)),
            "promo_codes": list(set(promo_codes)),
            "discovered_brands": discovered,
            "method": "rule-based"
        }

    def analyze(self, text: str, description: str = "") -> Dict[str, any]:
        """
        Complete disclosure analysis
        """
        combined_text = f"{text}\n{description}"
        rule_result = self.detect_rule_based(combined_text)

        # Base result
        result = rule_result
        
        # If we have discovered brands, they should be cleaned/unique
        unique_discovered = {}
        for b in rule_result.get("discovered_brands", []):
            name = b["name"]
            if name not in unique_discovered or b["confidence"] > unique_discovered[name]["confidence"]:
                unique_discovered[name] = b
        
        result["discovered_brands"] = list(unique_discovered.values())

        return {
            "has_disclosure": result["has_disclosure"],
            "has_cta": result["has_cta"],
            "confidence": result["confidence"],
            "score": result["confidence"],
            "markers": result["markers"],
            "cta_matches": result["cta_matches"],
            "erids": result["erids"],
            "promo_codes": result["promo_codes"],
            "discovered_brands": result["discovered_brands"],
            "method": result["method"]
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
