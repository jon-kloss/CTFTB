# CTFTB — Channel Teams Feed The Bear

A Microsoft Teams bot that fetches all posts from a Teams channel for the current day, sends them to Claude, and returns a concise bulleted summary.

## Features

- Triggered by typing **"summarize"** (or @mentioning the bot with "summarize") in a Teams channel
- Fetches today's messages from a configured Teams channel via the Microsoft Graph API
- Sends the conversation transcript to Claude for summarization
- Returns a bulleted markdown summary of key points, decisions, and action items
- Configurable to reply in-channel or as a DM to the requester

## Project Structure

```
CTFTB/
├── app.py              # Entry point: aiohttp server + bot message handler
├── config.py           # Config class reading from env vars
├── graph_client.py     # MS Graph API client (MSAL auth + fetch channel messages)
├── summarizer.py       # Anthropic Claude integration for summarization
├── requirements.txt    # Python dependencies
├── .env.example        # Template of required env vars
└── .gitignore          # Standard Python + .env exclusion
```

## Prerequisites

### Azure Setup

1. **Azure AD app registration** with `ChannelMessage.Read.All` application permission (admin-consented)
2. **Bot Framework registration** with the messaging endpoint set to `https://<your-domain>/api/messages`
3. **Bot installed** (sideloaded) in the target Teams team

### API Keys

- Microsoft Azure AD credentials (app ID, password, tenant ID)
- [Anthropic API key](https://console.anthropic.com/)

## Setup

1. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/<your-username>/CTFTB.git
   cd CTFTB
   pip install -r requirements.txt
   ```

2. Copy the env template and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

3. Start the server:

   ```bash
   python app.py
   ```

   The server runs on port 3978 by default.

4. Expose the server for Teams (for local development):

   ```bash
   ngrok http 3978
   ```

   Update your Bot Framework registration's messaging endpoint to `https://<ngrok-url>/api/messages`.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `MICROSOFT_APP_ID` | Azure AD app (client) ID | *required* |
| `MICROSOFT_APP_PASSWORD` | Azure AD app client secret | *required* |
| `MICROSOFT_TENANT_ID` | Azure AD tenant ID | *required* |
| `ANTHROPIC_API_KEY` | Anthropic API key | *required* |
| `TEAMS_TEAM_ID` | ID of the Teams team to read from | *required* |
| `TEAMS_CHANNEL_ID` | ID of the channel to read from | *required* |
| `SUMMARY_REPLY_MODE` | `channel` (reply in-channel) or `dm` (direct message) | `channel` |
| `CLAUDE_MODEL` | Claude model to use | `claude-sonnet-4-20250514` |
| `PORT` | Server port | `3978` |

## Usage

In the target Teams channel, either:

- Type **summarize**
- @mention the bot with **summarize**

The bot will fetch all messages posted today (UTC), send them to Claude, and reply with a bulleted summary.

## How It Works

1. The bot receives a message via the Bot Framework webhook (`POST /api/messages`)
2. If the message contains "summarize", it authenticates to MS Graph using MSAL client credentials
3. It fetches channel messages and filters client-side for today's date (Graph API doesn't support `$filter` on channel messages)
4. The messages are formatted as a transcript and sent to Claude with a summarization prompt
5. Claude's bulleted summary is returned to the user (in-channel or via DM)

## License

MIT
