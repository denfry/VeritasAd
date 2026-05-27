import pytest
from app.services.link_detector import LinkDetector

def test_link_detector_platforms():
    detector = LinkDetector()
    
    # TikTok
    res = detector.analyze_url("https://www.tiktok.com/@user/video/123")
    assert res["is_social"] is True
    assert res["platform"] == "tiktok"
    
    # X/Twitter
    res = detector.analyze_url("https://x.com/user/status/456")
    assert res["is_social"] is True
    assert res["platform"] == "twitter"
    
    # Reddit
    res = detector.analyze_url("https://www.reddit.com/r/test/comments/789")
    assert res["is_social"] is True
    assert res["platform"] == "reddit"

def test_link_detector_commercial_with_platform():
    detector = LinkDetector()
    
    # Commercial link
    res = detector.analyze_url("https://myshop.com/promo")
    assert res["is_commercial"] is True
    assert res["is_social"] is False
    assert res["platform"] is None
