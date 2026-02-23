from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import logging
import httpx
from config import settings
from services.api_client import VeritasAdApiClient

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """Handle /analyze command."""
    await message.answer(
        "<b>Video Analysis</b>\n\n"
        "Send me a link to a video (YouTube, Telegram, TikTok) "
        "or upload a video file for advertising analysis."
    )


@router.message(F.text.startswith("http"))
async def analyze_url(message: Message):
    """Analyze video from URL."""
    url = message.text or ""
    user_id = message.from_user.id
    api_key = f"tg_{user_id}"

    logger.info(f"Analyze URL request from user {user_id}: {url[:50]}...")
    status_msg = await message.answer("Starting analysis...")

    try:
        api_client = VeritasAdApiClient(settings.API_URL)
        result = await api_client.analyze_url(api_key=api_key, url=url)
        await api_client.close()
    except httpx.ConnectError as e:
        logger.error(f"Connection error analyzing URL: {e}")
        await status_msg.edit_text(
            "❌ <b>Connection Error</b>\n\n"
            "Cannot connect to the analysis server. "
            "Please make sure the backend is running and try again."
        )
        return
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error analyzing URL: {e}")
        await status_msg.edit_text(
            "❌ <b>Timeout Error</b>\n\n"
            "The request timed out. This may happen with long videos or slow connections. "
            "Please try again."
        )
        return
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error analyzing URL: {e.response.status_code}")
        error_detail = ""
        try:
            error_detail = e.response.json().get("detail", str(e.response.text[:100]))
        except Exception:
            error_detail = str(e.response.text[:100]) if e.response.text else "Unknown error"
        await status_msg.edit_text(
            f"❌ <b>Server Error</b>\n\n"
            f"Status: {e.response.status_code}\n"
            f"Details: {error_detail}"
        )
        return
    except Exception as exc:
        logger.exception(f"Unexpected error analyzing URL: {exc}")
        await status_msg.edit_text(
            "❌ <b>Analysis Error</b>\n\n"
            f"An unexpected error occurred: {str(exc)[:150]}"
        )
        return

    final_result = await wait_for_result(api_key, result, status_msg)
    await status_msg.edit_text(render_result(final_result, api_key), parse_mode="HTML")


@router.message(F.video | F.document)
async def analyze_file(message: Message):
    """Analyze uploaded video file."""
    user_id = message.from_user.id
    api_key = f"tg_{user_id}"
    logger.info(f"Analyze file request from user {user_id}")

    status_msg = await message.answer("Downloading file...")

    file_id = None
    filename = "video.mp4"

    if message.video:
        file_id = message.video.file_id
        filename = message.video.file_name or filename
    elif message.document:
        file_id = message.document.file_id
        filename = message.document.file_name or filename

    if not file_id:
        await status_msg.edit_text("❌ Failed to read file. Please try again.")
        return

    try:
        tg_file = await message.bot.get_file(file_id)

        # Check file size (Telegram limit: 20MB for bots)
        if tg_file.file_size and tg_file.file_size > 20 * 1024 * 1024:
            await status_msg.edit_text(
                "❌ <b>File Too Large</b>\n\n"
                "File is too large. Maximum size: 20MB.\n"
                "Please use a smaller video or upload via the website."
            )
            return

        from io import BytesIO
        buffer = BytesIO()
        await message.bot.download_file(tg_file.file_path, buffer)
        buffer.seek(0)
        file_size = len(buffer.getvalue())
        logger.info(f"File downloaded: {filename} ({file_size} bytes)")

        await status_msg.edit_text("Uploading to server for analysis...")

        api_client = VeritasAdApiClient(settings.API_URL)
        result = await api_client.analyze_file(
            api_key=api_key,
            filename=filename,
            content=buffer.read()
        )
        await api_client.close()

    except httpx.ConnectError as e:
        logger.error(f"Connection error analyzing file: {e}")
        await status_msg.edit_text(
            "❌ <b>Connection Error</b>\n\n"
            "Cannot connect to the analysis server. "
            "Please make sure the backend is running and try again."
        )
        return
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error analyzing file: {e}")
        await status_msg.edit_text(
            "❌ <b>Timeout Error</b>\n\n"
            "The request timed out while uploading the file. "
            "Please try again with a smaller file or better connection."
        )
        return
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error analyzing file: {e.response.status_code}")
        error_detail = ""
        try:
            error_detail = e.response.json().get("detail", str(e.response.text[:100]))
        except Exception:
            error_detail = str(e.response.text[:100]) if e.response.text else "Unknown error"
        await status_msg.edit_text(
            f"❌ <b>Server Error</b>\n\n"
            f"Status: {e.response.status_code}\n"
            f"Details: {error_detail}"
        )
        return
    except Exception as exc:
        logger.exception(f"Unexpected error analyzing file: {exc}")
        await status_msg.edit_text(
            "❌ <b>Analysis Error</b>\n\n"
            f"An unexpected error occurred: {str(exc)[:150]}"
        )
        return

    final_result = await wait_for_result(api_key, result, status_msg)
    await status_msg.edit_text(render_result(final_result, api_key), parse_mode="HTML")


async def wait_for_result(
    api_key: str,
    initial_result: dict,
    status_msg: Message,
) -> dict:
    """Wait for async analysis to complete."""
    task_id = initial_result.get("task_id")
    status = initial_result.get("status")

    logger.info(f"Waiting for result, task_id={task_id}, initial_status={status}")

    # If already completed, return immediately
    if not task_id or status not in {"queued", "processing"}:
        logger.info(f"Task already completed or no task_id, returning immediately")
        return initial_result

    last_progress = None
    max_attempts = 300  # ~10 minutes at 2s interval
    consecutive_failures = 0
    max_consecutive_failures = 10

    api_client = VeritasAdApiClient(settings.API_URL)

    try:
        for attempt in range(max_attempts):
            await asyncio.sleep(2)

            try:
                progress_data = await api_client.get_task_status(
                    api_key=api_key,
                    task_id=task_id
                )
                consecutive_failures = 0  # Reset on success
            except Exception as e:
                consecutive_failures += 1
                logger.warning(f"Failed to get progress (attempt {attempt + 1}, consecutive failures: {consecutive_failures}): {e}")
                
                # If too many consecutive failures, abort
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"Too many consecutive failures ({consecutive_failures}), aborting")
                    return {"status": "failed", "error": "Failed to get progress updates from server"}
                continue

            progress = progress_data.get("progress", 0)
            status = progress_data.get("status", "processing")
            message_text = progress_data.get("message", "")

            # Update status message if progress changed
            if progress != last_progress:
                status_text = f"Processing... {progress}%"
                if message_text:
                    status_text += f"\n{message_text}"

                try:
                    await status_msg.edit_text(status_text)
                except Exception as edit_err:
                    logger.debug(f"Failed to edit status message: {edit_err}")
                    pass  # Ignore edit errors (same text)

                last_progress = progress
                logger.debug(f"Task {task_id} progress: {progress}%, status: {status}")

            # Check if completed or failed
            if status in {"completed", "failed"}:
                logger.info(f"Task {task_id} finished with status: {status}")
                try:
                    return await api_client.get_task_result(
                        api_key=api_key,
                        task_id=task_id
                    )
                except Exception as exc:
                    logger.error(f"Failed to fetch final result: {exc}")
                    return {"status": "failed", "error": "Не удалось получить результат"}

        # Timeout
        logger.warning(f"Task {task_id} timed out after {max_attempts} attempts")
        return {"status": "failed", "error": "Превышено время ожидания (10 минут)"}

    finally:
        await api_client.close()


def format_confidence_bar(confidence: float, length: int = 10) -> str:
    """Create visual confidence bar."""
    filled = int(confidence * length)
    empty = length - filled
    return f"{'█' * filled}{'░' * empty} {confidence:.0%}"


def format_timestamp(seconds: float) -> str:
    """Format timestamp as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def format_brand_list(brands: list) -> str:
    """Format detected brands as a readable list."""
    if not brands:
        return "None detected"
    
    brand_lines = []
    for brand in brands[:5]:  # Limit to 5 brands
        name = brand.get("name", "Unknown")
        conf = brand.get("confidence", 0)
        timestamps = brand.get("timestamps", [])
        
        # Format timestamps
        if timestamps:
            ts_str = ", ".join(format_timestamp(ts) for ts in timestamps[:3])
            if len(timestamps) > 3:
                ts_str += f" and {len(timestamps) - 3} more"
            brand_lines.append(f"  {name} ({conf:.0%}) — {ts_str}")
        else:
            brand_lines.append(f"  {name} ({conf:.0%})")
    
    if len(brands) > 5:
        brand_lines.append(f"  and {len(brands) - 5} more brands")
    
    return "\n".join(brand_lines)


def render_result(result: dict, api_key: str) -> str:
    """Render analysis result as HTML message."""
    if result.get("status") == "failed":
        error_msg = result.get("error", "Unknown error")
        return f"<b>Analysis Failed</b>\nReason: {error_msg}"

    has_ads = result.get("has_advertising", False)
    confidence = result.get("confidence_score", 0.0)
    brands = result.get("detected_brands", [])

    # Additional metrics
    visual_score = result.get("visual_score", 0.0)
    audio_score = result.get("audio_score", 0.0)
    text_score = result.get("text_score", 0.0)
    disclosure_score = result.get("disclosure_score", 0.0)
    link_score = result.get("link_score", 0.0)
    transcript = result.get("transcript", "")
    disclosure_markers = result.get("disclosure_markers", [])
    cta_matches = result.get("cta_matches", [])
    commercial_urls = result.get("commercial_urls", [])
    ad_classification = result.get("ad_classification", "no_ad")
    ad_reason = result.get("ad_reason", "")

    # Result indicator
    result_indicator = "[WARNING] " if has_ads else "[OK] "
    result_text = "Advertising detected" if has_ads else "No advertising detected"

    # Build message parts
    parts = [
        f"{result_indicator}<b>ANALYSIS COMPLETE</b>\n",
        f"<b>Result:</b> {result_text}",
        f"<b>Confidence:</b> {format_confidence_bar(confidence)}",
        "",
        "<b>Detection:</b>",
        f"  Visual: {format_confidence_bar(visual_score, 6)}",
        f"  Audio: {format_confidence_bar(audio_score, 6)}",
        f"  Text: {format_confidence_bar(text_score, 6)}",
        f"  Disclosure: {format_confidence_bar(disclosure_score, 6)}",
        f"  Links: {format_confidence_bar(link_score, 6)}",
        "",
        "<b>Brands:</b>",
        format_brand_list(brands),
    ]

    # Add disclosure markers if found
    if disclosure_markers:
        markers_text = ", ".join(disclosure_markers[:3])
        if len(disclosure_markers) > 3:
            markers_text += f" and {len(disclosure_markers) - 3} more"
        parts.extend(["", f"<b>Disclosure Markers:</b> {markers_text}"])

    # Add CTA matches if found
    if cta_matches:
        cta_text = ", ".join(cta_matches[:3])
        if len(cta_matches) > 3:
            cta_text += f" and {len(cta_matches) - 3} more"
        parts.extend(["", f"<b>Calls to Action:</b> {cta_text}"])

    # Add commercial URLs if found
    if commercial_urls:
        urls_text = ", ".join(commercial_urls[:3])
        if len(commercial_urls) > 3:
            urls_text += f" and {len(commercial_urls) - 3} more"
        parts.extend(["", f"<b>Commercial Links:</b> {urls_text}"])

    # Add classification reason
    if ad_reason and ad_classification != "no_ad":
        parts.extend(["", f"<b>Reason:</b> <i>{ad_reason}</i>"])

    # Add transcript snippet if available
    if transcript and len(transcript) > 0:
        snippet = transcript[:200]
        if len(transcript) > 200:
            snippet += "..."
        parts.extend(["", f"<b>Transcript (excerpt):</b>\n<i>{snippet}</i>"])

    # Add API key as hidden
    parts.extend(["", f"<tg-spoiler>API Key: <code>{api_key}</code></tg-spoiler>"])

    return "\n".join(parts)
