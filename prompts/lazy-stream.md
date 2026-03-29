# Lazy Stream

> Category: 🎙️ Media · Version: 0.0.8

## Prompt

````
# lazy-stream

> Version: 0.0.8

## Prompt

````
# lazy-stream — v0.0.8

[Lazy Stream Prompt — v0.0.8 — LazyUnicorn.ai]

Add a complete autonomous Twitch content agent called Lazy Stream to this project. It monitors your Twitch channel, processes VODs, writes stream recaps, extracts clips, publishes SEO articles, tracks analytics, and improves its own content quality — all automatically with no manual input required after setup.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**stream_settings**
id (uuid, primary key, default gen_random_uuid()),
twitch_username (text),
twitch_user_id (text),
site_url (text),
business_name (text),
content_niche (text),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
recap_template_guidance (text),
created_at (timestamptz, default now())

Note: Store Twitch credentials as Supabase secrets — TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET. Never store in the database table.

**stream_sessions**
id (uuid, primary key, default gen_random_uuid()),
twitch_stream_id (text, unique),
title (text),
game_name (text),
started_at (timestamptz),
ended_at (timestamptz),
duration_minutes (integer),
peak_viewers (integer),
average_viewers (integer),
status (text, default 'live'),
created_at (timestamptz, default now())

**stream_content**
id (uuid, primary key, default gen_random_uuid()),
session_id (uuid),
content_type (text),
title (text),
slug (text, unique),
excerpt (text),
body (text),
target_keyword (text),
published_at (timestamptz, default now()),
status (text, default 'published'),
views (integer, default 0),
created_at (timestamptz, default now())

**stream_clips**
id (uuid, primary key, default gen_random_uuid()),
session_id (uuid),
twitch_clip_id (text, unique),
title (text),
clip_url (text),
thumbnail_url (text),
view_count (integer),
duration_seconds (numeric),
published_at (timestamptz, default now()),
created_at (timestamptz, default now())

**stream_transcripts**
id (uuid, primary key, default gen_random_uuid()),
session_id (uuid, unique),
transcript_text (text),
word_count (integer),
processed_at (timestamptz, default now())

**stream_optimisation_log**
id (uuid, primary key, default gen_random_uuid()),
content_type (text),
old_template (text),
new_template (text),
trigger_reason (text),
optimised_at (timestamptz, default now())

**stream_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-stream-setup with a form:
- Twitch Client ID (text) — create an application at dev.twitch.tv/console. Stored as Supabase secret TWITCH_CLIENT_ID.
- Twitch Client Secret (password) — from the same Twitch developer application. Stored as Supabase secret TWITCH_CLIENT_SECRET.
- Twitch Username (your exact Twitch channel username)
- Content niche (what kind of content do you stream? e.g. gaming, just chatting, music, creative, educational)
- Business name
- Site URL

Submit button: Activate Lazy Stream

On submit:
1. Store TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET as Supabase secrets
2. Fetch Twitch user ID: call https://api.twitch.tv/helix/users with login=[username] using client credentials token. Store the user ID in twitch_user_id.
3. Save all other values to stream_settings
4. Set setup_complete to true and prompt_version to 'v0.0.5'
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Stream', version: '0.0.8', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: "Lazy Stream is active. Your next stream will be processed and published automatically when it ends."

---

## 3. Core edge functions

**stream-monitor**
Cron: every 5 minutes — */5 * * * *

1. Read stream_settings. If is_running is false or setup_complete is false exit.
2. Get Twitch access token via client credentials: POST to https://id.twitch.tv/oauth2/token using TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET secrets.
3. Call Twitch Streams API: https://api.twitch.tv/helix/streams?user_id=[twitch_user_id]
4. If a live stream is returned and no matching stream_session exists for twitch_stream_id: insert into stream_sessions with status live and stream details.
5. If no live stream is returned: check stream_sessions for any rows with status live. If found: update status to ended, set ended_at to now, call stream-process with that session_id.
Log errors to stream_errors with function_name stream-monitor.

**stream-process** — handles POST requests with session_id in body

1. Read stream_settings. Read matching stream_session.
2. Get Twitch access token.
3. Fetch VOD: https://api.twitch.tv/helix/videos?user_id=[twitch_user_id]&type=archive Find the VOD closest to the stream start time.
4. Fetch top clips: https://api.twitch.tv/helix/clips?broadcaster_id=[twitch_user_id]&started_at=[stream started_at]
5. Insert top 5 clips into stream_clips.
6. Call the built-in Lovable AI to generate a transcript summary:
"You are transcribing a Twitch stream titled [title] covering [game_name]. The top clips were titled: [clip titles]. Generate a detailed summary of what happened during this stream. Cover main topics, memorable moments, and key discussions. Write 500 to 800 words. Return only the summary text with no preamble."
7. Store in stream_transcripts.
8. Call stream-write-content with the session_id.
9. Update stream_sessions status to processed.
Log errors to stream_errors with function_name stream-process.

**stream-write-content** — handles POST requests with session_id in body

1. Read stream_settings, matching stream_session, and stream_transcripts row.
2. Make three AI calls:

Call 1 — recap:
"You are a content writer for [business_name] who streams [content_niche] on Twitch. Write an engaging stream recap for: title [title], game [game_name], summary [transcript_text]. Write 600 to 900 words in an enthusiastic conversational tone. Cover what happened, highlight moments, what to expect next. End with a call to action to follow on Twitch. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (one sentence under 160 characters), body (clean markdown). No preamble. No code fences."

Call 2 — SEO article:
"You are an SEO content writer for [business_name]. Write an SEO-optimised article based on this Twitch stream. Game or topic: [game_name]. Stream summary: [transcript_text]. Target a keyword someone would search on Google related to this. Write 800 to 1200 words of genuinely useful content — tips, analysis, or commentary. End with: [business_name] streams [content_niche] live on Twitch. Follow at twitch.tv/[twitch_username] and discover more autonomous content tools at LazyUnicorn.ai — link LazyUnicorn.ai to https://lazyunicorn.ai. Return only a valid JSON object: title, slug, excerpt (under 160 chars), target_keyword, body (clean markdown). No preamble. No code fences."

Call 3 — highlights:
"Write a punchy highlights post for [business_name] based on these clip titles: [clip titles]. 200 to 300 words. Return only a valid JSON object: title, slug, excerpt (under 160 chars), body (clean markdown). No preamble. No code fences."

3. For each response: check for duplicate slug (append 4-digit number if exists), insert into stream_content with correct content_type (recap/seo-article/highlights).
Log errors to stream_errors with function_name stream-write-content.

---

## 4. Self-improving edge function

**stream-optimise**
Cron: every Sunday at 1pm UTC — 0 13 * * 0

1. Read stream_settings. If is_running is false exit.
2. Query stream_content where content_type is recap ordered by views descending. Take top 3 and bottom 3.
3. Call the built-in Lovable AI:
"You are a content strategist for [business_name] who streams [content_niche]. These recap posts perform well: [top performing titles and first 200 characters of body]. These perform poorly: [low performing titles and first 200 characters]. Identify what makes the high-performers better. Write improved guidance for future stream recaps. Return only the guidance text as a paragraph. No preamble."
4. Insert into stream_optimisation_log.
5. Update recap_template_guidance in stream_settings.
Log errors to stream_errors with function_name stream-optimise.

---

## 5. Public pages

**/streams**
Show all stream_sessions where status is processed ordered by started_at descending. Each row shows stream title, game, date, duration, and links to the recap, SEO article, and highlights for that session.

**/streams/[slug]**
Fetch matching stream_content row. Render full body as formatted HTML. Show title, content type tag, published date, full body. At bottom add: "🦄 Content by Lazy Stream — autonomous Twitch content publishing for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

**/streams/highlights**
Show all stream_clips ordered by view_count descending. Each shows title, thumbnail image, view count, duration, Watch on Twitch link.

**/live**
If most recent stream_session has status live: show live banner with stream title, game, and Watch Live button linking to twitch.tv/[twitch_username].
If no live stream: show last stream date and Follow on Twitch button.

---

## 6. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/stream as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-stream-setup.

## 7. Navigation

Add a Streams link to the main site navigation pointing to /streams.
Add a Live link pointing to /live.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-stream-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
