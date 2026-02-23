from typing import Dict, List, Any


def classify_advertising(
    has_advertising: bool,
    disclosure_markers: List[str] | None,
    detected_brands: List[Dict[str, Any]] | None,
    detected_keywords: List[str] | None,
    has_cta: bool = False,
    has_commercial_links: bool = False,
    commercial_urls: List[str] | None = None,
) -> Dict[str, str]:
    disclosure_markers = disclosure_markers or []
    detected_brands = detected_brands or []
    detected_keywords = detected_keywords or []
    commercial_urls = commercial_urls or []

    has_disclosure = len(disclosure_markers) > 0
    has_mentions = len(detected_brands) > 0 or len(detected_keywords) > 0

    # Priority 1: Official disclosure (ERID, #ad, etc.)
    if has_disclosure:
        return {
            "classification": "official",
            "reason": "Disclosure markers detected (e.g. ERID/#ad/#реклама).",
        }

    # Priority 2: Advertising signals + CTA or commercial links (hidden advertising)
    if has_advertising and (has_cta or has_commercial_links):
        urls_text = f" Links: {', '.join(commercial_urls[:2])}" if commercial_urls else ""
        return {
            "classification": "hidden_ad",
            "reason": f"Potential hidden advertising detected. CTA: {has_cta}, Commercial links: {has_commercial_links}.{urls_text}",
        }

    # Priority 3: Advertising signals without disclosure
    if has_advertising:
        return {
            "classification": "unofficial",
            "reason": "Advertising signals detected without official disclosure.",
        }

    # Priority 4: Brand mentions only
    if has_mentions:
        return {
            "classification": "mention",
            "reason": "Brand mention detected without advertising signals.",
        }

    # Priority 5: CTA or commercial links without strong ad signals
    if has_cta or has_commercial_links:
        urls_text = f" Links: {', '.join(commercial_urls[:2])}" if commercial_urls else ""
        return {
            "classification": "potential_ad",
            "reason": f"Call-to-action or commercial links detected.{urls_text}",
        }

    return {
        "classification": "no_ad",
        "reason": "No advertising signals detected.",
    }
