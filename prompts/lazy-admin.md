[LazyUnicorn Admin Dashboard Prompt — v0.0.9 — LazyUnicorn.ai]

Rebuild the entire admin dashboard at /admin from scratch. Replace everything currently there. This is a unified control panel for all LazyUnicorn agents. It detects which agents are installed by checking which database tables exist and shows only those panels.

IMPORTANT: Do not change anything outside /admin.

---

## Design

Dark background #0a0a08. Text #f0ead6 cream. Gold accent #c9a84c. Borders rgba(240,234,214,0.x) — subtle warm white. Font: Space Grotesk. Status dots are the only use of green/amber/red — everything else stays in the LazyUnicorn palette. No sidebar. No standalone dashboard pages. All navigation through top tabs.

---

## Top bar

Fixed across all /admin pages.

Left side: 🦄 LAZY UNICORN logo. Next to it: live agent count — query all settings tables for is_running true and show as "● [n] AGENTS RUNNING" in green. If zero agents running show in muted grey.

Right side: PAUSE ALL text button — on click sets is_running to false across all agent settings tables and updates the label to RESUME ALL. Next to it: ⚙ settings icon linking to /admin/settings. Next to it: gold pill link "LAZY CLOUD ↗" pointing to /lazy-cloud or https://lazyunicorn.ai/cloud.

---

## Category tabs

Shown on /admin only. Gold underline on active tab. Clicking a tab filters the agent grid to show only agents in that category. ALL is selected by default.

Tabs and their agents:

ALL — every agent
CONTENT — Blogger, SEO, GEO, Crawl, Perplexity, Repurpose, Trend
COMMERCE — Store, Drop, Print, Pay, Mail, SMS, Churn
MEDIA — Voice, Stream, YouTube
DEV — Code, GitLab, Linear, Contentful, Design, Auth, Granola
MONITOR — Alert, Telegram, Supabase, Security, Watch
INTELLIGENCE — Fix, Build, Intel, Agents

Platform tools (Run, Admin, Cloud, Waitlist) are not in the tab system.

---

## Overview (/admin)

Only show the stats row when at least one agent settings table exists and setup_complete is true. If no agents are installed, skip the stats row entirely and go straight to the agent grid.

Stats row — 5 stats in equal-width columns:

Posts Today — sum of blog_posts + seo_posts + geo_posts published today where each table exists.

Agents Active — count of settings tables where is_running is true, shown as "[n]/36".

Revenue Today — sum of pay_transactions where status is succeeded and created_at is today. Only show if pay_settings exists. Show as "$[amount]" in gold.

Errors Today — count of all rows across all _errors tables where created_at is today. Show in red tint if above zero.

Security Score — latest score from security_scans. Green if 80+, amber if 60–79, red if below 60. Only show if security_settings exists.

---

## Agent grid

Show all 36 known agents in a responsive grid (4 columns desktop, 2 tablet, 1 mobile). Installed agents appear first. Not installed agents appear below in a visually muted section labelled "NOT INSTALLED — [n] AGENTS". The two sections are separated by a subtle divider with the label "INSTALLED — [n] AGENTS" above the first section.

When a category tab is active, only show agents belonging to that category. Apply the same installed/not-installed split within the filtered view.

Each agent maps to a known settings table. Use this mapping to determine state:

Blogger → blog_settings, SEO → seo_settings, GEO → geo_settings, Crawl → crawl_settings, Perplexity → perplexity_settings, Store → store_settings, Drop → drop_settings, Print → print_settings, Pay → pay_settings, SMS → sms_settings, Mail → mail_settings, Voice → voice_settings, Stream → stream_settings, YouTube → youtube_settings, Code → code_settings, GitLab → gitlab_settings, Linear → linear_settings, Contentful → contentful_settings, Design → design_settings, Auth → auth_settings, Granola → granola_settings, Alert → alert_settings, Telegram → telegram_settings, Supabase → supabase_settings, Security → security_settings, Watch → watch_settings, Fix → fix_settings, Build → build_settings, Intel → intel_settings, Repurpose → repurpose_settings, Trend → trend_settings, Churn → churn_settings, Agents → agent_settings, Run → run_settings, Waitlist → waitlist_settings

---

### Card: Not installed

Border: 1px solid rgba(240,234,214,0.06). Opacity: 0.6. No status dot.

Show: agent name in muted cream, one-line description, "+ INSTALL" ghost button (border rgba(240,234,214,0.1), text rgba(240,234,214,0.3)). Clicking INSTALL links to /lazy-[agent]-setup.

---

### Card: Needs setup (settings table exists, setup_complete is false)

Border: 1px solid rgba(201,168,76,0.25). Status dot: amber #c9a84c.

Show: agent name, a gold left-border callout that lists exactly what is missing (e.g. "Add AIKIDO_API_KEY to Supabase secrets"). Never show a generic "setup required" message without specifying what is needed. Gold fill button "COMPLETE SETUP →" linking to /lazy-[agent]-setup.

Required secrets per agent:
- Security: AIKIDO_API_KEY and aikido_project_id in security_settings
- Watch: GITHUB_TOKEN and GITHUB_REPO in watch_settings
- Agents: GITHUB_TOKEN and GITHUB_REPO in agent_settings
- Fix: GITHUB_TOKEN and GITHUB_REPO in fix_settings
- Build: GITHUB_TOKEN and GITHUB_REPO in build_settings
- YouTube: youtube_channel_id in youtube_settings
- GitLab: gitlab_url and gitlab_token in gitlab_settings
- Linear: linear_api_key in linear_settings
- Contentful: contentful_space_id in contentful_settings
- Pay: stripe_secret_key in pay_settings
- SMS: twilio_account_sid in sms_settings
- Voice: elevenlabs_api_key in voice_settings
- Stream: twitch_channel in stream_settings
- Mail: resend_api_key in mail_settings
- Granola: granola_api_key in granola_settings

---

### Card: Running (setup_complete true, is_running true, no errors in last hour)

Border: 1px solid rgba(240,234,214,0.12). Status dot: green #4ade80.

Show: agent name, 2 key metrics in a 2-column mini-stat grid (use the most meaningful metrics for each agent — posts for content agents, revenue for commerce agents, issues for monitoring agents). Last run time in muted text. "MANAGE →" ghost button.

---

### Card: Error (setup_complete true, is_running true, errors exist in last hour above threshold)

Border: 1px solid rgba(248,113,113,0.2). Status dot: red #f87171.

Show: agent name, red left-border callout with the most recent error message (truncated to 60 chars), gold "How to fix →" inline link. "MANAGE →" ghost button.

---

### Card: Paused (is_running false)

Border: 1px solid rgba(240,234,214,0.08). Opacity: 0.6. Status dot: grey rgba(240,234,214,0.2).

Show: agent name, last known stats in muted style. "RESUME →" ghost button — on click sets is_running to true in that agent's settings table.

---

## Agent pages

All follow the same layout:
1. Status bar — name, subtitle, status badge, is_running toggle
2. Quick actions — buttons that trigger edge functions immediately with loading/success/error states
3. Stats + queue — two columns
4. History — last 50 rows, searchable, paginated
5. Settings — collapsible, saves without page reload
6. Error log — collapsible, last 10 errors, clear button

---

BLOGGER (/admin/blogger — blog_settings)
Subtitle: Publishes blog posts every 15 minutes.
Actions: Publish Now (blog-publish).
Stats: Posts today, this week, SEO posts total, GEO posts total.
Queue: next product in rotation, top unwritten keyword with source badge.
History: blog_posts — title, type, date, View link.

SEO (/admin/seo — seo_settings)
Subtitle: Discovers keywords and publishes ranking articles.
Actions: Publish Now (seo-publish), Discover Now (seo-discover).
Stats: Posts published, keywords found, keywords remaining.
Queue: seo_keywords where has_content false — keyword, priority, source badge, Publish button.
History: seo_posts — title, keyword, date, View link.

GEO (/admin/geo — geo_settings)
Subtitle: Publishes content cited by AI search engines.
Actions: Publish Now (geo-publish), Discover Now (geo-discover), Test Citations (geo-test).
Stats: Posts published, queries found, citation rate.
Queue: geo_queries where has_content false — query, type, source, Publish button.
History: geo_posts — title, product, date, View link.

CRAWL (/admin/crawl — crawl_settings)
Subtitle: Monitors competitors and feeds intelligence into your content agents.
Actions: Crawl Now (crawl-run), Publish Intel (crawl-publish).
Stats: Active targets, pages crawled today, intel items today, leads total.
Queue: crawl_targets — name, URL, last crawled, Crawl Now button per row.
History: crawl_intel — type, title, actioned badge, date.

PERPLEXITY (/admin/perplexity — perplexity_settings)
Subtitle: Researches your niche and tests brand citation rates.
Actions: Research Now (perplexity-research), Test Citations (perplexity-test-citations).
Stats: Research calls this week, brand citation rate, content published.
History: perplexity_content — title, citations count, date, View link.

CONTENTFUL (/admin/contentful — contentful_settings)
Subtitle: Two-way content sync with Contentful.
Actions: Pull Now (contentful-pull), Push Now (contentful-push).
Stats: Entries pulled, posts pushed, last pull, last push, sync failures today.
Queue: contentful_sync_log where failed — direction, title, error, Retry button.
History: contentful_sync_log — direction badge, type, title, status, time.

STORE (/admin/store — store_settings)
Subtitle: Discovers products, writes listings, optimises conversion.
Actions: Discover (store-discover), Optimise (store-optimise), Promote (store-promote), Publish Content (store-content).
Stats: Products listed, active promotions, avg conversion rate, content published.
History: store_products — name, price, sales, conversion rate, date.

DROP (/admin/drop — drop_settings)
Subtitle: Syncs dropshipping products from AutoDS and publishes content.
Actions: Sync Now (drop-sync), Publish Content (drop-content), Optimise (drop-optimise).
Stats: Products synced, content published, last sync time.
History: drop_products — name, price, content badge, date.

PRINT (/admin/print — print_settings)
Subtitle: Syncs Printful products and publishes print-on-demand content.
Actions: Sync Now (print-sync), Publish Content (print-content), Optimise (print-optimise).
Stats: Products synced, content published, last sync time.
History: print_products — name, price, content badge, date.

PAY (/admin/pay — pay_settings)
Subtitle: Stripe payments with self-improving conversion optimisation.
Actions: Optimise Now (pay-optimise), Run Recovery (pay-recover).
Stats: MRR, total revenue, active subscribers, abandoned checkouts, recovery rate.
Queue: pay_abandoned where recovery not sent — email, product, time, Send Recovery button.
History: pay_transactions — email, product, amount, status badge, date.

SMS (/admin/sms — sms_settings)
Subtitle: Automated SMS sequences that improve themselves.
Actions: Run Sequences (sms-sequences-run), Optimise (sms-optimise).
Stats: Sent today, delivery rate, response rate, opted out.
History: sms_messages — direction badge, number, type, status, time.

MAIL (/admin/mail — mail_settings)
Subtitle: Automated email campaigns that improve themselves.
Actions: Send Campaign (mail-campaign), Optimise (mail-optimise).
Stats: Campaigns sent this month, subscribers, avg open rate, avg click rate.
History: mail_campaigns — subject, recipients, open rate, click rate, date.

VOICE (/admin/voice — voice_settings)
Subtitle: Narrates every post in your ElevenLabs voice.
Actions: Narrate Now (voice-narrate).
Stats: Episodes generated, audio hours total, posts without audio.
Queue: blog_posts/seo_posts/geo_posts with no voice_episodes row — title, type, Narrate Now button.
History: voice_episodes — title, source badge, duration, date, Play button.

STREAM (/admin/stream — stream_settings)
Subtitle: Turns every Twitch stream into blog posts and SEO content.
Actions: Process Last Stream (stream-process), Optimise (stream-optimise).
Stats: Streams processed, content published, clips saved. Live status badge.
Queue: stream_sessions ended but unprocessed — title, game, date, Process button.
History: stream_content — title, type badge, views, date.

YOUTUBE (/admin/youtube — youtube_settings)
Subtitle: Turns every YouTube video into transcripts, SEO, GEO, and chapter markers.
Actions: Sync Now (youtube-sync), Fetch Comments (youtube-extract-comments), Track Performance (youtube-track-performance).
Stats: Videos processed, content published, comments extracted, top video this week.
History: youtube_videos — title, processed badge, content count, date.

GITHUB (/admin/code — code_settings)
Subtitle: Turns every GitHub commit into changelogs and developer posts.
Actions: Sync Roadmap (code-sync-roadmap), Optimise (code-optimise).
Stats: Commits processed, content published, open roadmap items, last webhook.
Queue: code_commits where processed false — sha, summary, significance badge, date.
History: code_content — title, type badge, date, View link.

GITLAB (/admin/gitlab — gitlab_settings)
Subtitle: Turns every GitLab commit into changelogs and developer posts.
Actions: Sync Roadmap (gitlab-sync-roadmap), Optimise (gitlab-optimise).
Stats: Commits processed, MRs processed, content published, last webhook.
History: gitlab_content — title, type badge, date, View link.

LINEAR (/admin/linear — linear_settings)
Subtitle: Turns Linear cycles and issues into product updates.
Actions: Sync Now (linear-sync-all), Velocity Report (linear-velocity-report).
Stats: Issues synced, cycles completed, content published, last sync.
Queue: linear_cycles completed but unprocessed — cycle name, issues count, Write Summary button.
History: linear_content — title, type badge, date, View link.

DESIGN (/admin/design — design_settings)
Subtitle: Visual design and component library management.
Stats: Last upgrade date, components updated, design version.
Actions: Run Design Upgrade (design-upgrade).
History: design_errors — function, error, date.

AUTH (/admin/auth — auth_settings)
Subtitle: Authentication system — Google Sign-In, email login, role management.
Stats: Total users, signups today, signups this week, admins, last signup time.
User table: user_profiles — email, name, role badge, joined date, onboarded badge. Edit role inline.
Settings: all auth_settings fields.

GRANOLA (/admin/granola — granola_settings)
Subtitle: Turns meeting notes from Granola into blog posts and product updates.
Actions: Sync Now (granola-sync), Publish Content (granola-publish).
Stats: Meetings synced, content published, last sync time.
Queue: granola_meetings where processed false — title, type, date, Publish button.
History: granola_content — title, meeting source, type badge, date, View link.

ALERT (/admin/alert — alert_settings)
Subtitle: Real-time Slack alerts for every agent event.
Actions: Send Test, Briefing Now (alert-briefing).
Stats: Alerts today, this week, success rate, last alert time.
Toggle grid: all alert_settings boolean toggles, update in real time.
History: alert_log — agent badge, event type, message preview, time, success badge.

TELEGRAM (/admin/telegram — telegram_settings)
Subtitle: Real-time Telegram alerts and bot commands.
Actions: Send Test, Briefing Now (telegram-briefing), Register Webhook.
Stats: Messages today, this week, success rate. Webhook status badge.
Toggle grid: all telegram_settings boolean toggles.
History: telegram_log — agent badge, event type, message preview, time, success badge.

SUPABASE (/admin/supabase — supabase_settings)
Subtitle: Monitors database milestones and publishes product updates.
Actions: Check Now (supabase-monitor), Weekly Report (supabase-weekly-report).
Stats: Current users, signups today, milestones reached, content published.
Queue: supabase_milestones where post_published false — type, value, date, Publish button.
History: supabase_milestones — type, value, date, published badge.

SECURITY (/admin/security — security_settings)
Subtitle: Automated pentests and vulnerability monitoring.
Actions: Run Pentest (security-scan), Quick Scan (security-monitor).
Stats: Security score (large, colour-coded), open critical (red if above zero), open high, last pentest, next pentest.
Vulnerabilities: always visible if any critical/high open — not collapsible. Severity badge, title, first found, Mark Fixed button. If none: green banner.
History: security_scans — date, type, status, score, critical count, View Report button.

WATCH (/admin/watch — watch_settings)
Subtitle: Monitors all agent error tables and opens GitHub issues automatically.
Actions: Run Now (watch-monitor).
Stats: Agents monitored, issues opened this month, issues resolved, last run time.
Open issues: watch_issues where resolved false — agent badge, issue title as GitHub link, severity badge, error count, Mark Resolved button.
Run history: watch_runs — started time, status badge, agents checked, issues opened, duration.
Settings: error threshold, GitHub repo, Slack webhook status.

FIX (/admin/fix — fix_settings)
Subtitle: Reads agent performance data and opens GitHub PRs with prompt improvements.
Actions: Run Now (fix-analyse).
Stats: PRs opened this month, improvements merged, last run time, next run (Sunday 11pm UTC).
Improvements table: fix_improvements — agent badge, problem, section improved, version change, PR link, PR status select.
Run history: fix_runs — date, status badge, agents analysed, PRs opened, duration.

BUILD (/admin/build — build_settings)
Subtitle: Writes and deploys new Lazy agents from a spec.
Actions: Build New Agent (build-engine).
Stats: Agents built total, last build date.
History: build_engines — agent name, status badge, PR link, date.

INTEL (/admin/intel — intel_settings)
Subtitle: Weekly competitive intelligence reports and content seeding.
Actions: Run Now (intel-weekly), Seed Agents (intel-seed).
Stats: Reports generated, topics seeded this week, last report date.
History: intel_reports — title, topics count, seeded badge, date, View link.

REPURPOSE (/admin/repurpose — repurpose_settings)
Subtitle: Repurposes existing content into new formats automatically.
Actions: Run Now (repurpose-run).
Stats: Jobs run this week, output pieces created, source posts repurposed.
History: repurpose_output — source title, output format badge, date, View link.

TREND (/admin/trend — trend_settings)
Subtitle: Discovers trending topics and seeds content agents.
Actions: Scan Now (trend-scan), Seed Agents (trend-seed).
Stats: Topics found this week, topics seeded to SEO, topics seeded to GEO.
History: trend_topics — topic, category, seeded badge, date.

CHURN (/admin/churn — churn_settings)
Subtitle: Detects churn signals and triggers retention actions automatically.
Actions: Analyse Now (churn-analyse).
Stats: Signals detected this week, actions triggered, users retained, churn rate.
History: churn_signals — user, signal type, action taken, outcome badge, date.

AGENTS (/admin/agents — agent_settings)
Subtitle: Autonomous agents that monitor, fix, and improve your stack via GitHub.
Stats: Issues opened, PRs opened, improvements merged, last run time.
History: agent_runs — agent name, status badge, output summary, date.

INSTALLS (/admin/installs — installs table)
Subtitle: Every agent install registered from your users.
Stats: Total installs, unique sites, most popular agent, installs this week.
Bar chart (recharts): installs per agent sorted descending.
Table: installs — site URL (clickable), agent badge colour-coded by category, version, installed date. Search by agent or site URL.

---

## Settings (/admin/settings)

Site settings: site URL, brand name, business description, support email. Propagate to All Agents button pushes values to all agent settings tables.

API keys: one section per installed service. Connection status badge. Password input, show/hide toggle, Test Connection button. Services: ElevenLabs, Stripe, Twilio, Twitch, GitHub, GitLab, Linear, Firecrawl, Perplexity, Aikido, Slack, Telegram, Contentful, Supabase service role, AutoDS, Printful, Resend, Granola.

Weekly schedule: read-only visual timeline of the full weekly cron schedule. Seven columns, one per day. Colour coded: content gold, commerce green, media blue, dev purple, ops red.

Version status: table of all installed agents showing installed version vs latest (from https://lazyunicorn.ai/api/versions), status badge, Get Latest Prompt link per row.

---

## Version checker

On mount fetch https://lazyunicorn.ai/api/versions with 5 second timeout. Fail silently.

Compare each installed agent's prompt_version against the API response. If any are out of date show a gold banner: Updates available for [n] agent(s) — View Updates button, Dismiss button. Dismiss stores dismissed versions in localStorage under lazy-version-dismissed.

---

## Interaction rules

All edge function calls: loading spinner on button, success toast + green checkmark for 2 seconds. Never reload the page. Tables refresh after function completes. Status dots poll every 60 seconds.

All tables: search input filtering by main text field. Pagination at 50 rows with Previous/Next.

---

## Error handling — global rules

Never show a generic "failed" message anywhere in admin. Every failure must show what went wrong and exactly what to do next.

**Agent not configured**
Before rendering any agent panel, check if its settings table exists and setup_complete is true. If not, replace the entire panel with a setup card:
- Title: "[Agent Name] is not configured"
- Message: "Complete setup to activate this agent."
- Button: "Set Up [Agent Name]" linking to /lazy-[agent]-setup
- Do not show action buttons, stats, or history

**Edge function call fails**
When a button triggers an edge function and it returns an error, show a red callout with the actual error message. Below it show a "How to fix" section:
- If the error contains "secret", "api key", or "unauthorized": "Add the required API key to your Supabase secrets — Project Settings → Edge Functions → Secrets"
- If the error contains "not found" or "does not exist": "Check that all database tables were created. Re-run the setup page."
- If the error contains "setup_complete": "Complete the setup page first."
- For all other errors: show the raw error and a "View Error Log" button that scrolls to the agent's error log section

**Missing secrets**
Each agent panel that requires external API keys shows a Requirements section at the top. For each required secret: green checkmark if the last function call succeeded, red warning with the secret name and setup instructions if it failed due to that secret being missing.

**Empty states**
If an agent is configured but has never run: "No data yet — click [primary action button] to run your first check."

---

## Routes

/admin, /admin/settings
/admin/blogger, /admin/seo, /admin/geo, /admin/crawl, /admin/perplexity, /admin/contentful
/admin/store, /admin/drop, /admin/print, /admin/pay, /admin/sms, /admin/mail
/admin/voice, /admin/stream, /admin/youtube
/admin/code, /admin/gitlab, /admin/linear, /admin/design, /admin/auth, /admin/granola
/admin/alert, /admin/telegram, /admin/supabase, /admin/security, /admin/watch, /admin/fix, /admin/build, /admin/intel, /admin/repurpose, /admin/trend, /admin/churn, /admin/agents
/admin/installs

Client-side routing. Direct links work. No full page reloads between pages. Only show routes for installed agents.