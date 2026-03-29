# Lazy Repurpose

> Category: ⚙️ Ops · Version: 0.0.4

## Prompt

````
[Lazy Repurpose Prompt — v0.0.4 — LazyUnicorn.ai]

Add an autonomous content repurposing agent called Lazy Repurpose to this project. Every Sunday it reads your top performing blog posts, SEO articles, and GEO content and automatically produces a Twitter thread, a LinkedIn post, a newsletter section, and a short-form video script for each one — published to a queue for scheduling or posted directly. One piece of content becomes five. Every week. Automatically.

Note: Lazy Repurpose uses the built-in Lovable AI. No additional API keys required beyond what is already in your stack. Optional: TWITTER_API_KEY, LINKEDIN_API_KEY for direct posting. Without these, content is queued for manual scheduling.

---

1. Database

Create these Supabase tables with RLS enabled:

repurpose_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), twitter_handle (text), linkedin_profile_url (text), newsletter_name (text), content_tone (text, default 'conversational'), posts_per_week (integer, default 3), auto_post_twitter (boolean, default false), auto_post_linkedin (boolean, default false), include_newsletter (boolean, default true), include_video_script (boolean, default true), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

repurpose_queue: id (uuid, primary key, default gen_random_uuid()), source_post_id (uuid), source_type (text — one of blog-post, seo-article, geo-article), source_title (text), source_url (text), twitter_thread (text), linkedin_post (text), newsletter_section (text), video_script (text), status (text, default 'queued' — one of queued, scheduled, posted, rejected), scheduled_at (timestamptz), posted_at (timestamptz), created_at (timestamptz, default now())

repurpose_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), posts_processed (integer, default 0), pieces_created (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

repurpose_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

Note: Store TWITTER_API_KEY and LINKEDIN_API_KEY as Supabase secrets (optional). Never store in the database.

---

2. Setup page

Create a page at /lazy-repurpose-setup.

Welcome message: 'One piece of content becomes five. Every week. Automatically. Lazy Repurpose reads your top blog posts and SEO articles and produces Twitter threads, LinkedIn posts, newsletter sections, and video scripts for each one — queued for scheduling or posted directly.'

Form fields:
- Brand name (text)
- Site URL (text)
- Twitter handle (text, optional) — without the @ symbol
- LinkedIn profile URL (text, optional)
- Newsletter name (text, optional)
- Content tone (select: Conversational / Professional / Provocative / Educational, default Conversational)
- Posts per week (number, default 3) — how many top posts to repurpose each week
- Auto-post to Twitter (toggle, default off) — requires TWITTER_API_KEY secret
- Auto-post to LinkedIn (toggle, default off) — requires LINKEDIN_API_KEY secret
- Include newsletter sections (toggle, default on)
- Include video scripts (toggle, default on)

Submit button: Activate Lazy Repurpose

On submit:
1. Save all values to repurpose_settings
2. Set setup_complete to true and prompt_version to 'v0.0.4'
3. Redirect to /admin with message: 'Lazy Repurpose is active. It will run this Sunday and queue repurposed content for your review.'

---

3. Edge function

repurpose-run
Cron: every Sunday at 9pm UTC — 0 21 * * 0

1. Read repurpose_settings. If is_running false or setup_complete false exit.
2. Insert into repurpose_runs with status running.
3. Gather top performing content from the last 7 days. Query blog_posts, seo_posts, and geo_posts if they exist. If view counts exist order by views descending, otherwise order by published_at descending. Take posts_per_week count.
4. For each post:
   a. Call the built-in Lovable AI to create repurposed content:
   'You are a content repurposing specialist for [brand_name]. Original post: [title]. Content: [body truncated to 2000 chars]. Repurpose this into 4 formats maintaining the core message and [content_tone] tone. Return only a valid JSON object: twitter_thread (string — 5 to 8 tweets formatted as numbered list, each under 280 chars, engaging hooks, include key insights), linkedin_post (string — 200 to 300 words, professional format, 3 to 5 line breaks for readability, clear value proposition), newsletter_section (string — 150 to 250 words, conversational, one CTA at end), video_script (string — 60 to 90 second script with [INTRO], [MAIN POINTS 1-3], [OUTRO] marked, spoken word style). No preamble. No code fences.'
   b. Parse response.
   c. Insert into repurpose_queue with all fields including source_post_id, source_type, source_title, source_url.
   d. Increment pieces_created counter.
5. If auto_post_twitter true and TWITTER_API_KEY secret exists: for each queued item post twitter_thread to Twitter API and update status to posted.
6. If auto_post_linkedin true and LINKEDIN_API_KEY secret exists: for each queued item post linkedin_post to LinkedIn API and update status to posted.
7. Update repurpose_runs: status completed, posts_processed count, pieces_created count, completed_at now, summary text.
Log errors to repurpose_errors with function_name repurpose-run.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Repurpose lives at /admin/repurpose as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-repurpose-setup.

The /admin/repurpose section shows:

Status bar: last run time, next run (next Sunday 9pm UTC), total pieces created this month, a Run Now button.

Repurposed content queue: all repurpose_queue rows ordered by created_at descending. Columns: source post title with link, source type badge (blog/seo/geo), formats available badges (Twitter/LinkedIn/Newsletter/Video), status badge (queued/scheduled/posted/rejected), created date. Click any row to expand and show all four repurposed versions with Copy buttons. Each version has Schedule, Post Now (if API keys configured), or Reject buttons.

Run history: all repurpose_runs ordered by started_at descending, last 10 rows. Columns: run date, status, posts processed, pieces created, summary.

Settings: all repurpose_settings fields editable, is_running toggle.

Error log: repurpose_errors last 20 rows, collapsed by default.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-repurpose-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
