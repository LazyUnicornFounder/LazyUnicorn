# Lazy Voice

> Category: 🎙️ Media · Version: 0.0.4

## Prompt

````
[Lazy Voice Prompt — v0.0.4 — LazyUnicorn.ai]

Add an autonomous audio narration engine called Lazy Voice to this project. It monitors every new post published to blog_posts, seo_posts, and geo_posts, converts each to audio using the ElevenLabs API, stores the audio file, embeds an audio player on every blog post page, and publishes a podcast feed at /listen — all automatically with no manual input required after setup.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**voice_settings**
id (uuid, primary key, default gen_random_uuid()),
podcast_title (text),
podcast_description (text),
podcast_author (text),
site_url (text),
voice_id (text, default 'EXAVITQu4vr4xnSDxMaL'),
rss_enabled (boolean, default true),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

Note: Store the ElevenLabs API key as a Supabase secret — ELEVENLABS_API_KEY. Never store it in the database table.

**voice_episodes**
id (uuid, primary key, default gen_random_uuid()),
post_id (text),
post_slug (text, unique),
post_title (text),
audio_url (text),
duration_seconds (integer),
file_size_bytes (integer),
source_table (text),
status (text, default 'published'),
published_at (timestamptz, default now()),
created_at (timestamptz, default now())

**voice_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
post_slug (text),
created_at (timestamptz, default now())

Create a Supabase storage bucket called voice-audio with public access enabled.

---

## 2. Setup page

Create a page at /lazy-voice-setup with a form:
- ElevenLabs API key (password) — get one at elevenlabs.io. Will be stored as Supabase secret ELEVENLABS_API_KEY. Never stored in the database.
- Voice ID (text) — the ElevenLabs voice ID to use. Default: EXAVITQu4vr4xnSDxMaL (Rachel voice). Note: find other voice IDs in your ElevenLabs dashboard under Voices.
- Podcast title (what is your podcast called?)
- Podcast description (one sentence describing your podcast)
- Podcast author name
- Site URL (your full site URL — used to build the RSS feed)
- Enable RSS feed (toggle, default on)

Submit button: Start Lazy Voice

On submit:
1. Store ElevenLabs API key as Supabase secret ELEVENLABS_API_KEY
2. Save all other values to voice_settings
3. Set setup_complete to true and prompt_version to 'v0.0.3'
4. Redirect to /admin with message: "Lazy Voice is running. Every new blog post will be narrated automatically within 30 minutes of publishing."

---

## 3. Edge functions

**voice-narrate**
Cron: every 30 minutes — */30 * * * *

1. Read voice_settings. If is_running is false or setup_complete is false exit.
2. Query blog_posts, seo_posts, and geo_posts for posts where status is published and published_at is within the last hour. For each table that does not exist skip it gracefully.
3. For each post check if a voice_episodes row already exists with matching post_slug. If it does skip.
4. Strip all markdown formatting from the post body to get clean plain text.
5. Send to ElevenLabs API at https://api.elevenlabs.io/v1/text-to-speech/[voice_id]:
   - Header: xi-api-key set to ELEVENLABS_API_KEY secret
   - Header: Content-Type application/json
   - Body: model_id "eleven_monolingual_v1", text "[post title]. [cleaned post body]", voice_settings stability 0.5 similarity_boost 0.75
6. Receive the audio binary response.
7. Upload to voice-audio Supabase storage bucket as [post-slug].mp3.
8. Get the public URL of the uploaded file.
9. Insert into voice_episodes: post_slug, post_title, audio_url, source_table (blog_posts/seo_posts/geo_posts), status published, published_at now.
Log all errors to voice_errors with function_name voice-narrate and the post_slug.

**voice-rss**
Serves the podcast RSS feed when called via GET request.

1. Read voice_settings.
2. Query all voice_episodes where status is published ordered by published_at descending.
3. Generate valid RSS 2.0 XML with iTunes podcast namespace:
   - Channel: title, description, link (site_url), language en-us, itunes:author, itunes:category Technology
   - Each episode item: title, description (post title), enclosure url (audio_url) type audio/mpeg, pubDate RFC 2822 format, guid (audio_url)
4. Return XML with Content-Type application/rss+xml.

---

## 4. Audio player component

Create a reusable AudioPlayer React component:
- Props: audioUrl (string), title (string)
- Shows: play/pause button, progress bar, current time, total duration, 1x/1.5x/2x speed control
- Matches the existing site design system
- Accessible: keyboard navigable, ARIA labels

Modify every blog post page at /blog/[slug], /seo/[slug], and /geo/[slug]:
- Query voice_episodes for a matching post_slug
- If an episode exists with status published show the AudioPlayer at the top of the post body before the article content
- Show a label: "🎧 Listen to this article" above the player
- If no episode exists show nothing — no loading state, no placeholder

---

## 5. Podcast feed page

Create a public page at /listen:
- Show podcast title and description from voice_settings at the top
- Show a copyable RSS feed URL: [site_url]/functions/v1/voice-rss
- Show instructions: "Copy this RSS URL and submit it to Apple Podcasts at podcasters.apple.com and Spotify at podcasters.spotify.com to distribute your podcast automatically."
- List all voice_episodes ordered by published_at descending. Each shows: post title, published date, duration, and an embedded HTML audio player using the audio_url.
- At the bottom add: "🦄 Powered by Lazy Voice — autonomous audio narration for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

---

## 6. Admin

Do not build a standalone dashboard page for this engine. The dashboard lives at /admin/voice as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This engine only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all engines in one place." and a link to /lazy-voice-setup.

## 7. Navigation

Add a Listen link to the main site navigation pointing to /listen.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-voice-setup to public navigation.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
