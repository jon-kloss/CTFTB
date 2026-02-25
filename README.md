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

#### 1. Register an Azure AD Application

1. Go to the [Azure Portal](https://portal.azure.com) and navigate to **Azure Active Directory** > **App registrations** > **New registration**
2. Set the name to `CTFTB` (or whatever you prefer)
3. Under **Supported account types**, select **Accounts in this organizational directory only (Single tenant)**
4. Leave **Redirect URI** blank and click **Register**
5. On the app's **Overview** page, copy the **Application (client) ID** — this is your `MICROSOFT_APP_ID`
6. Also copy the **Directory (tenant) ID** — this is your `MICROSOFT_TENANT_ID`

##### Create a Client Secret

1. Go to **Certificates & secrets** > **Client secrets** > **New client secret**
2. Add a description (e.g. "CTFTB bot secret"), pick an expiry, and click **Add**
3. Copy the secret **Value** immediately (it won't be shown again) — this is your `MICROSOFT_APP_PASSWORD`

##### Add Graph API Permissions

1. Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Application permissions**
2. Search for and add `ChannelMessage.Read.All`
3. Click **Grant admin consent for [your organization]** (requires admin privileges)

#### 2. Create a Bot Framework Registration

1. In the Azure Portal, search for **Azure Bot** and click **Create**
2. Fill in:
   - **Bot handle**: a unique name (e.g. `ctftb-bot`)
   - **Pricing tier**: F0 (free) is fine for development
   - **Microsoft App ID**: select **Use existing app registration** and paste your `MICROSOFT_APP_ID` from step 1
3. Click **Create** and wait for deployment
4. Once deployed, go to the Bot resource > **Configuration**
5. Set the **Messaging endpoint** to `https://<your-domain>/api/messages` (use your ngrok URL during development)
6. Go to **Channels** > click **Microsoft Teams** > **Save** to enable the Teams channel

#### 3. Install the Bot in Teams

1. Go to the Bot resource > **Channels** > click **Open in Teams** under the Microsoft Teams channel — this lets you chat with the bot directly for testing
2. To add the bot to a specific team/channel, create a Teams app package:
   1. Create a `manifest.json` with your bot's App ID (see [Teams manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema))
   2. Include two icon PNGs (192x192 and 32x32)
   3. Zip all three files together
3. In Teams, go to **Apps** > **Manage your apps** > **Upload a custom app** > **Upload for my org** (or "Upload for me")
4. Select the zip file and install it to the desired team

#### 4. Find Your Team and Channel IDs

You need `TEAMS_TEAM_ID` and `TEAMS_CHANNEL_ID` for your `.env` file. The easiest way to find them:

1. In Teams, navigate to the channel you want to summarize
2. Click the **three dots (...)** next to the channel name > **Get link to channel**
3. The link looks like:
   ```
   https://teams.microsoft.com/l/channel/<CHANNEL_ID>/<channel-name>?groupId=<TEAM_ID>&tenantId=<TENANT_ID>
   ```
4. The `groupId` parameter is your `TEAMS_TEAM_ID`
5. The first path segment after `/channel/` is your `TEAMS_CHANNEL_ID` (URL-decode it, e.g. `19%3A...` becomes `19:...`)

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
