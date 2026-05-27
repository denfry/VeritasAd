import pytest
import respx
from httpx import Response
from app.services.social_parsers import (
    fetch_telegram_post,
    fetch_vk_post,
    fetch_instagram_post,
    fetch_tiktok_post,
    fetch_twitter_post,
    fetch_reddit_post,
    extract_social_post
)

@pytest.mark.asyncio
@respx.mock
async def test_fetch_telegram_post():
    url = "https://t.me/durov/251"
    respx.get("https://t.me/durov/251?embed=1").mock(return_value=Response(200, content='<div class="tgme_widget_message_text">Hello World</div><div class="tgme_widget_message_author_name">Durov</div>'))
    
    result = await fetch_telegram_post(url)
    assert result is not None
    assert result["uploader"] == "Durov"
    assert result["description"] == "Hello World"

@pytest.mark.asyncio
@respx.mock
async def test_fetch_reddit_post():
    url = "https://www.reddit.com/r/test/comments/123/title/"
    mock_data = [
        {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "123",
                            "title": "Test Title",
                            "selftext": "Test Content",
                            "author": "test_user",
                            "ups": 100
                        }
                    }
                ]
            }
        }
    ]
    respx.get("https://www.reddit.com/r/test/comments/123/title/.json").mock(return_value=Response(200, json=mock_data))
    
    result = await fetch_reddit_post(url)
    assert result is not None
    assert result["id"] == "123"
    assert result["title"] == "Test Title"
    assert result["uploader"] == "test_user"

@pytest.mark.asyncio
@respx.mock
async def test_fetch_tiktok_post():
    url = "https://www.tiktok.com/@user/video/123"
    html = '<html><meta property="og:title" content="User | TikTok"><meta property="og:description" content="Check this out"></html>'
    respx.get(url).mock(return_value=Response(200, content=html))
    
    result = await fetch_tiktok_post(url)
    assert result is not None
    assert result["uploader"] == "User"
    assert result["description"] == "Check this out"

@pytest.mark.asyncio
@respx.mock
async def test_fetch_twitter_post():
    url = "https://x.com/user/status/123"
    html = '<html><meta property="og:title" content="User on X"><meta property="og:description" content="Tweet content"></html>'
    respx.get(url).mock(return_value=Response(200, content=html))
    
    result = await fetch_twitter_post(url)
    assert result is not None
    assert result["uploader"] == "User"
    assert result["description"] == "Tweet content"

@pytest.mark.asyncio
@respx.mock
async def test_extract_social_post_router():
    # Test router for different platforms
    respx.get("https://t.me/durov/251?embed=1").mock(return_value=Response(200, content='<div class="tgme_widget_message_text">Hello</div>'))
    
    result = await extract_social_post("https://t.me/durov/251")
    assert result is not None
    assert result["id"] == "251"
    
    # Reddit
    mock_reddit = [{"data": {"children": [{"data": {"id": "456", "title": "Red", "selftext": "", "author": "a", "ups": 1}}]}}]
    respx.get("https://www.reddit.com/r/a/comments/456/.json").mock(return_value=Response(200, json=mock_reddit))
    result = await extract_social_post("https://www.reddit.com/r/a/comments/456/")
    assert result is not None
    assert result["id"] == "456"
