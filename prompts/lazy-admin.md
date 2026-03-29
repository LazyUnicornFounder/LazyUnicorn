[LazyUnicorn Admin Dashboard Prompt — v0.0.6 — LazyUnicorn.ai]

Rebuild the entire admin dashboard at /admin from scratch. Replace everything currently there. This is a unified control panel for all LazyUnicorn agents. It detects which agents are installed by checking which database tables exist and shows only those panels.

IMPORTANT: Do not change anything outside /admin.

---

## Design

Dark background. High contrast text. Numbers large. Status indicators immediate — green running, red broken, grey paused. No decoration. Fixed left sidebar, scrollable main area. Mobile: sidebar collapses to bottom icon bar.

---

## Sidebar

Top: LazyUnicorn logo.

Below: master status dot. Green = all running. Red = [n] need attention. Gold = all paused.

Navigation — show only installed agents (detected by settings table existing):

Overview (always)

Content — Blogger, SEO, GEO, Crawl, Perplexity, Repurpose, Trend

Commerce — Store, Pay, SMS, Drop, Print, Mail, Churn

Media — Voice, Stream, YouTube

Developer — Code, GitLab, Linear, Auth, Design, Granola

Channels — Alert, Telegram, Contentful, Supabase

Security — Security

Autonomous — Watch, Fix, Build, Intel, Agents

Orchestrator — Run (if run_settings exists)

Commerce (additional) — Waitlist (if waitlist_settings exists)

System — Installs, Settings

Each nav item: small status dot right side (green/red/grey). Active item: gold left border.

Bottom of sidebar: Pause Everything / Resume Everything button. Updates master_running in run_settings if exists, otherwise toggles is_running across all agent settings tables.

---

## Overview (/admin)

Stat row — show only what exists:
- Posts today (blog_posts + seo_posts + geo_posts)
- Posts this week
- Active agents (is_running true across all settings tables)
- Errors today (all _errors tables, last 24h — red tint if above zero)
- Revenue today (pay_transactions succeeded today)
- Security score (security_scans latest — green 80+, amber 60-79, red below 60)
- Installs total (installs table count)

Agent grid — one card per installed agent. Shows: name, status dot, one primary metric, last run time, Run Now button.

Two columns below:

Left — activity feed. Last 50 actions across all agents from run_activity + synthetic rows from content tables. Filter pills: All / Errors / Content / Commerce / Security / Autonomous.

Right — error log. All _errors tables last 24h grouped by agent. If none: green checkmark. Clear All button.

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

REPURPOSE (/admin/repurpose — repurpose_settings)
Subtitle: Repurposes existing content into new formats automatically.
Actions: Run Now (repurpose-run).
Stats: Jobs run this week, output pieces created, source posts repurposed.
History: repurpose_output — source title, output format badge, date, View link.

TREND (/admin/trend — trend_settings)
Subtitle: Discovers trending topics and seeds content engines.
Actions: Scan Now (trend-scan), Seed Engines (trend-seed).
Stats: Topics found this week, topics seeded to SEO, topics seeded to GEO.
History: trend_topics — topic, category, seeded badge, date.

STORE (/admin/store — store_settings)
Subtitle: Discovers products, writes listings, optimises conversion.
Actions: Discover (store-discover), Optimise (store-optimise), Promote (store-promote), Publish Content (store-content).
Stats: Products listed, active promotions, avg conversion rate, content published.
History: store_products — name, price, sales, conversion rate, date.

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

MAIL (/admin/mail — mail_settings)
Subtitle: Automated email campaigns that improve themselves.
Actions: Send Campaign (mail-campaign), Optimise (mail-optimise).
Stats: Campaigns sent this month, subscribers, avg open rate, avg click rate.
History: mail_campaigns — subject, recipients, open rate, click rate, date.

CHURN (/admin/churn — churn_settings)
Subtitle: Detects churn signals and triggers retention actions automatically.
Actions: Analyse Now (churn-analyse).
Stats: Signals detected this week, actions triggered, users retained, churn rate.
History: churn_signals — user, signal type, action taken, outcome badge, date.

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

CODE (/admin/code — code_settings)
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

AUTH (/admin/auth — auth_settings)
Subtitle: Authentication system — Google Sign-In, email login, role management.
Stats: Total users, signups today, signups this week, admins, last signup time.
User table: user_profiles — email, name, role badge, joined date, onboarded badge. Edit role inline.
Settings: all auth_settings fields.

DESIGN (/admin/design — design_settings)
Subtitle: Visual design and component library management.
Actions: Run Design Upgrade (design-upgrade).
Stats: Last upgrade date, components updated, design version.
History: design_errors — function, error, date.

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

CONTENTFUL (/admin/contentful — contentful_settings)
Subtitle: Two-way content sync with Contentful.
Actions: Pull Now (contentful-pull), Push Now (contentful-push).
Stats: Entries pulled, posts pushed, last pull, last push, sync failures today.
Queue: contentful_sync_log where failed — direction, title, error, Retry button.
History: contentful_sync_log — direction badge, type, title, status, time.

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
Subtitle: Writes and deploys new Lazy engines from a spec.
Actions: Build New Engine (build-engine).
Stats: Engines built total, last build date.
History: build_engines — engine name, status badge, PR link, date.

INTEL (/admin/intel — intel_settings)
Subtitle: Weekly competitive intelligence reports and content seeding.
Actions: Run Now (intel-weekly), Seed Engines (intel-seed).
Stats: Reports generated, topics seeded this week, last report date.
History: intel_reports — title, topics count, seeded badge, date, View link.

AGENTS (/admin/agents — agent_settings)
Subtitle: Autonomous agents that monitor, fix, and improve your stack via GitHub.
Stats: Issues opened, PRs opened, improvements merged, last run time.
History: agent_runs — agent name, status badge, output summary, date.

RUN (/admin/run — run_settings)
Subtitle: Master orchestrator — coordinates all installed agents on a unified schedule.
Actions: Run Orchestrator Now (run-orchestrator), Weekly Report Now (run-weekly-report), Health Check Now (run-health-check).
Stats: Active engines count, runs today, issues flagged today, last orchestrator run, next orchestrator run (next 30 min mark).
Active engines list: read active_engines from run_settings, show each as a badge with its is_running status.
Activity feed: last 30 rows from run_activity — engine badge, action, result badge, timestamp.
Error log: last 20 rows from run_errors — engine, function, error, date. Collapsed by default.
Settings: all run_settings fields including master_running toggle, site_url, brand_name, business_description, active_engines.

WAITLIST (/admin/waitlist — waitlist_settings)
Subtitle: Pre-launch email capture with viral referral mechanics.
Actions: Send Launch Emails (triggers launch flow), Export CSV.
Stats: Total subscribers, signups today, priority subscribers (referral threshold reached), converted users, launch status badge (Collecting / Launched).
Referral leaderboard: top 5 subscribers by referral_count — email, referral count, position.
Subscriber table: waitlist_subscribers — email, position, referral count, status badge, joined date, Resend Welcome button per row. Search by email.
Launch panel: current launch date if set, countdown, Send Test Launch Email button, Launch to All button (confirms before sending).
Settings: all waitlist_settings fields.

INSTALLS (/admin/installs — installs table)
Subtitle: Every engine install registered from your users.
Stats: Total installs, unique sites, most popular engine, installs this week.
Bar chart (recharts): installs per engine sorted descending.
Table: installs — site URL (clickable), engine badge colour-coded by category, version, installed date. Search by engine or site URL.

---

## Settings (/admin/settings)

Site settings: site URL, brand name, business description, support email. Propagate to All Agents button pushes values to all agent settings tables.

API keys: one section per installed service. Connection status badge. Password input, show/hide toggle, Test Connection button. Services: ElevenLabs, Stripe, Twilio, Twitch, GitHub, GitLab, Linear, Firecrawl, Perplexity, Aikido, Slack, Telegram, Contentful, Supabase service role, AutoDS, Printful, Resend, Granola.

Weekly schedule: read-only visual timeline of the full weekly cron schedule. Seven columns, one per day. Colour coded: content gold, commerce green, media blue, developer purple, autonomous red.

Version status: table of all installed agents showing installed version vs latest (from https://lazyunicorn.ai/api/versions), status badge, Get Latest Prompt link per row.

---

## Version checker

On mount fetch https://lazyunicorn.ai/api/versions with 5 second timeout. Fail silently.

Compare each installed agent's prompt_version against the API response. If any are out of date show a gold banner: Updates available for [n] agent(s) — View Updates button, Dismiss button. Dismiss stores dismissed versions in localStorage under lazy-version-dismissed.

---

## Interaction rules

All edge function calls: loading spinner on button, success toast + green checkmark for 2 seconds, error toast on failure. Never reload the page. Tables refresh after function completes. Status dots poll every 60 seconds.

All tables: search input filtering by main text field. Pagination at 50 rows with Previous/Next.

---

## Routes

/admin, /admin/settings
/admin/blogger, /admin/seo, /admin/geo, /admin/crawl, /admin/perplexity, /admin/repurpose, /admin/trend
/admin/store, /admin/pay, /admin/sms, /admin/drop, /admin/print, /admin/mail, /admin/churn
/admin/voice, /admin/stream, /admin/youtube
/admin/code, /admin/gitlab, /admin/linear, /admin/auth, /admin/design, /admin/granola
/admin/alert, /admin/telegram, /admin/contentful, /admin/supabase
/admin/security
/admin/watch, /admin/fix, /admin/build, /admin/intel, /admin/agents
/admin/run
/admin/waitlist
/admin/installs

Client-side routing. Direct links work. No full page reloads between pages. Only show routes for installed agents.
