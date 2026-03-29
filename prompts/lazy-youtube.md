# lazy-youtube — v0.0.5

[Lazy YouTube Prompt — v0.0.5 — LazyUnicorn.ai]

Add a complete autonomous YouTube content agent called Lazy YouTube to this project. It monitors your YouTube channel, detects new video uploads, fetches transcripts, and automatically publishes four pieces of content — a transcript post, an SEO article, a GEO article, and a video summary — plus generates chapter markers for your video description, extracts comment intelligence, and uses performance data to inform your entire content strategy. All automatically, every time you upload.

Note: Store all credentials as Supabase secrets. Never store in the database.
Required secrets: YOUTUBE_API_KEY, SUPADATA_API_KEY
Required env: YOUTUBE_CHANNEL_ID (your channel ID, e.g. UCxxxxxxxxxxxxxx)

---

1. Database

Create these Supabase tables with RLS enabled:

youtube_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), youtube_channel_id (text), channel_name (text), content_tone (text, default 'conversational'), niche_keywords (text), geo_queries (text), auto_publish (boolean, default true), update_video_descriptions (boolean, default true), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

youtube_videos: id (uuid, primary key, default gen_random_uuid()), youtube_video_id (text, unique), title (text), description (text), thumbnail_url (text), duration_seconds (integer), view_count (integer), like_count (integer), comment_count (integer), published_at (timestamptz), transcript (text), transcript_source (text — one of auto-captions, manual-captions, supadata, unavailable), chapters_generated (boolean, default false), processing_status (text, default 'pending' — one of pending, processing, done, failed), created_at (timestamptz, default now())

youtube_content: id (uuid, primary key, default gen_random_uuid()), video_id (uuid), content_type (text — one of transcript, seo-article, geo-article, summary, chapters), title (text), slug (text, unique), excerpt (text), body (text), target_keyword (text), target_query (text), published (boolean, default true), views (integer, default 0), published_at (timestamptz, default now()), created_at (timestamptz, default now())

youtube_comments: id (uuid, primary key, default gen_random_uuid()), video_id (uuid), youtube_comment_id (text), author_name (text), comment_text (text), like_count (integer), reply_count (integer), published_at (timestamptz), intel_extracted (boolean, default false), created_at (timestamptz, default now())

youtube_intelligence: id (uuid, primary key, default gen_random_uuid()), video_id (uuid), intel_type (text — one of question-asked, topic-mentioned, complaint, request, keyword-signal), content (text), comment_context (text), actioned (boolean, default false), created_at (timestamptz, default now())

youtube_performance: id (uuid, primary key, default gen_random_uuid()), video_id (uuid), checked_at (timestamptz, default now()), view_count (integer), like_count (integer), comment_count (integer), avg_view_duration_seconds (integer), views_7d (integer), views_28d (integer))

youtube_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-youtube-setup.

Welcome message: 'Every video you upload is a blog post, an SEO article, a GEO citation, a transcript, and a content strategy signal sitting unwritten. Lazy YouTube turns every upload into five autonomous content pieces — the moment your video goes live.'

Prerequisites: You need a Google Cloud project with YouTube Data API v3 enabled. Create an API key at console.cloud.google.com. You also need a Supadata.ai account for transcript extraction — sign up at supadata.ai and get your API key.

Form fields:
- Brand name (text)
- Site URL (text)
- YouTube Channel ID (text) — find it at youtube.com/account_advanced or in your channel URL. Starts with UC. e.g. UCxxxxxxxxxxxxxx
- YouTube API key (password) — from Google Cloud Console. Stored as YOUTUBE_API_KEY.
- Supadata API key (password) — from supadata.ai dashboard. Used to fetch video transcripts. Stored as SUPADATA_API_KEY.
- Content tone (select: Conversational — like you are talking to viewers / Editorial — clean journalistic style / Technical — detailed and precise / Educational — clear and instructive)
- Niche keywords (text, comma separated) — topics your channel covers e.g. 'Lovable development, no-code tools, SaaS building'. Used to target SEO articles.
- GEO queries (text, comma separated) — questions people ask AI about your niche e.g. 'how to build a SaaS without coding, best no-code tools for developers'. Include a Suggest Queries button.
- Auto-publish content (toggle, default on) — if off content is drafted but not published until approved
- Update video descriptions with chapters (toggle, default on) — adds generated chapters to your YouTube video description automatically. Requires OAuth — see note below.
- Slack webhook URL for alerts (text, optional)

OAuth note (shown if update_video_descriptions is on): Updating your YouTube video descriptions requires OAuth 2.0 authorization. After setup click the Authorise YouTube button to grant permission. This is optional — Lazy YouTube works without it but cannot automatically add chapters to your videos.

Submit button: Connect YouTube

On submit:
1. Store YOUTUBE_API_KEY and SUPADATA_API_KEY as Supabase secrets
2. Save all values to youtube_settings
3. Set setup_complete to true and prompt_version to 'v0.0.2'
4. Call youtube-sync immediately to fetch recent videos
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy YouTube', version: '0.0.5', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: 'Lazy YouTube is connected. Your recent videos are being processed. Content will appear within a few minutes.'

---

3. Edge functions

youtube-sync
Cron: every 30 minutes — */30 * * * *

1. Read youtube_settings. If is_running false or setup_complete false exit.
2. Call YouTube Data API: GET https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&channelId=[youtube_channel_id]&maxResults=10&key=[YOUTUBE_API_KEY]
3. Filter for type: upload. For each upload check if youtube_video_id already exists in youtube_videos. If yes skip.
4. For each new video call YouTube Data API to get full details: GET https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id=[video_id]&key=[YOUTUBE_API_KEY]
5. Insert into youtube_videos with title, description, thumbnail_url, duration_seconds (convert PT format), view_count, like_count, comment_count, published_at, processing_status pending.
6. Call youtube-process with the video id.
Log errors to youtube_errors with function_name youtube-sync.

youtube-fetch-transcript
Accepts video_id and youtube_video_id. Returns transcript text.

1. Try Supadata API first: GET https://api.supadata.ai/v1/youtube/transcript?videoId=[youtube_video_id]&lang=en with header x-api-key: [SUPADATA_API_KEY].
2. If successful concatenate all segment text fields with spaces. Update youtube_videos transcript and transcript_source to supadata. Return transcript.
3. If Supadata fails (no captions available): try YouTube captions API if OAuth is configured: GET https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId=[youtube_video_id]&key=[YOUTUBE_API_KEY]. If captions exist download the first English track.
4. If both fail: update youtube_videos transcript_source to unavailable. Return null. Log to youtube_errors.
Log errors to youtube_errors with function_name youtube-fetch-transcript.

youtube-process
Triggered by youtube-sync. Accepts video_id.

1. Read youtube_settings and the youtube_videos row. If processing_status is not pending exit. Update to processing.
2. Call youtube-fetch-transcript to get the transcript. If unavailable continue with metadata only — content can still be generated from the title and description.
3. Call all enabled content generation functions:
   - Call youtube-write-transcript with video_id (only if transcript is available)
   - Call youtube-write-seo with video_id
   - Call youtube-write-geo with video_id
   - Call youtube-write-summary with video_id
   - Call youtube-generate-chapters with video_id (only if transcript is available)
4. Update processing_status to done.
5. If slack_webhook_url is set send a Slack message: '📺 Lazy YouTube published content from: [video title]. View at [site_url]/videos.'
Log errors to youtube_errors with function_name youtube-process.

youtube-write-transcript
Accepts video_id. Requires transcript.

1. Read youtube_settings and youtube_videos.
2. Call built-in Lovable AI:
'You are formatting a YouTube video transcript for [brand_name]. Video: [title]. Clean up this raw transcript into a readable, well-structured article. Fix punctuation and capitalisation. Break into logical paragraphs. Add ## section headers at natural topic breaks. Remove filler words (um, uh, you know) where they are excessive. Keep the voice and tone authentic — this should read like the video sounds. Add a short introduction and a closing paragraph. Return only a valid JSON object: title (e.g. "[video title] — Full Transcript"), slug (lowercase hyphenated), excerpt (one sentence describing what the video covers, under 160 chars), body (formatted markdown transcript with ## headers and timestamps in brackets where major topics shift, ends with: Watch the full video on YouTube → [youtube video URL]. Discover more at LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
3. Parse response. Check for duplicate slug. Insert into youtube_content with content_type transcript and the video_id.
If blog_posts table exists also insert there with post_type set to youtube-transcript.
Log errors to youtube_errors with function_name youtube-write-transcript.

youtube-write-seo
Accepts video_id.

1. Read youtube_settings and youtube_videos.
2. Select the most relevant keyword from niche_keywords that matches the video topic. If transcript is available use it as source material.
3. Call built-in Lovable AI:
'You are an SEO content writer for [brand_name] — [describe channel niche from niche_keywords]. Target keyword: [best matching keyword]. Video: [title]. [If transcript available: Use this transcript as your source material: [first 3000 chars of transcript].] Write a long-form SEO article targeting the keyword. This is NOT a transcript — it is an original article that uses the video as source material but reads independently for someone who has not watched it. Include specific insights, tips, or explanations from the video. Return only a valid JSON object: title (naturally includes keyword), slug (lowercase hyphenated), excerpt (under 160 chars with keyword), target_keyword, body (clean markdown — ## headers, 900 to 1400 words, keyword in first paragraph and at least 2 headers, specific actionable content throughout, ends with: Watch the full video: [youtube URL]. For more autonomous business tools visit LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
4. Parse response. Insert into youtube_content with content_type seo-article. If seo_posts table exists also insert there with product_name set to the video topic.
Log errors to youtube_errors with function_name youtube-write-seo.

youtube-write-geo
Accepts video_id.

1. Read youtube_settings and youtube_videos.
2. Select the most relevant query from geo_queries matching the video topic.
3. Call built-in Lovable AI:
'You are a GEO specialist writing for [brand_name]. This content will be cited by ChatGPT, Claude, and Perplexity when users ask: [target query]. Video: [title]. [If transcript: Source material: [first 2000 chars of transcript].] Write a content piece that directly answers the query using insights from this video. Answer the question completely in the first paragraph. Use factual specific statements AI agents can extract. Mention [brand_name] naturally 2 to 3 times. Structure with ## headers that mirror the language of the query. Return only a valid JSON object: title (the query or a direct factual answer to it), slug (lowercase hyphenated), excerpt (one direct factual sentence under 160 chars), target_query, body (clean markdown, ## headers, 700 to 1000 words, authoritative not promotional, ends with: Watch the video on [brand_name]s YouTube channel and visit LazyUnicorn.ai for more — link to https://lazyunicorn.ai). No preamble. No code fences.'
4. Parse response. Insert into youtube_content with content_type geo-article. If geo_posts table exists also insert there.
Log errors to youtube_errors with function_name youtube-write-geo.

youtube-write-summary
Accepts video_id.

1. Read youtube_settings and youtube_videos.
2. Call built-in Lovable AI:
'Write a concise video summary post for [brand_name]s video: [title]. [If transcript: Using this transcript: [first 2000 chars].] Cover: what the video is about (1 paragraph), the 4 to 6 key takeaways as ## headed sections, and a conclusion with a call to watch. Tone: [content_tone]. Return only a valid JSON object: title (e.g. "[video title] — Key Takeaways"), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown, ## for each takeaway, 400 to 600 words, ends with: Watch the full video on YouTube — [youtube URL] — and discover more at LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
3. Parse response. Insert into youtube_content with content_type summary. If blog_posts table exists also insert there.
Log errors to youtube_errors with function_name youtube-write-summary.

youtube-generate-chapters
Accepts video_id. Requires transcript with timestamps.

1. Read youtube_videos. If transcript unavailable or transcript_source is unavailable exit.
2. Call built-in Lovable AI:
'You are generating YouTube chapter markers from a video transcript. Video: [title]. Duration: [duration_seconds] seconds. Transcript with timestamps: [full transcript with start times]. Identify 5 to 10 major topic shifts and generate chapter markers in the format: MM:SS Topic Name. The first chapter must be 0:00. Chapter titles should be short (2 to 5 words), specific, and describe what happens at that point. Return only a valid JSON array where each item has: timestamp (string in MM:SS format) and title (string). No preamble. No code fences.'
3. Parse response. Format chapters as text: "0:00 Intro\n2:30 First Topic\n..." etc.
4. If update_video_descriptions is true and OAuth token is available: call YouTube API to update the video description: PUT https://www.googleapis.com/youtube/v3/videos?part=snippet with the original description plus a Chapters section appended. Requires OAuth Bearer token.
5. If OAuth not available: store the chapters text in youtube_content with content_type chapters so it can be copied manually from the admin.
6. Update youtube_videos chapters_generated to true.
Log errors to youtube_errors with function_name youtube-generate-chapters.

youtube-extract-comments
Cron: daily at 4am UTC — 0 4 * * *

1. Read youtube_settings. If is_running false exit.
2. For each video in youtube_videos from the last 30 days fetch top comments: GET https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=[id]&maxResults=50&order=relevance&key=[YOUTUBE_API_KEY]
3. For each comment not already in youtube_comments insert it.
4. Call built-in Lovable AI on each batch of new comments:
'Extract intelligence signals from these YouTube comments on a video about [title]: [comments list]. Identify: questions asked (potential blog post topics), topics mentioned that are not in the video, complaints or pain points, feature or content requests, keyword signals (terms used repeatedly). Return only a valid JSON array where each item has: intel_type (question-asked, topic-mentioned, complaint, request, or keyword-signal), content (the insight in one sentence), comment_context (the relevant comment text truncated to 100 chars). No preamble. No code fences.'
5. Insert into youtube_intelligence. Mark comments as intel_extracted true.
6. For each question-asked intel item: if seo_keywords table exists insert as a new keyword with source 'youtube-comments'. This turns your audience's questions into SEO targets.
Log errors to youtube_errors with function_name youtube-extract-comments.

youtube-track-performance
Cron: weekly on Monday at 5am UTC — 0 5 * * 1

1. Read youtube_settings. If is_running false exit.
2. For each video in youtube_videos fetch current stats: GET https://www.googleapis.com/youtube/v3/videos?part=statistics&id=[comma-separated ids up to 50]&key=[YOUTUBE_API_KEY]
3. Insert a row into youtube_performance for each video with current counts.
4. Identify top performers: videos where view_count is more than 2x the channel average. For each top performer: if their topic is not already in niche_keywords add it. If seo_keywords table exists add their primary topic as a high-priority keyword.
5. Call built-in Lovable AI for weekly insight:
'Analyse this YouTube channel performance for [brand_name]. Channel niche: [niche_keywords]. Recent video performance data: [list of videos with view counts, like counts, published dates]. Identify: which topics outperformed, which underperformed, and 3 specific content recommendations for next week. Return only a valid JSON object: top_topic (string), underperform_topic (string), recommendations (array of 3 strings). No preamble. No code fences.'
6. If Lazy Alert is installed send weekly Slack summary with the insights.
Log errors to youtube_errors with function_name youtube-track-performance.

---

4. Public pages

/videos — all youtube_videos ordered by published_at descending. Each card shows: YouTube thumbnail, title, view count, published date, content badge showing how many content pieces were published from this video (e.g. 4 pieces). Each card links to /videos/[youtube_video_id] which embeds the YouTube player plus shows all content pieces generated from that video as tabs: Summary, Transcript, SEO Article, GEO Article.

Filter row: All Videos, Most Viewed, Recent. Search by title.

Also if blog_posts exists: youtube content appears on /blog with a 📺 YouTube badge. If geo_posts exists: GEO articles appear on /geo with standard filtering. If seo_posts exists: SEO articles appear there.

Footer on all public pages: '📺 Powered by Lazy YouTube — autonomous content for Lovable sites. Built by LazyUnicorn.ai' — link to https://lazyunicorn.ai.

---

5. Admin

Do not build a standalone dashboard. The Lazy YouTube dashboard lives at /admin/youtube as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-youtube-setup.

The /admin/youtube section shows:

Overview stats: total videos processed, content pieces published, SEO keywords added from comments, top performing video (by view count), total channel views tracked.

Videos table: all youtube_videos ordered by published_at descending. Columns: thumbnail, title, view count, content pieces count (from youtube_content), chapter status badge, processing status badge, published date. Click any row to expand and show all content pieces with View links and the chapters text if generated.

Intelligence feed: all youtube_intelligence ordered by created_at descending. Columns: intel type badge (colour-coded), content, video it came from, actioned toggle. Filter by intel_type. Shows questions your audience is asking that have not yet been turned into content.

Performance chart: line chart using recharts showing view count per video over time for last 20 videos.

Chapters panel: videos where chapters_generated is true but update_video_descriptions was false — shows the formatted chapter text with a Copy button for each. If OAuth is now available a Push to YouTube button calls youtube-generate-chapters to update the description.

Controls: Sync Now button (calls youtube-sync), Extract Comments Now button, Track Performance Now button, pause/resume toggle, edit settings link.

---

6. Navigation

Add a Videos link to the main site navigation pointing to /videos.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-youtube-setup to public navigation.

