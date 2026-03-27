# Lazy Supabase

> Category: 📡 Channels · Version: 0.0.5

## Prompt

````
[Lazy Supabase Prompt — v0.0.5 — LazyUnicorn.ai]

Add a complete autonomous Supabase monitoring and content engine called Lazy Supabase to this project. It monitors your Supabase project for database events, user signups, edge function errors, and storage activity — turning database milestones, user growth, and system events into blog posts, product updates, and Slack alerts automatically.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-supabase. It is a marketing and landing page for a product called Lazy Supabase — an autonomous monitoring and content engine that turns your Supabase database events into product updates, user milestone posts, and system alerts automatically.

Hero section
Headline: 'Your Supabase database is full of stories. Lazy Supabase tells them automatically.' Subheading: 'Lazy Supabase monitors your database for user signups, milestone events, and system health — turning every significant moment into a product update, blog post, or Slack alert without you writing a word.' Primary button: Copy the Lovable Prompt. Secondary button: See What It Monitors. Badge: Powered by Supabase.

How it works section
Headline: Your database events. Published automatically. Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Configure which database events to monitor. 4. Significant events trigger content and alerts automatically.

What it monitors section
Eight cards: 1. User milestones — 100th user, 1000th user, growth streaks. Automatically writes a celebratory blog post for every milestone. 2. Signup spikes — detects unusual signup volume and alerts you in Slack. 3. Edge function errors — monitors all edge function error logs and alerts when error rates spike. 4. Storage growth — tracks storage usage and alerts when approaching limits. 5. Database size — monitors table growth and surfaces which tables are growing fastest. 6. Row milestones — when any key table hits a round number posts a product update automatically. 7. Revenue events — monitors pay_transactions if Lazy Pay is installed and surfaces MRR milestones. 8. Self-improving reports — learns which milestone posts get the most traffic and improves the template.

Pricing section
Free — self-hosted, uses your existing Supabase project. Pro at $19/month — coming soon.

Bottom CTA
Headline: Your database is growing. Let it tell its own story. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy Supabase to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete autonomous Supabase monitoring and content engine called Lazy Supabase to this project. It monitors database events, user signups, edge function errors, and milestones — generating blog posts, product updates, and alerts automatically.

1. Database
Create these Supabase tables with RLS enabled:

supabase_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), business_description (text), site_url (text), supabase_project_url (text), monitor_signups (boolean, default true), monitor_errors (boolean, default true), monitor_storage (boolean, default true), monitor_milestones (boolean, default true), milestone_tables (text), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), created_at (timestamptz, default now()).
Note: Store SUPABASE_SERVICE_ROLE_KEY as a Supabase secret. Never in the database.

supabase_snapshots: id (uuid, primary key, default gen_random_uuid()), snapshot_type (text — one of signups, errors, storage, table-size), metric_name (text), metric_value (numeric), recorded_at (timestamptz, default now()).

supabase_milestones: id (uuid, primary key, default gen_random_uuid()), milestone_type (text), milestone_value (numeric), table_name (text), description (text), post_published (boolean, default false), alerted (boolean, default false), reached_at (timestamptz, default now()).

supabase_content: id (uuid, primary key, default gen_random_uuid()), content_type (text — one of milestone-post, product-update, growth-report), title (text), slug (text, unique), excerpt (text), body (text), published_at (timestamptz, default now()), status (text, default 'published'), views (integer, default 0).

supabase_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-supabase-setup with a form:
- Brand name
- Business description
- Site URL
- Supabase project URL (your project URL from the Supabase dashboard)
- Supabase Service Role Key (password) — find in Supabase project settings under API. Stored as Supabase secret SUPABASE_SERVICE_ROLE_KEY.
- Monitor user signups (toggle, default on)
- Monitor edge function errors (toggle, default on)
- Monitor storage growth (toggle, default on)
- Monitor row milestones (toggle, default on)
- Tables to monitor for milestones (text, comma separated — e.g. blog_posts, pay_transactions, sms_messages)

Submit button: Activate Lazy Supabase

On submit:
1. Store SUPABASE_SERVICE_ROLE_KEY as Supabase secret
2. Save all values to supabase_settings
3. Set setup_complete to true and prompt_version to 'v0.0.1'
4. Immediately call supabase-monitor once
5. Redirect to /admin with message: Lazy Supabase is running. Monitoring your database for milestones and events.

3. Core monitoring edge function
Create a Supabase edge function called supabase-monitor. Cron: every hour — 0 * * * *

1. Read supabase_settings. If is_running is false or setup_complete is false exit.
2. Use the Supabase Management API at https://api.supabase.com using SUPABASE_SERVICE_ROLE_KEY to collect metrics:

User signups (if monitor_signups is true):
Query the auth.users table for count of users created in the last hour and total count. Insert a snapshot into supabase_snapshots with snapshot_type signups. Check if the total count has crossed a milestone: 10, 50, 100, 500, 1000, 5000, 10000. If so insert into supabase_milestones and trigger supabase-publish-milestone.

Edge function errors (if monitor_errors is true):
Query the edge function logs for error counts in the last hour. Insert a snapshot with snapshot_type errors. If error rate has increased more than 50 percent versus the previous hour insert a milestone with type error-spike and trigger alert-send if Lazy Alert is installed.

Storage growth (if monitor_storage is true):
Query Supabase storage for total bytes used. Insert a snapshot with snapshot_type storage. If approaching 90 percent of plan limits insert a milestone with type storage-warning and alert.

Table row milestones (if monitor_milestones is true):
For each table in milestone_tables query the row count. Insert a snapshot with snapshot_type table-size and the table name as metric_name. Check if the count has crossed a round milestone: 100, 500, 1000, 5000, 10000, 50000, 100000. If so insert into supabase_milestones and trigger supabase-publish-milestone.

Revenue milestones (if pay_transactions table exists):
Query total successful transaction count and sum of amount_cents. Check for MRR milestones. If Lazy Pay is installed and MRR crosses $100, $500, $1000, $5000 insert a milestone and publish a celebration post.

Log all errors to supabase_errors with function_name supabase-monitor.

4. Content generation edge function
Create a Supabase edge function called supabase-publish-milestone handling POST requests with a milestone_id.

1. Read supabase_settings. Read the matching supabase_milestones row.
2. Call the built-in Lovable AI:
'You are writing a product update post for [brand_name] described as [business_description]. Celebrate this milestone: [description]. Write an authentic, excited but not hypey post that founders and users will want to share. Include what the milestone means, how long it took to get here, and what comes next. 400 to 700 words. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (one punchy sentence under 160 characters), body (clean markdown, no HTML, no bullet points in prose, ## for headers, ends with: Built autonomously using LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
3. Check for duplicate slug — append 4-digit number if exists.
4. Insert into supabase_content and also into blog_posts if that table exists.
5. Update supabase_milestones: set post_published to true.
6. If Lazy Alert is installed call alert-send with engine Lazy Supabase, event_type milestone-reached, and the milestone description.
Log errors to supabase_errors with function_name supabase-publish-milestone.

5. Weekly growth report edge function
Create a Supabase edge function called supabase-weekly-report. Cron: every Monday at 6am UTC — 0 6 * * 1

1. Read supabase_settings. If is_running is false exit.
2. Collect last 7 days of supabase_snapshots data. Calculate: new signups this week, total users, week over week growth rate, error rate trend, storage usage trend, top growing tables.
3. Call the built-in Lovable AI to write a growth report:
'Write a brief weekly growth report for [brand_name]. Data: [metrics]. Write 3 to 5 bullet points highlighting what grew, what stayed flat, and one thing to watch. Friendly tone. Return only the report text.'
4. Insert into supabase_content with content_type growth-report.
5. If Lazy Alert is installed send the report to Slack.
Log errors to supabase_errors with function_name supabase-weekly-report.

6. Public pages
/milestones — show all supabase_content ordered by published_at descending. Each shows title, content type tag, excerpt, and date. Links to /milestones/[slug].
/milestones/[slug] — full post rendered from markdown.
At the bottom add: 🦄 Powered by Lazy Supabase — autonomous database monitoring for Lovable sites. Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

7. Admin

Do not build a standalone dashboard page for this engine. The dashboard lives at /admin/supabase as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all engines in one place." and a link to /lazy-supabase-setup.

8. Navigation
Add Milestones link to the main navigation pointing to /milestones. Add an Admin link to the main site navigation pointing to /admin.
Do not add the setup page to public navigation.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
