from datetime import datetime, timezone
from html.parser import HTMLParser

import aiohttp
import msal

from config import Config


class _HTMLTextExtractor(HTMLParser):
    """Strip HTML tags and return plain text."""

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str):
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def _strip_html(html: str) -> str:
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def _get_access_token() -> str:
    app = msal.ConfidentialClientApplication(
        client_id=Config.MICROSOFT_APP_ID,
        client_credential=Config.MICROSOFT_APP_PASSWORD,
        authority=f"https://login.microsoftonline.com/{Config.MICROSOFT_TENANT_ID}",
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Failed to acquire Graph token: {result.get('error_description', result)}")
    return result["access_token"]


async def get_today_messages() -> list[dict]:
    """Fetch today's channel messages from MS Graph, returning [{author, time, text}]."""
    token = _get_access_token()
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    url = (
        f"https://graph.microsoft.com/v1.0"
        f"/teams/{Config.TEAMS_TEAM_ID}"
        f"/channels/{Config.TEAMS_CHANNEL_ID}"
        f"/messages?$top=50"
    )
    headers = {"Authorization": f"Bearer {token}"}
    messages: list[dict] = []

    async with aiohttp.ClientSession() as session:
        while url:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()

            stop_paging = False
            for msg in data.get("value", []):
                created = datetime.fromisoformat(msg["createdDateTime"].replace("Z", "+00:00"))
                if created < today_start:
                    stop_paging = True
                    break

                body = msg.get("body", {})
                text = _strip_html(body.get("content", "")) if body.get("contentType") == "html" else body.get("content", "")
                if not text:
                    continue

                author = msg.get("from", {}).get("user", {}).get("displayName", "Unknown")
                messages.append({
                    "author": author,
                    "time": created.strftime("%H:%M UTC"),
                    "text": text,
                })

            if stop_paging:
                break
            url = data.get("@odata.nextLink")

    return messages
