import asyncio
import re
import traceback

from aiohttp import web
from botbuilder.core import BotFrameworkAdapterSettings, BotFrameworkHttpAdapter, TurnContext
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import Activity
from dotenv import load_dotenv

load_dotenv()

from config import Config  # noqa: E402
import graph_client  # noqa: E402
import summarizer  # noqa: E402

settings = BotFrameworkAdapterSettings(
    app_id=Config.MICROSOFT_APP_ID,
    app_password=Config.MICROSOFT_APP_PASSWORD,
)
adapter = BotFrameworkHttpAdapter(settings)


async def on_error(context: TurnContext, error: Exception):
    traceback.print_exc()
    await context.send_activity("Sorry, something went wrong while generating the summary.")


adapter.on_turn_error = on_error

TRIGGER = re.compile(r"\bsummarize\b", re.IGNORECASE)


class SummaryBot(TeamsActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text or ""
        # Strip @mention XML that Teams wraps around the bot name
        cleaned = re.sub(r"<at>.*?</at>\s*", "", text).strip()

        if not TRIGGER.search(cleaned):
            return

        await turn_context.send_activity("Fetching today's messages and generating summary...")

        messages = await graph_client.get_today_messages()
        summary = await asyncio.to_thread(summarizer.summarize, messages)

        if Config.SUMMARY_REPLY_MODE == "dm":
            try:
                dm_ref = TurnContext.get_conversation_reference(turn_context.activity)
                dm_ref.conversation = None  # force a new personal conversation
                await turn_context.adapter.create_conversation(
                    dm_ref,
                    lambda ctx: ctx.send_activity(summary),
                )
                await turn_context.send_activity("Summary sent to your DMs!")
                return
            except Exception:
                traceback.print_exc()
                # Fall back to in-channel reply

        await turn_context.send_activity(summary)


bot = SummaryBot()


async def messages(req: web.Request) -> web.Response:
    if req.content_type != "application/json":
        return web.Response(status=415)
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    await adapter.process_activity(activity, auth_header, bot.on_turn)
    return web.Response(status=201)


app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=Config.PORT)
