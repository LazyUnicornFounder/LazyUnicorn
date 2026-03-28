# Lazy Repurpose

> Category: 🤖 Agents · Version: v0.0.2

## Prompt

````
[Lazy Repurpose Prompt — v0.0.1 — LazyUnicorn.ai]

Add an autonomous content repurposing agent called Lazy Repurpose to this project. Every Sunday it reads your top performing blog posts, SEO articles, and GEO content and automatically produces a Twitter thread, a LinkedIn post, a newsletter section, and a short-form video script for each one — published to a queue for scheduling or posted directly. One piece of content becomes five. Every week. Automatically.

Note: Lazy Repurpose uses the built-in Lovable AI. No additional API keys required beyond what is already in your stack. Optional: TWITTER_API_KEY, LINKEDIN_API_KEY for direct posting. Without these, content is queued for manual scheduling.

---

1. Database

Create these Supabase tables with RLS enabled:

repurpose_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), twitter_handle (text), linkedin_profile_url (text), newsletter_name (text), content_tone (text, default 'conversational'), posts_per_week (integer, default 3), auto_post_twitter (boolean, default false), auto_post_linkedin (boolean, default false), include_newsletter (boolean, default true), include_video_script (boolean, default true), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

repurpose_queue: id (uuid, primary key, default gen_random_uuid()), source_post_id (uuid), source_type (text — one of blog-post, seo-article, geo-article), source_title (text), source_url (text), twitter_thread (text), linkedin_post (text), newsletter_section (text), video_script (text), status (text, default 'queued' — one of queued, scheduled, posted, rejected), scheduled_at (timestamptz), posted_at (timestamptz), created_at (timestamptz, default now())

repurpose_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), posts_processed (integer, default 0), pieces_created (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

repurpose_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
