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

## Agent detail page

Reached by clicking MANAGE → on any installed agent card. URL: /admin/[agent-slug]. Back button returns to /admin.

### Header
Full-width. Agent name in large caps, subtitle in muted text, status dot + label, ON/OFF toggle (updates is_running in that agent's settings table).

### Two-column layout — equal width

**Left column — Status**

2×2 stat grid showing the 4 most meaningful metrics for that agent. Use large numbers, muted labels in caps.

Below the stat grid: "NEXT UP" section showing what the agent will do on its next run (next product in rotation for Blogger, next keyword for SEO, next scheduled pentest for Security, etc.).

Below that: last 3 activity rows (most recent actions) with timestamps and external links where applicable (e.g. link to blog post, GitHub issue, YouTube video).

**Right column — Actions**

Primary action button: gold fill, full width, uppercase with arrow (e.g. "PUBLISH NOW →", "RUN PENTEST →", "SYNC NOW →").

Secondary action buttons: ghost style, full width, for less common actions (e.g. "VIEW ALL POSTS ↗", "DISCOVER KEYWORDS →").

Settings section: key/value rows, each with an inline edit pencil icon. Clicking the pencil makes the value editable inline and shows Save/Cancel. No separate settings page. Settings shown: the most important 3–5 fields from that agent's settings table.

Error log section: collapsed by default with a toggle. When expanded shows the last 10 rows from that agent's _errors table ordered by created_at descending. When no errors: "No errors in the last 24 hours" in muted text. Clear button removes all rows from the _errors table.

### Per-agent metrics and actions

Blogger — Stats: posts today, posts this week, SEO posts total, GEO posts total. Next up: next product in rotation + top unwritten keyword. Primary action: PUBLISH NOW (blog-publish). Secondary: VIEW ALL POSTS.

SEO — Stats: posts published, keywords found, keywords remaining, avg position. Next up: top unused keyword. Primary action: PUBLISH NOW (seo-publish). Secondary: DISCOVER KEYWORDS (seo-discover).

GEO — Stats: posts published, queries found, citation rate, queries remaining. Primary action: PUBLISH NOW (geo-publish). Secondary: DISCOVER QUERIES (geo-discover), TEST CITATIONS (geo-test).

Crawl — Stats: active targets, pages crawled today, intel items today, leads total. Primary action: CRAWL NOW (crawl-run). Secondary: PUBLISH INTEL (crawl-publish).

Perplexity — Stats: research calls this week, brand citation rate, content published. Primary action: RESEARCH NOW (perplexity-research). Secondary: TEST CITATIONS (perplexity-test-citations).

Contentful — Stats: entries pulled, posts pushed, last pull, sync failures today. Primary action: PULL NOW (contentful-pull). Secondary: PUSH NOW (contentful-push).

Store — Stats: products listed, active promotions, avg conversion rate, content published. Primary action: DISCOVER (store-discover). Secondary: OPTIMISE (store-optimise), PROMOTE (store-promote).

Drop — Stats: products synced, content published, last sync time. Primary action: SYNC NOW (drop-sync). Secondary: PUBLISH CONTENT (drop-content).

Print — Stats: products synced, content published, last sync time. Primary action: SYNC NOW (print-sync). Secondary: PUBLISH CONTENT (print-content).

Pay — Stats: MRR, total revenue, active subscribers, abandoned checkouts. Primary action: OPTIMISE NOW (pay-optimise). Secondary: RUN RECOVERY (pay-recover).

SMS — Stats: sent today, delivery rate, response rate, opted out. Primary action: RUN SEQUENCES (sms-sequences-run). Secondary: OPTIMISE (sms-optimise).

Mail — Stats: campaigns sent this month, subscribers, avg open rate, avg click rate. Primary action: SEND CAMPAIGN (mail-campaign). Secondary: OPTIMISE (mail-optimise).

Voice — Stats: episodes generated, audio hours total, posts without audio. Primary action: NARRATE NOW (voice-narrate).

Stream — Stats: streams processed, content published, clips saved. Primary action: PROCESS LAST STREAM (stream-process).

YouTube — Stats: videos processed, content published, comments extracted. Primary action: SYNC NOW (youtube-sync). Secondary: FETCH COMMENTS (youtube-extract-comments).

Code — Stats: commits processed, content published, open roadmap items. Primary action: SYNC ROADMAP (code-sync-roadmap).

GitLab — Stats: commits processed, MRs processed, content published. Primary action: SYNC ROADMAP (gitlab-sync-roadmap).

Linear — Stats: issues synced, cycles completed, content published. Primary action: SYNC NOW (linear-sync-all). Secondary: VELOCITY REPORT (linear-velocity-report).

Design — Stats: last upgrade date, components updated, design version. Primary action: RUN UPGRADE (design-upgrade).

Auth — Stats: total users, signups today, signups this week, admins. Primary action: none — show user table inline (user_profiles — email, name, role badge, joined, onboarded badge, edit role inline).

Granola — Stats: meetings synced, content published, last sync. Primary action: SYNC NOW (granola-sync). Secondary: PUBLISH CONTENT (granola-publish).

Alert — Stats: alerts today, this week, success rate, last alert time. Primary action: SEND TEST. Secondary: BRIEFING NOW (alert-briefing). Show toggle grid for all alert_settings boolean fields.

Telegram — Stats: messages today, this week, success rate, webhook status. Primary action: SEND TEST. Secondary: BRIEFING NOW (telegram-briefing), REGISTER WEBHOOK. Show toggle grid for all telegram_settings boolean fields.

Supabase — Stats: current users, signups today, milestones reached, content published. Primary action: CHECK NOW (supabase-monitor). Secondary: WEEKLY REPORT (supabase-weekly-report).

Security — Stats: security score (large, colour-coded), open critical, open high, last pentest. Primary action: RUN PENTEST (security-scan). Secondary: QUICK SCAN (security-monitor). Show vulnerabilities table if any critical/high open.

Watch — Stats: agents monitored, issues opened this month, issues resolved, last run. Primary action: RUN NOW (watch-monitor). Show open issues table inline.

Fix — Stats: PRs opened this month, improvements merged, last run. Primary action: RUN NOW (fix-analyse). Show improvements table inline.

Build — Stats: agents built total, last build date. Primary action: BUILD NEW AGENT (build-engine).

Intel — Stats: reports generated, topics seeded this week, last report date. Primary action: RUN NOW (intel-weekly). Secondary: SEED AGENTS (intel-seed).

Repurpose — Stats: jobs run this week, output pieces created, source posts repurposed. Primary action: RUN NOW (repurpose-run).

Trend — Stats: topics found this week, seeded to SEO, seeded to GEO. Primary action: SCAN NOW (trend-scan). Secondary: SEED AGENTS (trend-seed).

Churn — Stats: signals detected this week, actions triggered, users retained, churn rate. Primary action: ANALYSE NOW (churn-analyse).

Agents — Stats: issues opened, PRs opened, improvements merged, last run. Primary action: RUN ALL NOW. Show 4 sub-agent status cards (error-monitor, prompt-improver, agent-writer, performance-intel).

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

All edge function calls: loading spinner on button, success toast + green checkmark for 2 seconds. Never reload the page. Stats and tables refresh after function completes. Status dots poll every 60 seconds.

All tables: search input filtering by main text field. Pagination at 50 rows with Previous/Next.

Settings edits: inline pencil icon per row. On click, value becomes an input. Save button updates the settings table row. Cancel reverts. Show saving spinner. Success: row returns to read mode. Error: show error inline.

---

## Error handling — global rules

Never show a generic "failed" message anywhere in admin. Every failure must show what went wrong and exactly what to do next.

**Agent not configured**
Before rendering any agent panel, check if its settings table exists and setup_complete is true. If not, replace the entire panel with a setup card:
- Title: "[Agent Name] is not configured"
- Message: "Complete setup to activate this agent."
- Button: "SET UP [AGENT NAME] →" linking to /lazy-[agent]-setup
- Do not show action buttons, stats, or history

**Edge function call fails**
When a button triggers an edge function and it returns an error, show a red callout with the actual error message. Below it show a "How to fix" section:
- If the error contains "secret", "api key", or "unauthorized": "Add the required API key to your Supabase secrets — Project Settings → Edge Functions → Secrets"
- If the error contains "not found" or "does not exist": "Check that all database tables were created. Re-run the setup page."
- If the error contains "setup_complete": "Complete the setup page first."
- For all other errors: show the raw error and a "View Error Log" button that scrolls to the error log section

**Missing secrets**
Each agent detail page that requires external API keys shows a Requirements section at the top of the right column. For each required secret: green checkmark if the last function call succeeded, red warning with the exact secret name and a link to Supabase secrets settings if it failed due to that secret being missing.

**Empty states**
If an agent is configured but has never run: "No data yet — click [primary action button] to run your first check."

**Spinner with no resolution**
Never show an indefinite spinner. All data fetches must have a 10 second timeout. On timeout show: "Could not load data. Check your Supabase connection." with a Retry button.

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