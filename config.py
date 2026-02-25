import os


class Config:
    MICROSOFT_APP_ID: str = os.environ.get("MICROSOFT_APP_ID", "")
    MICROSOFT_APP_PASSWORD: str = os.environ.get("MICROSOFT_APP_PASSWORD", "")
    MICROSOFT_TENANT_ID: str = os.environ.get("MICROSOFT_TENANT_ID", "")
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
    TEAMS_TEAM_ID: str = os.environ.get("TEAMS_TEAM_ID", "")
    TEAMS_CHANNEL_ID: str = os.environ.get("TEAMS_CHANNEL_ID", "")
    SUMMARY_REPLY_MODE: str = os.environ.get("SUMMARY_REPLY_MODE", "channel")  # "channel" or "dm"
    CLAUDE_MODEL: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    PORT: int = int(os.environ.get("PORT", "3978"))
