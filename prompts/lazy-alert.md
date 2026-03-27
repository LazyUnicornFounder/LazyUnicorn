# Lazy Alert

> Category: 📡 Channels · Version: 0.0.5

## Prompt

````
[Lazy Alert Prompt — v0.0.5 — LazyUnicorn.ai]

Add a complete Slack integration called Lazy Alert to this project. It sends real-time Slack notifications for every significant event across every installed Lazy engine, delivers a daily morning briefing, installs slash commands for controlling engines from Slack, and alerts on errors — all automatically with no manual input required after setup.

Note: Store the Slack signing secret as Supabase secret SLACK_SIGNING_SECRET. Never in the database.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**alert_settings**
id (uuid, primary key, default gen_random_uuid()),
slack_webhook_url (text),
slack_channel (text, default 'general'),
daily_briefing_enabled (boolean, default true),
daily_briefing_time (text, default '08:00'),
alert_payments (boolean, default true),
alert_sms_replies (boolean, default true),
alert_posts (boolean, default false),
alert_keywords (boolean, default true),
alert_citations (boolean, default true),
alert_products (boolean, default true),
alert_streams (boolean, default true),
alert_releases (boolean, default true),
alert_errors (boolean, default true),
last_checked (timestamptz),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: Store SLACK_SIGNING_SECRET as Supabase secret.

**alert_log**
id (uuid, primary key, default gen_random_uuid()),
engine (text),
event_type (text),
message (text),
slack_response (text),
sent_at (timestamptz, default now()),
success (boolean, default true)

**alert_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-alert-setup.

Welcome message: "Connect your autonomous business to Slack. Every significant event across every Lazy engine will send a Slack message automatically."

Form fields:
- Slack Incoming Webhook URL (text) — instructions: go to api.slack.com/apps, create a new app, go to Incoming Webhooks, activate and add a webhook, paste the URL here.
- Slack Bot Token (password, optional) — instructions: for slash commands go to your Slack app, add slash commands pointing to [site_url]/api/slack-command, paste Bot User OAuth Token here.
- Slack Channel (text, default: general) — without the hash symbol.
- Daily briefing toggle (default on)
- Daily briefing time (select: 6am / 7am / 8am / 9am)
- Alert toggles grid: Payments, SMS Replies, Posts Published, Keywords Captured, Brand Citations, Products Listed, Streams Live, Releases Published, Engine Errors, Crawl Intelligence, Perplexity Citations

Submit button: Connect to Slack

On submit:
1. Store SLACK_SIGNING_SECRET as Supabase secret
2. Save all values to alert_settings
3. Set setup_complete to true and prompt_version to 'v0.0.1'
4. Send a test message via the webhook: "Your Lazy Alert is connected. Your autonomous business will now report to you in Slack."
5. Redirect to /admin with message: "Slack connected. Check your channel for the test message."

---

## 3. Core send function

Create a Supabase edge function called alert-send handling POST requests.
Accept: message (text), engine (text), event_type (text), fields (array of objects with title and value).

Read alert_settings. If is_running is false or setup_complete is false exit.

Build Slack Block Kit payload:
- Header block: bold title with emoji prefix — 💰 payments, 💬 SMS replies, 📝 posts, 🔑 keywords, 🤖 citations, 🛍️ products, 🔴 streams live, 🚀 releases, ⚠️ errors, 📊 reports, 🕷️ crawl intel, 🔍 perplexity
- Section block: main message text
- Fields block: up to four key-value pairs
- Context block: timestamp and engine name

POST to slack_webhook_url stored in alert_settings.
Insert into alert_log with engine, event_type, message, slack response, success status.
Log errors to alert_errors with function_name alert-send.

---

## 4. Event monitor edge function

Create a Supabase edge function called alert-monitor.
Cron: every 5 minutes — */5 * * * *

Read alert_settings. If is_running is false or setup_complete is false exit.
Use last_checked watermark. Process only events newer than last_checked.

Monitor these events based on their toggle settings:

Payments (if alert_payments and pay_transactions table exists):
New succeeded transactions → call alert-send with 💰 emoji, engine Lazy Pay, event_type payment-received.

SMS replies (if alert_sms_replies and sms_messages table exists):
New inbound messages where message_type is not opt-out → call alert-send with 💬, engine Lazy SMS, event_type customer-replied.

Keywords captured (if alert_keywords and seo_posts table exists):
Batch new SEO posts → one summary message showing count, latest title and keyword.

Brand citations (if alert_citations and geo_citations table exists):
New citations where brand_mentioned is true → call alert-send with 🤖, engine Lazy GEO, event_type brand-cited.

Perplexity citations (if alert_citations and perplexity_citations table exists):
New real citations where brand_mentioned is true → call alert-send with 🔍, engine Lazy Perplexity, event_type brand-cited-perplexity. Include note that this is a real Perplexity API result.

Products listed (if alert_products and store_products table exists):
Batch new products → one summary message.

Streams live (if alert_streams and stream_sessions table exists):
New live sessions → call alert-send with 🔴, engine Lazy Stream, event_type stream-live.

Releases (if alert_releases and code_content or gitlab_content tables exist):
New release-notes content → call alert-send with 🚀.

Crawl intelligence (if crawl_intel table exists):
New price-change or brand-mention intel → call alert-send with 🕷️, engine Lazy Crawl.

Security vulnerabilities (if security_vulnerabilities table exists and alert_errors toggle on):
New critical or high severity vulnerabilities where alerted is false and first_found_at is greater than last_checked → call alert-send with 🚨, engine Lazy Security, event_type vulnerability-found. Message: [severity] vulnerability found: [title]. Fields: Severity, Category, Remediation hint, Dashboard link. After alerting update alerted to true on each vulnerability row.

Engine errors (if alert_errors toggle on):
Query all engine error tables that exist for errors since last_checked. Group by engine. Any engine with more than 3 new errors → call alert-send with ⚠️.

Update last_checked in alert_settings to now after all events processed.
Log all errors to alert_errors with function_name alert-monitor.

---

## 5. Daily briefing edge function

Create a Supabase edge function called alert-briefing.
Cron: 0 8 * * * (default — adjust based on daily_briefing_time setting)

Read alert_settings. If is_running is false or daily_briefing_enabled is false exit.

Collect metrics from last 24 hours from every installed engine (skip any table that does not exist):
blog_posts published, seo_posts published, geo_posts published, geo_citations brand_mentioned true, pay_transactions succeeded and total revenue, sms_messages sent and response rate, store_products new, voice_episodes new, stream_sessions processed, code_content published, gitlab_content published, linear_content published, crawl_intel new items and leads found, perplexity_citations brand_mentioned true.

Call the built-in Lovable AI:
"Write a daily Slack briefing for [brand_name]. Metrics from the last 24 hours: [metrics]. Write 3 to 5 bullet points maximum, each one line. Lead with the most impressive metric. Flag anything unusually low. End with one sentence about what the engines will do today. Return only the briefing text with bullet points. No preamble."

Build Slack message. Header: "Good morning [brand_name] — your daily autonomous business report."
Call alert-send with engine Lazy Run, event_type daily-briefing.
Log errors to alert_errors with function_name alert-briefing.

---

## 6. Slash command edge function

Create a Supabase edge function called alert-command handling POST requests at /api/slack-command.
Verify request using SLACK_SIGNING_SECRET.
Parse command text.

Handle:
/lazy status — return engine status from all settings tables
/lazy publish blog — call blog-publish
/lazy publish seo — call seo-publish
/lazy publish geo — call geo-publish
/lazy crawl — call crawl-run for all active targets
/lazy research — call perplexity-research
/lazy pause [engine] — update is_running false in matching settings table
/lazy resume [engine] — update is_running true
/lazy errors — last 10 errors across all engine error tables
/lazy pentest — triggers security-scan immediately if Lazy Security is installed. Reply: Pentest queued. Results will appear in your dashboard within the next hour. If Lazy Security is not installed reply: Lazy Security is not installed. Paste the Lazy Security prompt into your Lovable project to enable pentesting.
/lazy security — if Lazy Security is installed returns: current security score from the latest completed security_scans row, open critical vulnerability count, open high vulnerability count, and next scheduled pentest date from security_settings. If Lazy Security is not installed reply: Lazy Security is not installed.
/lazy help — list all commands

All responses use Slack ephemeral format.
Log errors to alert_errors with function_name alert-command.

---

## 7. Admin

Do not build a standalone dashboard page for this engine. The dashboard lives at /admin/alert as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This engine only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all engines in one place." and a link to /lazy-alert-setup.

## 8. Navigation

Do not add any Lazy Alert pages to public navigation. All pages are admin-only.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
