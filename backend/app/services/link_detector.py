"""
Link detector service for identifying commercial/promotional links in descriptions.
Detects potential advertising through links to commercial resources.
"""
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class LinkDetector:
    """Detect commercial/promotional links in text"""

    def __init__(self):
        # Commercial domain keywords (RU/EN)
        self.commercial_keywords = [
            # E-commerce
            'shop', 'store', 'market', 'shopify', 'wildberries', 'ozon',
            'aliexpress', 'amazon', 'beru', 'lenta', 'perekrrestok',
            'magazin', 'купить', 'заказать', 'доставка',
            
            # Services & Apps
            'app', 'download', 'install', 'get', 'promo', 'bonus',
            'cashback', 'скидка', 'промокод', 'бонус', 'кэшбэк',
            
            # Finance
            'bank', 'credit', 'loan', 'invest', 'trading', 'broker',
            'банк', 'кредит', 'инвест', 'трейдинг',
            
            # Education
            'course', 'learn', 'education', 'school', 'online',
            'курс', 'обучение', 'школа', 'вебинар',
            
            # Gaming & Betting
            'casino', 'bet', 'game', 'play', 'win',
            'казино', 'ставки', 'игра', 'выигрыш',
            
            # Health & Beauty
            'clinic', 'medical', 'health', 'beauty', 'salon',
            'клиника', 'медицинский', 'красота', 'салон',
            
            # Real Estate
            'estate', 'property', 'rent', 'sale', 'flat',
            'недвижимость', 'аренда', 'продажа', 'квартира',
            
            # Food & Delivery
            'delivery', 'food', 'restaurant', 'cafe', 'pizza',
            'доставка', 'еда', 'ресторан', 'кафе',
            
            # Tech & Services
            'hosting', 'cloud', 'server', 'software', 'service',
            'хостинг', 'облако', 'сервер', 'программа', 'сервис',
        ]

        # Suspicious TLDs (often used for ads)
        self.suspicious_tlds = [
            '.shop', '.store', '.online', '.site', '.xyz',
            '.top', '.club', '.vip', '.pro', '.biz'
        ]

        # URL shorteners (often hide ad links)
        self.url_shorteners = [
            'bit.ly', 'goo.gl', 't.co', 'tinyurl.com',
            'cutt.ly', 'clck.ru', 'vk.cc', 'tn.link',
            'telegra.ph', 'teletype.in', 'taplink.cc', 'linktr.ee'
        ]

        # Social platforms (less suspicious but can contain ads)
        self.social_platforms = [
            't.me', 'telegram.me', 'vk.com', 'instagram.com',
            'youtube.com', 'tiktok.com', 'twitter.com'
        ]

        # Call-to-action patterns (RU/EN)
        self.cta_patterns = [
            r'переходите\s+по\s+ссылке',
            r'ссылка\s+в\s+(описании|профиле|шапке)',
            r'узнайте\s+подробнее',
            r'заказывайте\s+прямо\s+сейчас',
            r'переходите\s+на\s+сайт',
            r'регистрация\s+по\s+ссылке',
            r'получите\s+бонус',
            r'click\s+the\s+link',
            r'link\s+in\s+(bio|description)',
            r'visit\s+our\s+website',
            r'sign\s+up\s+now',
            r'get\s+yours\s+now',
            r'shop\s+now',
            r'order\s+now',
        ]

        # Compile CTA patterns
        self.compiled_cta_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.cta_patterns
        ]

        # URL pattern
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE
        )

    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        if not text:
            return []
        return self.url_pattern.findall(text)

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a single URL for commercial/advertising signals

        Args:
            url: URL to analyze

        Returns:
            Analysis results
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            full_url = url.lower()

            signals = []
            score = 0.0

            # Check URL shorteners
            for shortener in self.url_shorteners:
                if shortener in domain:
                    signals.append('url_shortener')
                    score += 0.3
                    break

            # Check social platforms (neutral)
            is_social = False
            for social in self.social_platforms:
                if social in domain:
                    is_social = True
                    break

            if not is_social:
                # Check commercial keywords in domain and path
                matched_keywords = []
                for keyword in self.commercial_keywords:
                    if keyword in domain or keyword in path:
                        matched_keywords.append(keyword)
                        score += 0.15

                if matched_keywords:
                    signals.append('commercial_keywords')
                    signals.extend([f'keyword:{k}' for k in matched_keywords])

                # Check suspicious TLDs
                for tld in self.suspicious_tlds:
                    if domain.endswith(tld):
                        signals.append('suspicious_tld')
                        score += 0.2
                        break

            # Cap score at 1.0
            score = min(1.0, score)

            return {
                'url': url,
                'domain': domain,
                'is_commercial': score > 0.3,
                'is_social': is_social,
                'score': score,
                'signals': signals,
            }

        except Exception as e:
            logger.error(f"URL analysis failed: {str(e)}")
            return {
                'url': url,
                'domain': '',
                'is_commercial': False,
                'is_social': False,
                'score': 0.0,
                'signals': [],
                'error': str(e)
            }

    def detect_cta(self, text: str) -> Dict[str, Any]:
        """
        Detect call-to-action phrases in text

        Args:
            text: Text to analyze

        Returns:
            CTA detection results
        """
        if not text:
            return {
                'has_cta': False,
                'score': 0.0,
                'matches': []
            }

        matches = []
        for pattern in self.compiled_cta_patterns:
            found = pattern.findall(text)
            if found:
                matches.extend(found)

        has_cta = len(matches) > 0
        score = min(1.0, len(matches) * 0.4)

        return {
            'has_cta': has_cta,
            'score': score,
            'matches': list(set(matches))
        }

    def analyze(self, text: str, description: str = "") -> Dict[str, Any]:
        """
        Complete link analysis

        Args:
            text: Main text (can include description)
            description: Additional text (video description, caption)

        Returns:
            Complete analysis results
        """
        # Combine texts
        combined_text = f"{text}\n{description}"

        # Extract URLs
        urls = self.extract_urls(combined_text)

        # Analyze each URL
        url_analyses = [self.analyze_url(url) for url in urls]

        # Detect CTAs
        cta_result = self.detect_cta(combined_text)

        # Calculate overall score
        commercial_urls = [u for u in url_analyses if u.get('is_commercial')]
        max_url_score = max([u.get('score', 0) for u in url_analyses], default=0)
        
        # Combine URL score and CTA score
        link_score = max(max_url_score, cta_result['score'])

        # Boost score if multiple commercial links
        if len(commercial_urls) > 1:
            link_score = min(1.0, link_score * 1.2)

        # Has advertising signals if score > threshold or CTA detected
        has_ad_signals = link_score > 0.4 or cta_result['has_cta']

        return {
            'has_ad_signals': has_ad_signals,
            'score': link_score,
            'link_score': link_score,
            'cta_score': cta_result['score'],
            'total_urls': len(urls),
            'commercial_urls': len(commercial_urls),
            'urls': urls,
            'url_details': url_analyses,
            'cta_matches': cta_result['matches'],
            'has_cta': cta_result['has_cta'],
        }
