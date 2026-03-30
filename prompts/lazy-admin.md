[LazyUnicorn Admin Dashboard Prompt — v0.0.12 — LazyUnicorn.ai]

Rebuild the entire admin dashboard at /admin from scratch. Replace everything currently there. This is a unified control panel for all LazyUnicorn agents. It detects which agents are installed by checking which Supabase tables exist and renders only those.

IMPORTANT: Do not change anything outside /admin.

---

## Design

Three-column layout: fixed left nav sidebar + wide scrollable main content + fixed right sidebar. Dark background #0a0a08. Text #f0ead6 cream. Gold accent #c9a84c. Borders rgba(240,234,214,0.08). Font: Space Grotesk. Status dots are the only use of green/amber/red.

Font sizes: top bar 15px bold, sidebar section headers 11px bold uppercase letter-spaced, sidebar items 14px, page title 28px bold, section labels 11px uppercase letter-spaced, table text 13px, right sidebar labels 10px uppercase, right sidebar values 18px bold.

---

## Top bar

Fixed, full-width, height 52px. Background #0a0a08, border-bottom rgba(240,234,214,0.08).

Left: 🦄 LAZY UNICORN — 15px bold cream.

Center: Search input — placeholder "Search agents..." with ⌘K hint. 400px wide, background rgba(240,234,214,0.05), border rgba(240,234,214,0.1), border-radius 6px.

Right: PAUSE ALL button — sets is_running = false on all settings tables, toggles to RESUME ALL. ⚙ icon → /admin/settings. Gold pill "LAZY CLOUD ↗" → https://lazyunicorn.ai/cloud.

---

## Three-column shell

Used on all /admin pages:

- Left sidebar: 240px fixed, border-right rgba(240,234,214,0.08), scrollable
- Main content: flex:1, padding 32px 40px, scrollable
- Right sidebar: 220px fixed, border-left rgba(240,234,214,0.08), padding 24px 20px

---

## Left sidebar

Top section: 🦄 Lazy 15px bold + "[n] of 36 running" 11px muted. Count = number of settings tables where is_running = true. Padding 20px 16px, border-bottom rgba(240,234,214,0.06).

Navigation groups:

Each group header: 11px bold uppercase letter-spaced, rgba(240,234,214,0.35), padding 16px 16px 6px.

Each agent item: 36px tall, padding 0 16px, 14px, gap 10px, border-radius 4px, margin 0 4px. Hover: rgba(240,234,214,0.04). Active: rgba(201,168,76,0.1), #f0ead6, font-weight 600.

Status dot (7px circle) left of name:
- is_running true + no errors in last hour → #4ade80
- errors in last hour in agent's _errors table → #f87171
- settings table exists, setup_complete false → #c9a84c
- settings table does not exist → rgba(240,234,214,0.2)

"All Agents" item (no group header above it) — active by default.

Groups:
- (none) → All Agents
- CONTENT → Blogger, SEO, GEO, Crawl, Perplexity, Repurpose, Trend
- COMMERCE → Store, Drop, Print, Pay, Mail, SMS, Churn
- MEDIA → Voice, Stream, YouTube
- DEV → Code, GitLab, Linear, Contentful, Design, Auth, Granola
- MONITOR → Alert, Telegram, Supabase, Security, Watch
- INTELLIGENCE → Fix, Build, Intel, Agents

Clicking a group header filters the main table to that category. Clicking an agent item navigates to /admin/[slug].

---

## Overview (/admin)

### Right sidebar — Quick Stats

Title: "QUICK STATS". Each stat: 10px muted label, 18px bold value, 20px gap.

- **Posts Today** — `SELECT COUNT(*) FROM blog_posts WHERE DATE(published_at) = CURRENT_DATE` + same for seo_posts + geo_posts. Only count from tables that exist.
- **Agents Active** — count of settings tables where is_running = true, shown as "[n]/36"
- **Revenue Today** — `SELECT COALESCE(SUM(amount_cents),0)/100 FROM pay_transactions WHERE DATE(created_at) = CURRENT_DATE AND status = 'succeeded'`. Gold text. Only show if pay_settings exists.
- **Errors Today** — sum of COUNT(*) from every _errors table where DATE(created_at) = CURRENT_DATE. Red if > 0.
- **Security Score** — `SELECT score FROM security_scans ORDER BY created_at DESC LIMIT 1`. Color: #4ade80 if >= 80, #c9a84c if 60–79, #f87171 if < 60. Only show if security_settings exists.

### Agent table

7-column grid. Header row: 11px bold uppercase letter-spaced, rgba(240,234,214,0.3), border-bottom rgba(240,234,214,0.1).

Column widths (fr): Agent 2, Status 1.2, Category 1, Activity 1.8, Last Run 1, Next Run 1, Version 1.4.

Row sections in order:
1. Error rows (errors in last hour) — background rgba(248,113,113,0.03)
2. Running rows (setup_complete true, is_running true, no errors last hour)
3. "NOT SET UP YET" divider row (10px muted caps) — then all not-set-up rows at opacity 0.45

**AGENT column** — 14px bold cream + inline button:
- Error: red fill "FIX →" pill
- Running: ghost "MANAGE" pill
- Needs setup (table exists, setup_complete false): gold fill "SET UP"
- Not installed: ghost "SET UP"

**STATUS column** — badge:
- Error: "● ERROR" rgba(248,113,113,0.15) bg, #f87171 text
- Running: "● RUNNING" rgba(74,222,128,0.1) bg, #4ade80 text
- Needs setup: "● NEEDS SETUP" rgba(201,168,76,0.15) bg, #c9a84c text
- Not set up: "NOT SET UP" rgba(240,234,214,0.05) bg, rgba(240,234,214,0.25) text

**CATEGORY column** — 12px muted text.

**ACTIVITY column** — exact query per agent:
- Blogger: `COUNT(*) FROM blog_posts WHERE DATE(published_at) = CURRENT_DATE` → "[n] posts today"
- SEO: `COUNT(*) FROM seo_keywords WHERE has_content = false` → "[n] keywords queued"
- GEO: `COUNT(*) FROM geo_queries WHERE brand_cited = true` / `COUNT(*) FROM geo_queries WHERE has_content = true` → "[n]% citation rate"
- Crawl: `COUNT(*) FROM crawl_intel WHERE actioned = false AND created_at >= NOW() - INTERVAL '7 days'` → "[n] intel items"
- Perplexity: `COUNT(*) FROM perplexity_citations WHERE brand_mentioned = true` / total → "[n]% cited"
- Pay: `COALESCE(SUM(amount_cents),0)/100 FROM pay_transactions WHERE DATE(created_at) = CURRENT_DATE AND status = 'succeeded'` → "$[n] today"
- Mail: `COUNT(*) FROM mail_subscribers WHERE status = 'confirmed'` → "[n] subscribers"
- SMS: `COUNT(*) FROM sms_contacts WHERE opted_out = false` → "[n] contacts"
- Voice: `COUNT(*) FROM voice_episodes WHERE status = 'published'` → "[n] episodes"
- Security: `score FROM security_scans ORDER BY created_at DESC LIMIT 1` → "Score: [n]" (coloured)
- Watch: `COUNT(*) FROM watch_issues WHERE resolved = false` → "[n] issues open"
- Alert: `COUNT(*) FROM alert_log WHERE DATE(sent_at) = CURRENT_DATE` → "[n] alerts today"
- Fix: `COUNT(*) FROM fix_improvements WHERE DATE(created_at) >= DATE_TRUNC('month', CURRENT_DATE)` → "[n] PRs this month"
- Intel: most recent `top_performing_topic FROM intel_briefs ORDER BY created_at DESC LIMIT 1` → topic name, truncated to 30 chars
- Run: `action FROM run_activity ORDER BY created_at DESC LIMIT 1` → last action, truncated
- Repurpose, Trend, Churn, Store, Drop, Print, Stream, YouTube, Code, GitLab, Linear, Contentful, Design, Auth, Granola, Telegram, Supabase, Agents, Build, Waitlist: one-line description of what the agent does (static text from the list below)

Static descriptions for not-set-up agents:
- Repurpose: "Repurpose posts into LinkedIn, tweets, email"
- Trend: "Seed trending topics into SEO and GEO"
- Churn: "Detect and prevent user churn"
- Store: "List and promote Shopify products"
- Drop: "Sync and publish AutoDS products"
- Print: "Sync and publish Printful products"
- Stream: "Process Twitch streams into content"
- YouTube: "Sync YouTube videos and comments"
- Code: "Turn GitHub commits into content"
- GitLab: "Turn GitLab activity into content"
- Linear: "Sync Linear issues to public roadmap"
- Contentful: "Pull and publish Contentful entries"
- Design: "Auto-upgrade design components"
- Auth: "Manage users and roles"
- Granola: "Sync and publish meeting notes"
- Telegram: "Daily briefings via Telegram bot"
- Supabase: "Monitor signups and milestones"
- Agents: "Run all 4 intelligence agents"
- Build: "Build new agent prompts automatically"
- Waitlist: "Manage waitlist signups"

**LAST RUN column** — exact source per agent (show relative time, "Never" if null):
- Blogger: `MAX(published_at) FROM blog_posts`
- SEO: `MAX(published_at) FROM seo_posts`
- GEO: `MAX(published_at) FROM geo_posts`
- Crawl: `MAX(crawled_at) FROM crawl_results`
- Perplexity: `MAX(researched_at) FROM perplexity_research`
- Pay: `MAX(created_at) FROM pay_transactions`
- Mail: `MAX(sent_at) FROM mail_sent`
- SMS: `MAX(sent_at) FROM sms_messages WHERE direction = 'outbound'`
- Voice: `MAX(created_at) FROM voice_episodes`
- Security: `MAX(completed_at) FROM security_scans`
- Watch: `MAX(completed_at) FROM watch_runs`
- Alert: `MAX(sent_at) FROM alert_log`
- Fix: `MAX(completed_at) FROM fix_runs`
- Intel: `MAX(completed_at) FROM intel_runs`
- Run: `MAX(created_at) FROM run_activity`
- All others: `MAX(created_at) FROM [agent]_errors` as a fallback, or "Never"

**NEXT RUN column** — calculate from known cron schedule (show relative time, "—" if not running):
- Blogger: every 15 min — next :00, :15, :30, or :45
- SEO publish: daily at 8am UTC (if posts_per_day=1), or 8am+6pm (if 2), or 6am/12pm/6pm/11pm (if 4)
- SEO discover: next Monday 6am UTC
- GEO publish: daily at 9am UTC (posts_per_day=1) up to 4x/day
- GEO discover: next Monday or Thursday 7am UTC (whichever is sooner)
- GEO test: next Sunday 9am UTC
- Security scan: show `next_pentest_at` from security_settings
- Security poll: every 10 min
- Watch: next top of hour
- Pay recover: next day 10am UTC; Pay optimise: next Sunday 11am UTC
- Alert monitor: every 5 min; Alert briefing: next day at `daily_briefing_time` from alert_settings (default 8am UTC)
- Mail broadcast: next `newsletter_day` 9am UTC; Mail optimise: next Sunday 11am UTC
- SMS sequences: next top of hour; SMS optimise: next Sunday 12pm UTC
- Voice: next :00 or :30
- Crawl run: next :00 or :30; Crawl publish: next day 6am UTC
- Perplexity research: next day 5am UTC; Perplexity test: next Sunday 10am UTC
- Fix: next Sunday 11pm UTC
- Intel: next Monday 6am UTC
- Run orchestrator: next :00 or :30; Run health: next top of hour; Run weekly: next Monday 7am UTC

**VERSION column** — `prompt_version` from each agent's settings table. If behind latest from https://lazyunicorn.ai/api/versions (fetched on mount, 5s timeout, fail silently), show gold "UPDATE" badge.

---

## Agent detail pages

Reached by clicking sidebar item or MANAGE button. URL: /admin/[slug]. Left sidebar stays visible, that agent highlighted active. Back button → /admin.

All detail pages use the three-column shell. Right sidebar shows ACTIONS for that agent.

---

### Blogger (/admin/blogger)

**Header** — "Lazy Blogger", status dot + label, ON/OFF toggle updates `is_running` in blog_settings.

**Stats grid (2×2)**
- Posts Today: `COUNT(*) FROM blog_posts WHERE DATE(published_at) = CURRENT_DATE`
- Posts This Week: `COUNT(*) FROM blog_posts WHERE published_at >= DATE_TRUNC('week', CURRENT_DATE)`
- SEO Posts: `COUNT(*) FROM blog_posts WHERE post_type = 'seo'`
- GEO Posts: `COUNT(*) FROM blog_posts WHERE post_type = 'geo'`

**Next up** — `last_product_published` from blog_settings — show the next product in rotation.

**Recent activity** — last 3 rows from blog_posts ORDER BY published_at DESC — show title + published_at + link slug.

**Settings** (inline editable) — brand_name, posts_per_day, post_mode, tone, target_keywords from blog_settings.

**Error log** — blog_errors ORDER BY created_at DESC LIMIT 10.

**Right sidebar actions**
- Primary: "PUBLISH NOW →" → calls edge function `blog-publish`
- Secondary: "VIEW ALL POSTS ↗" → links to /blog

---

### SEO (/admin/seo)

**Stats grid**
- Posts Published: `COUNT(*) FROM seo_posts`
- Keywords Found: `COUNT(*) FROM seo_keywords`
- Keywords Queued: `COUNT(*) FROM seo_keywords WHERE has_content = false`
- Top Priority: `MAX(priority) FROM seo_keywords WHERE has_content = false`

**Next up** — `keyword FROM seo_keywords WHERE has_content = false ORDER BY priority DESC LIMIT 1`

**Recent activity** — last 3 seo_posts ORDER BY published_at DESC.

**Settings** — site_url, posts_per_day, competitors, target_keywords from seo_settings.

**Error log** — seo_errors.

**Right sidebar**
- Primary: "PUBLISH NOW →" → `seo-publish`
- Secondary: "DISCOVER KEYWORDS →" → `seo-discover`

---

### GEO (/admin/geo)

**Stats grid**
- Posts Published: `COUNT(*) FROM geo_posts`
- Queries Found: `COUNT(*) FROM geo_queries`
- Cited: `COUNT(*) FROM geo_queries WHERE brand_cited = true`
- Citation Rate: cited / COUNT(*) WHERE has_content = true, shown as "%"

**Next up** — `query FROM geo_queries WHERE has_content = false ORDER BY priority DESC LIMIT 1`

**Recent activity** — last 3 geo_posts ORDER BY published_at DESC.

**Settings** — brand_name, posts_per_day, niche_topics, competitors from geo_settings.

**Error log** — geo_errors.

**Right sidebar**
- Primary: "PUBLISH NOW →" → `geo-publish`
- Secondary: "DISCOVER QUERIES →" → `geo-discover`
- Secondary: "TEST CITATIONS →" → `geo-test`

---

### Crawl (/admin/crawl)

**Stats grid**
- Active Targets: `COUNT(*) FROM crawl_targets WHERE active = true`
- Pages Crawled Today: `COUNT(*) FROM crawl_results WHERE DATE(crawled_at) = CURRENT_DATE`
- Intel Items (unactioned): `COUNT(*) FROM crawl_intel WHERE actioned = false`
- Leads Total: `COUNT(*) FROM crawl_leads`

**Next up** — next crawl target due: `name FROM crawl_targets WHERE active = true ORDER BY last_crawled ASC LIMIT 1`

**Recent activity** — last 3 crawl_intel rows ORDER BY created_at DESC — show title + intel_type.

**Settings** — brand_name, site_url, niche from crawl_settings. Show crawl_targets table inline (name, url, target_type, last_crawled, active toggle).

**Error log** — crawl_errors.

**Right sidebar**
- Primary: "CRAWL NOW →" → `crawl-run`
- Secondary: "PUBLISH INTEL →" → `crawl-publish`

---

### Perplexity (/admin/perplexity)

**Stats grid**
- Research Calls This Week: `COUNT(*) FROM perplexity_research WHERE created_at >= NOW() - INTERVAL '7 days'`
- Brand Citations: `COUNT(*) FROM perplexity_citations WHERE brand_mentioned = true`
- Citation Rate: brand_mentioned=true / total in perplexity_citations, as "%"
- Content Published: `COUNT(*) FROM perplexity_content WHERE status = 'published'`

**Next up** — `query FROM perplexity_research WHERE processed = false ORDER BY researched_at ASC LIMIT 1`

**Recent activity** — last 3 perplexity_content rows ORDER BY published_at DESC.

**Settings** — brand_name, site_url, research_topics, competitors from perplexity_settings.

**Error log** — perplexity_errors.

**Right sidebar**
- Primary: "RESEARCH NOW →" → `perplexity-research`
- Secondary: "TEST CITATIONS →" → `perplexity-test-citations`
- Secondary: "IMPROVE CONTENT →" → `perplexity-improve-content`

---

### Pay (/admin/pay)

**Stats grid**
- Revenue Today: `COALESCE(SUM(amount_cents),0)/100 FROM pay_transactions WHERE DATE(created_at) = CURRENT_DATE AND status = 'succeeded'`
- Active Subscriptions: `COUNT(*) FROM pay_subscriptions WHERE status = 'active'`
- Abandoned (unconverted): `COUNT(*) FROM pay_abandoned WHERE converted = false`
- Products: `COUNT(*) FROM pay_products WHERE active = true`

**Next up** — next pay-recover run: daily 10am UTC. Show time until next run.

**Recent activity** — last 3 pay_transactions ORDER BY created_at DESC — show amount, product, status.

**Settings** — business_name, currency, support_email, site_url from pay_settings.

**Error log** — pay_errors.

**Right sidebar**
- Primary: "OPTIMISE PRODUCTS →" → `pay-optimise`
- Secondary: "RUN RECOVERY →" → `pay-recover`

---

### Mail (/admin/mail)

**Stats grid**
- Subscribers: `COUNT(*) FROM mail_subscribers WHERE status = 'confirmed'`
- Pending Confirmation: `COUNT(*) FROM mail_subscribers WHERE status = 'pending'`
- Broadcasts Sent: `COUNT(*) FROM mail_broadcasts WHERE status = 'sent'`
- Avg Open Rate: `AVG(open_rate) FROM mail_broadcasts WHERE status = 'sent'` as "%"

**Next up** — next newsletter broadcast based on newsletter_day + time from mail_settings.

**Recent activity** — last 3 mail_broadcasts ORDER BY sent_at DESC — show subject, recipient_count, open_rate.

**Settings** — brand_name, from_email, newsletter_frequency, newsletter_day, welcome_email_enabled from mail_settings.

**Error log** — mail_errors.

**Right sidebar**
- Primary: "SEND BROADCAST →" → `mail-broadcast`
- Secondary: "OPTIMISE SEQUENCES →" → `mail-optimise`
- Secondary: "SEND TEST →" → `mail-send-test`

---

### SMS (/admin/sms)

**Stats grid**
- Active Contacts: `COUNT(*) FROM sms_contacts WHERE opted_out = false`
- Messages Sent Today: `COUNT(*) FROM sms_messages WHERE direction = 'outbound' AND DATE(sent_at) = CURRENT_DATE`
- Response Rate: `AVG(response_rate) FROM sms_sequences WHERE active = true` as "%"
- Opt-outs: `COUNT(*) FROM sms_contacts WHERE opted_out = true`

**Next up** — next sms-sequences-run: top of next hour.

**Recent activity** — last 3 sms_messages WHERE direction = 'outbound' ORDER BY sent_at DESC.

**Settings** — business_name, twilio_phone_number from sms_settings.

**Error log** — sms_errors.

**Right sidebar**
- Primary: "RUN SEQUENCES →" → `sms-sequences-run`
- Secondary: "OPTIMISE →" → `sms-optimise`

---

### Voice (/admin/voice)

**Stats grid**
- Episodes Published: `COUNT(*) FROM voice_episodes WHERE status = 'published'`
- Total Duration: `SUM(duration_seconds)/3600 FROM voice_episodes WHERE status = 'published'` shown as "[n] hrs"
- Posts Without Audio: `COUNT(*) FROM blog_posts WHERE slug NOT IN (SELECT post_slug FROM voice_episodes WHERE status = 'published')`
- Last Episode: `MAX(created_at) FROM voice_episodes`

**Next up** — oldest blog_post with no voice_episode entry.

**Recent activity** — last 3 voice_episodes ORDER BY created_at DESC — show post_title + duration_seconds.

**Settings** — podcast_title, voice_id, rss_enabled from voice_settings.

**Error log** — voice_errors.

**Right sidebar**
- Primary: "NARRATE NOW →" → `voice-narrate`
- Secondary: "VIEW RSS FEED ↗" → /voice-rss or similar

---

### Security (/admin/security)

**Stats grid**
- Security Score: latest `score` from security_scans. Large, colour-coded (#4ade80 ≥80, #c9a84c 60–79, #f87171 <60).
- Critical Open: `COUNT(*) FROM security_vulnerabilities WHERE severity = 'critical' AND status = 'open'`
- High Open: `COUNT(*) FROM security_vulnerabilities WHERE severity = 'high' AND status = 'open'`
- Last Pentest: `MAX(completed_at) FROM security_scans WHERE scan_type = 'pentest'`

**Next up** — `next_pentest_at` from security_settings.

**Recent activity** — last 3 security_vulnerabilities ORDER BY first_found_at DESC — show title, severity badge, status.

Below recent activity: inline table of security_vulnerabilities WHERE status = 'open' AND severity IN ('critical','high') — columns: title, severity badge, category, first_found_at.

**Settings** — aikido_project_id, pentest_frequency, alert_critical, alert_high from security_settings.

**Error log** — security_errors.

**Right sidebar**
- Primary: "RUN PENTEST →" → `security-scan`
- Secondary: "QUICK SCAN →" → `security-monitor`

---

### Watch (/admin/watch)

**Stats grid**
- Agents Monitored: count of known agent settings tables that exist
- Issues Open: `COUNT(*) FROM watch_issues WHERE resolved = false`
- Issues This Month: `COUNT(*) FROM watch_issues WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)`
- Last Run: `MAX(completed_at) FROM watch_runs`

**Next up** — next top of hour.

**Recent activity** — last 3 watch_issues ORDER BY created_at DESC — show agent_name, issue_title, severity badge, issue_url link.

Below: inline table of watch_issues WHERE resolved = false — columns: agent, title, severity, created_at, GitHub link, "Mark Resolved" button (sets resolved = true).

**Settings** — github_repo, error_threshold from watch_settings.

**Error log** — watch_errors.

**Right sidebar**
- Primary: "RUN NOW →" → `watch-monitor`

---

### Alert (/admin/alert)

**Stats grid**
- Alerts Today: `COUNT(*) FROM alert_log WHERE DATE(sent_at) = CURRENT_DATE`
- Failed: `COUNT(*) FROM alert_log WHERE DATE(sent_at) = CURRENT_DATE AND success = false`
- Success Rate: success / total in alert_log last 7 days, as "%"
- Last Briefing: `MAX(sent_at) FROM alert_log WHERE event_type = 'daily-briefing'`

**Next up** — next daily briefing based on `daily_briefing_time` from alert_settings.

**Recent activity** — last 5 alert_log rows ORDER BY sent_at DESC — show agent, event_type, sent_at, success badge.

**Settings** — slack_webhook_url, daily_briefing_time. Then a toggle grid for all boolean fields in alert_settings: alert_payments, alert_sms_replies, alert_posts, alert_keywords, alert_citations, alert_products, alert_streams, alert_releases, alert_errors.

**Error log** — alert_errors.

**Right sidebar**
- Primary: "SEND BRIEFING →" → `alert-briefing`
- Secondary: "SEND TEST →" → `alert-send` with test payload

---

### Fix (/admin/fix)

**Stats grid**
- PRs Opened This Month: `COUNT(*) FROM fix_improvements WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)`
- PRs Merged: `COUNT(*) FROM fix_improvements WHERE pr_status = 'merged'`
- Agents Analysed (last run): `agents_analysed FROM fix_runs ORDER BY created_at DESC LIMIT 1`
- Last Run: `MAX(completed_at) FROM fix_runs`

**Next up** — next Sunday 11pm UTC.

**Recent activity** — last 3 fix_improvements ORDER BY created_at DESC — show agent_name, improvement_description truncated, pr_url link, pr_status badge.

**Settings** — github_repo, improvement_focus from fix_settings.

**Error log** — fix_errors.

**Right sidebar**
- Primary: "RUN NOW →" → `fix-analyse`

---

### Intel (/admin/intel)

**Stats grid**
- Reports Generated: `COUNT(*) FROM intel_briefs`
- Keywords Added This Week: `SUM(keywords_added) FROM intel_runs WHERE created_at >= NOW() - INTERVAL '7 days'`
- GEO Queries Added This Week: `SUM(geo_queries_added) FROM intel_runs WHERE created_at >= NOW() - INTERVAL '7 days'`
- Last Run: `MAX(completed_at) FROM intel_runs`

**Next up** — next Monday 6am UTC.

**Recent activity** — last 3 intel_briefs ORDER BY created_at DESC — show week_of, top_performing_topic, keywords_added count.

Latest brief detail section: show full `weekly_summary`, `top_performing_topic`, first 3 items of `recommended_seo_keywords` and `recommended_geo_queries` from the most recent intel_briefs row.

**Settings** — brand_name, niche_description, auto_add_keywords toggle, auto_add_geo_queries toggle from intel_settings.

**Error log** — intel_errors.

**Right sidebar**
- Primary: "RUN NOW →" → `intel-analyse`
- Secondary: "SEED AGENTS →" → `intel-analyse` (runs with seed_only flag)

---

### Run (/admin/run) — Lazy Run orchestrator

**Stats grid**
- Active Engines: `active_engines` from run_settings — show count
- Master Status: `master_running` from run_settings — show ON/OFF badge
- Errors Today: sum of _errors tables today across all agents
- Last Orchestration: `MAX(created_at) FROM run_activity`

**Next up** — next :00 or :30 (run-orchestrator runs every 30 min).

**Recent activity** — last 10 run_activity rows ORDER BY created_at DESC — show engine, action, result badge (success/error).

**Settings** — brand_name, site_url, business_description, target_audience, support_email, active_engines (comma-separated, editable) from run_settings. master_running toggle at top.

**Error log** — run_errors.

**Right sidebar**
- Primary: "RUN NOW →" → `run-orchestrator`
- Secondary: "WEEKLY REPORT →" → `run-weekly-report`
- Secondary: "HEALTH CHECK →" → `run-health-check`

---

## Settings (/admin/settings)

### Site settings
Fields from run_settings (if installed) or a local config: site_url, brand_name, business_description, target_audience, support_email. "PROPAGATE TO ALL AGENTS →" button — on click, copies these values into every installed agent's settings table where the matching column exists.

### API keys
One section per service. Each section: service name, connection status badge (green "Connected" / red "Not configured"), password input with show/hide, "TEST CONNECTION" button that calls the relevant test edge function. Services and their test functions:
- Resend → `mail-send-test`
- Stripe → check pay_settings for stripe_secret_key presence
- Twilio → check sms_settings for twilio_account_sid presence
- ElevenLabs → check voice_settings for voice_id presence
- Aikido → `security-monitor`
- GitHub → check watch_settings/fix_settings for github_repo presence
- Slack → `alert-send` with test payload

### Weekly schedule
Read-only visual calendar. Seven columns (Mon–Sun). For each known cron job, show a pill in the correct column. Colour-coded: Content gold, Commerce green, Media blue, Dev purple, Monitor red, Intelligence amber.

Schedule to render:
- Mon 6am: SEO Discover, Intel Analyse, Run Weekly Report
- Mon/Thu 7am: GEO Discover
- Daily 5am: Perplexity Research
- Daily 6am: Crawl Publish
- Daily 8am: Alert Briefing (configurable)
- Daily 9am: Mail Broadcast (configurable day)
- Daily 10am: Pay Recover
- Daily 3am: Security Monitor
- Sun 9am: GEO Test
- Sun 10am: Perplexity Test
- Sun 11am: Pay Optimise, Mail Optimise
- Sun 12pm: SMS Optimise
- Sun 11pm: Fix Analyse
- Wed 9am: Perplexity Improve

### Version status
Table: agent name, installed version (from prompt_version in each settings table), latest version (from https://lazyunicorn.ai/api/versions), status badge (Up to date / UPDATE AVAILABLE in gold), "Get Latest Prompt ↗" link to GitHub per row. Only show agents where the settings table exists.

---

## Version checker

On mount, fetch https://lazyunicorn.ai/api/versions with 5s timeout, fail silently. Compare each installed agent's prompt_version. If any out of date: gold banner at top of main content — "Updates available for [n] agent(s) — View Updates | Dismiss". Dismiss stores dismissed version set in localStorage key lazy-version-dismissed.

---

## Interaction rules

All edge function calls: show loading spinner on button, success toast + green checkmark for 2s on success, error callout with message on failure. Never reload the page. Stats and tables refresh after function call completes. Status dots poll every 60 seconds (re-query all settings tables).

Tables: search input filtering by main text column. Pagination at 50 rows.

Settings edits: inline pencil icon per row. Clicking opens inline input with Save/Cancel. Save → UPDATE that row in the settings table. Show spinner. On success: row returns to display. On error: show error inline.

---

## Error handling

Never show a generic "failed" message. Every failure shows what went wrong and what to do.

**Agent not configured** — before rendering any agent panel, check settings table exists AND setup_complete = true. If not, show a setup card: "[Agent] is not configured. Complete setup to activate." + "SET UP [AGENT] →" button linking to /lazy-[slug]-setup. No stats, no action buttons.

**Edge function error** — red callout with actual error message, then:
- Contains "secret", "api key", "unauthorized" → "Add the required API key to Supabase secrets: Project Settings → Edge Functions → Secrets"
- Contains "not found", "does not exist" → "Re-run the setup page at /lazy-[agent]-setup"
- Other → show raw error + "View Error Log" button scrolling to error log section

**Timeout** — all data fetches have 10s timeout. On timeout: "Could not load data. Check your Supabase connection." + Retry button.

**Empty state** — agent configured but zero rows in data table → "No data yet — click [primary action] to run for the first time."

---

## Routes

/admin — overview (3-column: left nav + agent table + quick stats)
/admin/settings — site settings, API keys, schedule, version status
/admin/[slug] — agent detail page

Slugs: blogger, seo, geo, crawl, perplexity, store, drop, print, pay, mail, sms, voice, stream, youtube, code, gitlab, linear, contentful, design, auth, granola, alert, telegram, supabase, security, watch, fix, build, intel, repurpose, trend, churn, agents, run, waitlist

Client-side routing. No full page reloads. /admin/[slug] requires settings table to exist AND setup_complete = true — otherwise redirect to /lazy-[slug]-setup.

Settings table → slug mapping:
blog_settings → blogger, seo_settings → seo, geo_settings → geo, crawl_settings → crawl, perplexity_settings → perplexity, store_settings → store, drop_settings → drop, print_settings → print, pay_settings → pay, mail_settings → mail, sms_settings → sms, voice_settings → voice, stream_settings → stream, youtube_settings → youtube, code_settings → code, gitlab_settings → gitlab, linear_settings → linear, contentful_settings → contentful, design_settings → design, auth_settings → auth, granola_settings → granola, alert_settings → alert, telegram_settings → telegram, supabase_settings → supabase, security_settings → security, watch_settings → watch, fix_settings → fix, build_settings → build, intel_settings → intel, repurpose_settings → repurpose, trend_settings → trend, churn_settings → churn, agent_settings → agents, run_settings → run, waitlist_settings → waitlist
