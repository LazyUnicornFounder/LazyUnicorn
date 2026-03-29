# lazy-telegram — v0.0.9

[Lazy Telegram Prompt — v0.0.9 — LazyUnicorn.ai]

Add a complete autonomous Telegram integration called Lazy Telegram to this project. It mirrors Lazy Alert but for Telegram — sending real-time event notifications, a daily briefing, and accepting bot commands to control your agents directly from Telegram. Your autonomous business in your pocket, delivered through Telegram.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-telegram. It is a marketing and landing page for a product called Lazy Telegram — a Telegram bot integration that connects every Lazy agent to your Telegram account so your autonomous business reports to you in real time.

Hero section
Headline: 'Your autonomous business. In your Telegram.' Subheading: 'Lazy Telegram connects every Lazy agent to a Telegram bot. Payments, posts, citations, customer replies, errors, and live events — all delivered as Telegram messages the moment they happen. One prompt. Your business in your pocket.' Primary button: Copy the Lovable Prompt. Secondary button: See What Gets Sent. Badge: Powered by Telegram.

How it works section
Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Create a Telegram bot via BotFather and add your bot token. 4. Every significant event sends you a Telegram message automatically.

What gets sent section
Eight event cards identical in structure to Lazy Alert but for Telegram. Include mock Telegram message previews styled as the Telegram chat interface with a blue LazyUnicorn avatar. Events: payments received, SMS customer replies, brand citations, posts published, products listed, streams going live, releases published, agent errors.

Bot commands section
Headline: Control everything from Telegram. Show commands in a code block: /status — all agents running or paused. /publish blog — trigger one blog post. /publish seo — trigger one SEO post. /publish geo — trigger one GEO post. /pause [agent] — pause an agent. /resume [agent] — resume an agent. /errors — last 10 errors. /report — send daily briefing now. /help — all commands.

Pricing section
Free — self-hosted, bring your own Telegram bot (free). Pro at $9/month — coming soon, hosted version, group chat support, multiple recipient routing.

Bottom CTA
Headline: Your autonomous business. Reporting to you on Telegram. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy Telegram to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete Telegram bot integration called Lazy Telegram to this project. It sends real-time Telegram notifications for every significant event across every installed Lazy agent, delivers a daily morning briefing, and accepts bot commands for controlling agents from Telegram.

1. Database
Create these Supabase tables with RLS enabled:

telegram_settings: id (uuid, primary key, default gen_random_uuid()), chat_id (text), daily_briefing_enabled (boolean, default true), daily_briefing_time (text, default '08:00'), alert_payments (boolean, default true), alert_sms_replies (boolean, default true), alert_posts (boolean, default false), alert_keywords (boolean, default true), alert_citations (boolean, default true), alert_products (boolean, default true), alert_streams (boolean, default true), alert_releases (boolean, default true), alert_errors (boolean, default true), last_checked (timestamptz), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), created_at (timestamptz, default now()).
Note: Store TELEGRAM_BOT_TOKEN as a Supabase secret. Never in the database.

telegram_log: id (uuid, primary key, default gen_random_uuid()), agent (text), event_type (text), message (text), telegram_response (text), sent_at (timestamptz, default now()), success (boolean, default true).

telegram_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-telegram-setup with a form:
- Telegram Bot Token (password) — with instructions: Open Telegram, search for BotFather, send /newbot, follow the prompts to name your bot, copy the token. Stored as Supabase secret TELEGRAM_BOT_TOKEN.
- Your Telegram Chat ID (text) — with instructions: Start a chat with your bot, then visit https://api.telegram.org/bot[YOUR_TOKEN]/getUpdates after sending a message to your bot. Copy the chat id from the response.
- Daily briefing toggle (default on)
- Daily briefing time (select: 6am / 7am / 8am / 9am)
- Alert toggles: Payments, SMS Replies, Posts, Keywords, Citations, Products, Streams, Releases, Errors

Submit button: Connect to Telegram

On submit:
1. Store TELEGRAM_BOT_TOKEN as Supabase secret
2. Save chat_id and all toggles to telegram_settings
3. Set setup_complete to true and prompt_version to 'v0.0.6'
4. Send a test message via Telegram: Your Lazy Telegram bot is connected. Your autonomous business will now report to you here.
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Telegram', version: '0.0.9', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: Telegram connected. Check your bot for the test message.

3. Core send function
Create a Supabase edge function called telegram-send handling POST requests.
Accept: message (text), agent (text), event_type (text).
Read telegram_settings. If is_running is false exit.
Format message using Telegram MarkdownV2:
- Bold header with relevant emoji and event type
- Main message text
- Key details as a clean list
POST to https://api.telegram.org/bot[TELEGRAM_BOT_TOKEN]/sendMessage with: chat_id from telegram_settings, text as the formatted message, parse_mode MarkdownV2.
Insert into telegram_log.
Log errors to telegram_errors with function_name telegram-send.

4. Event monitor edge function
Create a Supabase edge function called telegram-monitor. Cron: every 5 minutes — */5 * * * *

Identical logic to Lazy Alert's alert-monitor but calling telegram-send instead of alert-send. Monitor: pay_transactions for payments, sms_messages for replies, seo_posts and geo_posts for keyword/citation events, store_products for new products, stream_sessions for live streams, code_content and gitlab_content for releases, all error tables for agent errors. Also monitor security_vulnerabilities for new critical or high severity findings where alerted is false and first_found_at is greater than last_checked — send alert with 🚨 emoji and mark as alerted true. Use last_checked watermark approach. Update last_checked after each run.
Log errors to telegram_errors with function_name telegram-monitor.

5. Daily briefing edge function
Create a Supabase edge function called telegram-briefing. Cron: 0 8 * * * (adjust based on setting).

Collect same metrics as Lazy Alert's briefing. Call the built-in Lovable AI to write a 3 to 5 bullet briefing. Format as a clean Telegram message with bold headers. Call telegram-send with agent Lazy Run and event_type daily-briefing.
Log errors to telegram_errors with function_name telegram-briefing.

6. Bot command edge function
Create a Supabase edge function called telegram-command handling POST requests at /api/telegram-webhook.

This receives Telegram webhook updates. Read TELEGRAM_BOT_TOKEN from secrets. Parse the message text from the update object.

Register the webhook by calling: https://api.telegram.org/bot[TELEGRAM_BOT_TOKEN]/setWebhook?url=[site_url]/api/telegram-webhook

Handle these commands:
/status — query all agent settings tables, return status of each agent with emoji indicators.
/publish blog — call blog-publish. Reply: Publishing one blog post now.
/publish seo — call seo-publish. Reply: Publishing one SEO post now.
/publish geo — call geo-publish. Reply: Publishing one GEO post now.
/pause [agent] — update is_running to false in matching agent settings table. Reply: [agent] paused.
/resume [agent] — update is_running to true. Reply: [agent] resumed.
/errors — query all agent error tables for last 5 errors each. Format and reply.
/pentest — trigger security-scan immediately if security_settings table exists and is_running is true. Reply: Pentest queued. Results will appear in your dashboard within the next hour. If not installed reply: Lazy Security is not installed.
/security — if security_settings exists query security_scans for latest completed scan score and security_vulnerabilities for open critical and high counts. Reply with score, open critical, open high, and next pentest date. If not installed reply: Lazy Security is not installed.
/report — trigger telegram-briefing immediately. Reply: Sending your briefing now.
/help — reply with all available commands and descriptions.

For unknown commands reply: Unknown command. Send /help for a list of available commands.

Respond to Telegram using the answerMessage API. Log errors to telegram_errors with function_name telegram-command.

7. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/telegram as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-telegram-setup.

8. Navigation
Do not add any Lazy Telegram pages to public navigation. All pages are admin-only.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.