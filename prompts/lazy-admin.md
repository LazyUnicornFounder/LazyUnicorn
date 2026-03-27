# Lazy Admin

> Category: 🚀 Unicorn · Version: 0.0.1

## Prompt

````
[LazyUnicorn Admin Dashboard Prompt — v0.0.1 — LazyUnicorn.ai]

Rebuild the entire admin dashboard at /admin from scratch. Replace everything currently there with a unified control panel for the entire LazyUnicorn autonomous operations layer. This admin detects which engines are installed by checking which database tables exist and shows only the relevant panels. It works whether one engine or all twenty are installed.

IMPORTANT: Do not change anything outside /admin. All public pages, product pages, blog posts, and the main site navigation remain exactly as they are.

---

## Design philosophy

Mission control, not a settings page. Every number is live. Every button does something immediately. Every error is visible before you have to look for it. The founder checks this for 60 seconds in the morning and knows at a glance whether everything is running, what it produced overnight, and whether anything needs attention.

Dark background matching the existing site. All text high contrast. Numbers large and readable. Status indicators immediate and unambiguous — green means running, red means broken, never any ambiguity. No unnecessary decoration. Everything earns its place.

---

## Layout

Fixed left sidebar navigation. Main content area on the right. Sidebar never scrolls away. Content area scrolls. On mobile sidebar collapses to a bottom tab bar showing only icons.

---

## Left sidebar

At the top: LazyUnicorn logo and wordmark.

Below it: master status indicator — a single large dot and label. Green dot: All systems running. Red dot: [n] engines need attention. Gold dot: Everything paused. This is the first thing the eye goes to.

Below that: vertical navigation list. Each item is an engine name with its icon. Only show engines whose settings table exists in the database — do not show uninstalled engines. Active item has a gold left border and gold text. Each item shows a small coloured dot on the right — green if running with no errors, red if errors in last 24 hours, grey if paused. Navigation order:

Overview (always show)
Category label: Content Engines — Blogger (if blog_settings exists), SEO (if seo_settings exists), GEO (if geo_settings exists), Crawl (if crawl_settings exists), Perplexity (if perplexity_settings exists)
Category label: Commerce Engines — Store (if store_settings exists), Pay (if pay_settings exists), SMS (if sms_settings exists)
Category label: Media Engines — Voice (if voice_settings exists), Stream (if stream_settings exists)
Category label: Developer Engines — Code (if code_settings exists), GitLab (if gitlab_settings exists), Linear (if linear_settings exists)
Category label: Channels — Alert (if alert_settings exists), Telegram (if telegram_settings exists), Contentful (if contentful_settings exists), Supabase (if supabase_settings exists)
Category label: Security — Security (if security_settings exists)
Settings (always show)

Below navigation: master pause button. Full sidebar width. When everything is running: Pause Everything in muted style. When paused: Resume Everything in gold. One click updates master_running in run_settings if that table exists. If run_settings does not exist toggle is_running individually across all detected engine settings tables.

---

## Overview page — loads by default at /admin

The morning dashboard. 60-second check.

Row 1 — stat cards in a horizontal row. Only show cards for data that exists. Detect and show from these sources:

Posts published today: count blog_posts + seo_posts + geo_posts published today if those tables exist.
Posts this week: same tables, last 7 days.
Active engines: count of settings tables where is_running is true, across all detected engine settings tables.
Errors today: count of rows from all detected engine error tables (blog_errors, seo_errors, geo_errors, store_errors, voice_errors, pay_errors, sms_errors, stream_errors, code_errors, gitlab_errors, linear_errors, crawl_errors, perplexity_errors, alert_errors, telegram_errors, contentful_errors, supabase_errors, security_errors, run_errors) from last 24 hours. Red background tint if above zero.
Last publish: most recent published_at across all content tables if any exist.
Security score: latest score from security_scans if security_settings exists. Green above 80, amber 60-79, red below 60. Dash if not installed.

Row 2 — engine status grid. One compact card per installed engine. Four columns on large screens, three on medium, two on small. Each card: engine name in small bold text, status dot top right, one primary metric below the name, last run time in muted text, small Run Now button. Metrics: posts today for content engines, revenue today for Pay (sum of pay_transactions amount_cents where status succeeded today divided by 100), messages sent today for SMS, episodes today for Voice, streams processed for Stream, commits processed for Code and GitLab, issues synced for Linear, intel items found today for Crawl, brand citation rate for Perplexity (brand_mentioned true divided by total in perplexity_citations), alerts sent today for Alert and Telegram, entries synced today for Contentful, milestones reached total for Supabase, current security score for Security.

Row 3 — two columns.

Left: unified activity feed. Reverse chronological list of every action across all engines in the last 24 hours. Sources: run_activity if run_settings exists, plus last published_at from each content table as synthetic activity rows labelled by engine. Each row: coloured dot (green success, red error, gold optimisation), engine name in muted small text, action description, timestamp. Maximum 50 rows. Scrollable. Filter pills: All, Errors Only, Content, Commerce, Security.

Right: error log. All errors from all engine error tables in the last 24 hours grouped by engine. Each group: engine name header in small red text, errors listed below with function name, error message truncated to 120 characters, time. If no errors: large green checkmark and text: No errors in the last 24 hours. Clear All button at top marks all as read.

---

## Individual engine pages

Each engine in the sidebar opens its own page at /admin/[engine]. All engine pages follow the same four-section layout.

Section 1 — Status bar. Full width. Left: engine name large, subtitle one sentence, status badge (Running green / Paused grey / Error red). Right: large on/off toggle updating is_running in that engine's settings table immediately. Green when running, grey when paused.

Section 2 — Quick actions. Horizontal row of buttons. Each triggers one immediate edge function without navigating away. Button shows loading spinner while running, checkmark for 2 seconds on success, then reverts. Show an error toast if the function fails.

Section 3 — Stats and queue. Two columns. Left: four to six stat cards with the most important numbers for that engine. Right: the queue or upcoming items for that engine. Maximum 20 rows with View All link if more.

Section 4 — History log. Last 50 rows of what this engine produced or processed. Columns vary by engine but always include title or description, date, status badge. For content engines include a View link. Sortable by date descending. Search input filters by title or keyword. Paginate at 50 rows.

Below Section 4 — collapsible Settings panel. Click to expand. Shows all setup form fields for that engine inline. Save Settings button updates the database. On save show a toast: Settings saved. No page reload.

Below Settings — collapsible Error log. Click to expand. Last 10 errors from that engine's error table. Clear button marks as read. Red dot on the chevron if unread errors.

---

## Engine-specific page specs

LAZY BLOGGER (/admin/blogger — only show if blog_settings exists)
Subtitle: Publishes SEO and GEO blog posts every 15 minutes.
Quick actions: Publish One Now (blog-publish), link to /lazy-blogger-setup.
Stats: Posts today, Posts this week, SEO posts total, GEO posts total, Research-grounded posts (where research_context is not ai-generated).
Queue: Show the current product in rotation — read last_product_published from blog_settings, find it in the 20-product list, and display the NEXT product as "Next up: [product name]". Show the top keyword from seo_keywords where has_content is false and product_name matches the next product, with source tag and product badge. Show the full 20-product rotation as a horizontal scrollable list of small pills with the current position highlighted in gold.
History: last 50 blog_posts with title, type tag, research badge, published date, View link.
Settings: all blog_settings fields.

LAZY SEO (/admin/seo — only show if seo_settings exists)
Subtitle: Discovers keywords and publishes ranking articles.
Quick actions: Publish SEO Post Now (seo-publish), Discover Keywords Now (seo-discover).
Stats: Posts published, Keywords discovered, Keywords with content, Keywords remaining.
Source breakdown: stat pills showing how many keywords from seo-discover vs crawl vs perplexity.
Queue: seo_keywords where has_content is false ordered by priority descending. Show keyword, priority, source tag (blue=seo-discover, orange=crawl, purple=perplexity), created date. Publish This button per row.
History: last 50 seo_posts with title, keyword, published date, View link.
Settings: all seo_settings fields.

LAZY GEO (/admin/geo — only show if geo_settings exists)
Subtitle: Publishes content cited by ChatGPT, Claude, and Perplexity.
Quick actions: Publish GEO Post Now (geo-publish), Discover Queries Now (geo-discover), Test Citations Now (geo-test).
Stats: Posts published, Queries discovered, Queries with content, Citation rate percentage.
Source breakdown: queries from geo-discover vs perplexity.
Queue: geo_queries where has_content is false ordered by priority. Show query, type tag (green=informational, gold=commercial, purple=navigational), source tag, priority. Publish This button per row.
Citation panel: last 10 geo_citations with query, brand mentioned yes/no, confidence, test method badge (simulated or real), date.
History: last 50 geo_posts with title, product badge, target query, published date, View link.
Settings: all geo_settings fields.

LAZY CRAWL (/admin/crawl — only show if crawl_settings exists)
Subtitle: Monitors competitors and feeds real intelligence into your content engines.
Quick actions: Crawl All Targets Now (crawl-run), Publish Intelligence Now (crawl-publish).
Stats: Active targets, Pages crawled today, Intel items found today, Keywords fed to SEO, Leads found total.
Queue: all crawl_targets with name, URL, type tag, frequency, last crawled, next crawl, active toggle, Crawl Now button per row.
Intelligence feed: last 20 crawl_intel rows with intel type tag, title, description, actioned badge, date.
History: last 50 crawl_results with URL, target name, crawled date, processed badge.
Settings: all crawl_settings fields plus all crawl_targets in an editable list with add/remove.

LAZY PERPLEXITY (/admin/perplexity — only show if perplexity_settings exists)
Subtitle: Researches your niche with live web data and tests brand citation rates.
Quick actions: Research Now (perplexity-research), Test Citations Now (perplexity-test-citations), Improve Content Now (perplexity-improve-content).
Stats: Research calls this week, Brand citation rate, Content published with citations, Keywords fed to SEO.
Queue: perplexity_research where processed is false. Show query, type tag, citation count, date.
Citation rate chart: line chart using recharts of brand citation rate per week for last 8 weeks.
History: last 50 perplexity_content with title, citations count badge, published date, View link.
Settings: all perplexity_settings fields.

LAZY STORE (/admin/store — only show if store_settings exists)
Subtitle: Discovers products, writes listings, optimises conversion, and runs promotions.
Quick actions: Discover Products Now (store-discover), Optimise Listings Now (store-optimise), Run Promotions Now (store-promote), Publish Content Now (store-content).
Stats: Products listed, Active promotions, Average conversion rate, Content published.
Queue: store_products where description is null or empty. Show name, category, price, date, Write Listing button calling store-listings for that product.
History: last 50 store_products ordered by created_at with name, price, views, sales, conversion rate, last optimised, promotion badge.
Settings: all store_settings fields.

LAZY PAY (/admin/pay — only show if pay_settings exists)
Subtitle: Stripe payments with self-improving conversion optimisation.
Quick actions: Optimise Now (pay-optimise), Run Recovery Now (pay-recover).
Stats: MRR, Total revenue, Active subscribers, Abandoned checkouts, Recovery rate.
Queue: pay_abandoned where recovery_email_sent is false and converted is false. Show customer email, product, abandoned time, Send Recovery button.
Optimisation log: last 10 pay_optimisation_log rows with product name, old conversion rate, new description preview, date.
History: last 50 pay_transactions with customer email, product, amount, status badge, date.
Settings: all pay_settings fields (not Stripe keys — those update via the Settings page).

LAZY SMS (/admin/sms — only show if sms_settings exists)
Subtitle: Automated SMS sequences that improve themselves.
Quick actions: Run Sequences Now (sms-sequences-run), Optimise Messages Now (sms-optimise).
Stats: Messages sent today, Delivery rate, Response rate, Opted-out contacts, Active sequences.
Queue: all sms_sequences with name, trigger, delay, template, sends, responses, response rate, last optimised, active toggle. Optimise This button on sequences with response rate below 5%.
History: last 50 sms_messages with direction badge, phone number, message type, status badge, sent time.
Settings: all sms_settings fields.

LAZY VOICE (/admin/voice — only show if voice_settings exists)
Subtitle: Narrates every post in your ElevenLabs voice automatically.
Quick actions: Generate Audio Now (voice-narrate), View RSS Feed (links to voice-rss function URL).
Stats: Episodes generated, Total audio hours, Episodes this week, Posts without audio.
Queue: posts from blog_posts, seo_posts, geo_posts with no matching voice_episodes row. Show title, type, published date, Narrate Now button.
History: last 50 voice_episodes with title, source table badge, duration, published date, Play button.
Settings: all voice_settings fields (not ElevenLabs API key — that updates via Settings page).

LAZY STREAM (/admin/stream — only show if stream_settings exists)
Subtitle: Turns every Twitch stream into blog posts, SEO articles, and highlights.
Quick actions: Process Last Stream Now (stream-process for most recent ended session), Optimise Content Now (stream-optimise).
Stats: Streams processed, Content published, Clips saved, Average views per piece. Live status badge: green dot Currently Live or Last stream date.
Queue: stream_sessions where status is ended and not yet processed. Show title, game, ended date, Process Now button.
History: last 50 stream_content with title, content type tag, stream it came from, published date, views, View link.
Settings: all stream_settings fields.

LAZY CODE (/admin/code — only show if code_settings exists)
Subtitle: Turns every GitHub commit into changelogs and developer blog posts.
Quick actions: Sync Roadmap Now (code-sync-roadmap), Optimise Content Now (code-optimise).
Stats: Commits processed, Content published, Open roadmap items, Completed roadmap items, Last webhook received.
Queue: code_commits where processed is false ordered by committed_at descending. Show sha (7 chars), plain English summary, significance badge, author, date.
History: last 50 code_content with title, content type badge, published date, views, View link.
Settings: all code_settings fields.

LAZY GITLAB (/admin/gitlab — only show if gitlab_settings exists)
Subtitle: Turns every GitLab commit and merge request into changelogs and developer posts.
Quick actions: Sync Roadmap Now (gitlab-sync-roadmap), Optimise Content Now (gitlab-optimise).
Stats: Commits processed, MRs processed, Content published, Open roadmap items, Last webhook received.
Queue: gitlab_commits where processed is false. Show sha (7 chars), summary, significance badge, author, date.
History: last 50 gitlab_content with title, type badge, published date, views, View link.
Settings: all gitlab_settings fields.

LAZY LINEAR (/admin/linear — only show if linear_settings exists)
Subtitle: Turns Linear cycles and issues into product updates and changelogs.
Quick actions: Sync Now (linear-sync-all), Velocity Report Now (linear-velocity-report), Optimise Now (linear-optimise).
Stats: Issues synced, Cycles completed, Content published, Last sync time.
Queue: linear_cycles where completed_at is not null and processed is false. Show cycle name, number, completion date, issues completed count, Write Summary button.
History: last 50 linear_content with title, type badge, published date, views, View link.
Settings: all linear_settings fields.

LAZY ALERT (/admin/alert — only show if alert_settings exists)
Subtitle: Real-time Slack alerts for every engine event.
Quick actions: Send Test Message, Send Briefing Now (alert-briefing).
Stats: Alerts sent today, Alerts this week, Success rate, Last alert sent time.
Toggle grid: all alert_settings boolean toggles as labelled on/off switches. Updates in real time, no save button.
History: last 50 alert_log rows with engine badge, event type, message preview, sent time, success badge.
Settings: all alert_settings fields.

LAZY TELEGRAM (/admin/telegram — only show if telegram_settings exists)
Subtitle: Real-time Telegram alerts and bot commands for every engine.
Quick actions: Send Test Message, Send Briefing Now (telegram-briefing), Register Webhook (calls Telegram setWebhook API).
Stats: Messages sent today, Messages this week, Success rate, Last message time.
Toggle grid: all telegram_settings boolean toggles.
Webhook status: show current webhook URL and a Registered / Not Registered badge.
History: last 50 telegram_log rows with engine badge, event type, message preview, sent time, success badge.
Settings: all telegram_settings fields.

LAZY CONTENTFUL (/admin/contentful — only show if contentful_settings exists)
Subtitle: Two-way content sync between your Lovable site and Contentful.
Quick actions: Pull from Contentful Now (contentful-pull), Push to Contentful Now (contentful-push).
Stats: Entries pulled from Contentful, Posts pushed to Contentful, Last pull time, Last push time, Sync failures today.
Queue: contentful_sync_log where status is failed. Show direction badge, entry title, error, date, Retry button.
History: last 50 contentful_sync_log rows with direction badge, type, entry title, status badge, time.
Settings: all contentful_settings fields.

LAZY SUPABASE (/admin/supabase — only show if supabase_settings exists)
Subtitle: Monitors database milestones and publishes product update posts.
Quick actions: Check Now (supabase-monitor), Send Report Now (supabase-weekly-report).
Stats: Current user count, Signups today, Milestones reached total, Content published, Last check time.
Queue: supabase_milestones where post_published is false. Show type, value, reached date, Publish Post button.
History: last 50 supabase_milestones with type, value, reached date, post published badge.
Settings: all supabase_settings fields.

LAZY SECURITY (/admin/security — only show if security_settings exists)
Subtitle: Automated Aikido pentests and continuous vulnerability monitoring.
Quick actions: Run Pentest Now (security-scan), Run Quick Scan (security-monitor).
Stats: Current security score (large, colour coded green/amber/red), Open critical vulnerabilities (red if above zero), Open high vulnerabilities (orange if above zero), Last pentest date, Next pentest date.
Open vulnerabilities: always visible if any critical or high issues are open — not collapsible. Show severity badge, title, category, first found date, remediation hint, Mark Fixed button. If none: green banner No critical or high vulnerabilities open.
History: last 50 security_scans with date, type badge, status badge, score, critical count, high count, View Report button showing the matching security_reports in a modal.
Settings: all security_settings fields except the Aikido API key — that updates via the main Settings page.

---

## Settings page (/admin/settings)

Three sections.

Site settings: site URL, brand name, business description, support email. These update run_settings if that table exists, and if not update each detected engine settings table that has those fields. A Propagate to All Engines button pushes updated values to all engine settings tables simultaneously.

API keys: one section per service. Show only services whose engine is installed (detected by settings table). Each section: service name, connection status badge (Connected green if secret exists / Not connected grey), password input to update the key, show/hide eye toggle, Test Connection button that verifies the key works. On success: Connected badge for 3 seconds. On failure: error message in red. Services to show if installed: ElevenLabs (test by fetching voices list), Stripe (test by fetching account), Twilio (test by fetching account info), Twitch (test by fetching public stream), GitHub (test by fetching user profile), GitLab (test by fetching user profile), Linear (test by fetching team info), Firecrawl (test by fetching account info), Perplexity (test with a simple completion), Aikido (test by fetching project list), Slack (test by posting to webhook), Telegram (test by fetching bot info), Contentful (test by fetching space info), Supabase service role (test by fetching table list).

Weekly schedule: a read-only visual timeline showing the full weekly publishing cadence. Seven columns, one per day. Each column shows scheduled runs as stacked time blocks. Each block shows engine name and function. Colour coded by category: content engines gold, commerce green, media blue, developer purple, channels grey, security red. Build this from the cron schedules defined in each installed engine rather than hardcoding — read the cron expressions and render them as human-readable time blocks.

---

## Interaction rules

Every action that calls an edge function shows a loading spinner on the button. On success: green checkmark for 2 seconds and a success toast bottom right. On failure: red X and error toast with the message. Never reload the page. Never navigate away. Tables refresh automatically after a function completes. Sidebar error dots poll every 60 seconds.

Every table with more than 50 rows shows pagination — Previous and Next buttons with current page and total. Every table has a search input that filters visible rows by the most relevant text field.

---

## Routes

/admin — Overview page (default)
/admin/blogger, /admin/seo, /admin/geo, /admin/crawl, /admin/perplexity
/admin/store, /admin/pay, /admin/sms
/admin/voice, /admin/stream
/admin/code, /admin/gitlab, /admin/linear
/admin/alert, /admin/telegram, /admin/contentful, /admin/supabase
/admin/security
/admin/settings

Use client-side routing. Direct linking to any route works correctly. Navigating between pages does not trigger a full page reload. Sidebar highlights the active route. Only show routes for installed engines.

---

## Version checker

Add a PromptVersionChecker component that mounts at the top of every admin page.

On mount fetch https://lazyunicorn.ai/api/versions with a 5-second timeout. If the fetch fails silently exit — never show an error, never block the page.

For each installed engine query its settings table for the prompt_version field. Compare each installed version against the API response. An engine is out of date if its installed version is numerically lower — compare by splitting on dots and comparing each segment as an integer.

If all engines are up to date render nothing.

If one or more engines are out of date render a gold banner at the very top of the admin above the sidebar content area. Left side: update icon and text Updates available for [n] engine[s]. Right side: View Updates button and Dismiss button.

Clicking View Updates opens a slide-out panel from the right. One row per out-of-date engine showing: engine name, installed version in a grey badge, latest version in a gold badge with up arrow, upgrade_complexity badge from the API (drop-in=green, setup-required=amber, breaking=red), View Changelog button linking to https://lazyunicorn.ai/changelog, Get Latest Prompt button linking to https://lazyunicorn.ai/downloads/[engine-slug]-prompt.txt.

Below the list: "Drop-in updates can be pasted directly. Setup-required updates need a visit to the engine setup page after pasting. Breaking updates require following the upgrade instructions on the changelog."

Dismiss stores the dismissed versions in localStorage under the key lazy-version-dismissed as a JSON object of engine slug to dismissed version string. The banner reappears when a newer version is released.

On the /admin/settings page add a Version Status section above the API keys section. Show a table: Engine, Installed Version, Latest Version, Status badge (Up to date green / Update available gold / Unknown grey). A Check for Updates button re-fetches the API. A Last checked timestamp below the button.

On each individual engine page /admin/[engine] add a small version badge in the Section 1 status bar next to the engine name showing the installed prompt_version in muted grey. If an update is available change the badge to gold and show: Installed: [old] → [new] available. Clicking the badge opens the slide-out panel filtered to that engine.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
