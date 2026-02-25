import anthropic

from config import Config


def summarize(messages: list[dict]) -> str:
    """Send channel messages to Claude and return a bulleted summary."""
    if not messages:
        return "No messages found in the channel today."

    transcript = "\n".join(
        f"[{m['time']}] {m['author']}: {m['text']}" for m in messages
    )

    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=Config.CLAUDE_MODEL,
        max_tokens=1024,
        system=(
            "You summarize Microsoft Teams channel conversations. "
            "Return a concise bulleted markdown summary of the key points, decisions, and action items. "
            "Group related messages together. Use '- ' for bullets."
        ),
        messages=[{"role": "user", "content": f"Summarize today's channel messages:\n\n{transcript}"}],
    )
    return response.content[0].text
