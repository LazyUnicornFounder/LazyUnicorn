[Lazy Run Prompt — v0.0.11 — LazyUnicorn.ai]

Add a complete unified autonomous operations runtime called Lazy Run to this project. Lazy Run installs and manages all Lazy engines from a single setup prompt, a single dashboard, and a unified scheduling and monitoring system. Install only the engines the user activates during setup.

---

## IMPORTANT: Function naming

All edge functions must use these exact names. Lazy Run calls them by these names.

| Engine | Functions |
|--------|----------|
| Blogger | blog-publish |
| SEO | seo-discover, seo-publish |
| GEO | geo-discover, geo-publish, geo-test |
| Store | store-discover, store-listings, store-prices, store-promote, store-optimise, store-content |
| Voice | voice-narrate, voice-rss |
| Pay | pay-checkout, pay-webhook, pay-optimise, pay-recover, pay-portal |
| SMS | sms-send, sms-receive, sms-status, sms-sequences-run, sms-optimise |
| Stream | stream-monitor, stream-process, stream-write-content, stream-optimise |
| YouTube | youtube-sync, youtube-process, youtube-fetch-transcript, youtube-write-transcript, youtube-write-seo, youtube-write-geo, youtube-write-summary, youtube-generate-chapters, youtube-extract-comments, youtube-track-performance |
| Code | github-webhook, code-sync-roadmap, code-write-content, code-optimise |
| GitLab | gitlab-webhook, gitlab-sync-roadmap, gitlab-write-content, gitlab-optimise |
| Linear | linear-sync-all, linear-write-content, linear-velocity-report, linear-optimise |
| Crawl | crawl-run, crawl-extract, crawl-publish |
| Perplexity | perplexity-research, perplexity-feed-engines, perplexity-test-citations, perplexity-improve-content |
| Alert | alert-send, alert-monitor, alert-briefing, alert-command |
| Telegram | telegram-send, telegram-monitor, telegram-briefing, telegram-command |
| Contentful | contentful-pull, contentful-webhook, contentful-push |
| Supabase | supabase-monitor, supabase-publish-milestone, supabase-weekly-report |
| Security | security-scan, security-poll, security-alert, security-generate-report, security-monitor |
| Auth | auth-setup |
| Design | design-upgrade |
| Granola | granola-sync, granola-publish |
| Drop | drop-sync, drop-content, drop-optimise |
| Print | print-sync, print-content, print-optimise |
| Mail | mail-send, mail-campaign, mail-optimise |
| Churn | churn-analyse, churn-trigger |
| Repurpose | repurpose-run |
| Trend | trend-scan, trend-seed |
| Intel | intel-weekly, intel-seed |
| Watch | watch-monitor |
| Fix | fix-analyse, fix-improve |
| Build | build-engine |
| Agents | agent-error-monitor, agent-prompt-improver, agent-engine-writer, agent-performance-intel |
| Run | run-orchestrator, run-weekly-report, run-health-check |

---

## IMPORTANT: API key storage

ALL API keys must be stored as Supabase secrets. Never in database tables.
Reference in edge functions via Deno.env.get().

Required secrets by engine:
- Blogger/SEO/GEO/Store: none (uses built-in Lovable AI)
- Voice: ELEVENLABS_API_KEY
- Pay: STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET
- SMS: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
- Stream: TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET
- YouTube: YOUTUBE_API_KEY, SUPADATA_API_KEY
- Code: GITHUB_TOKEN, GITHUB_WEBHOOK_SECRET
- GitLab: GITLAB_TOKEN, GITLAB_WEBHOOK_SECRET
- Linear: LINEAR_API_KEY
- Crawl: FIRECRAWL_API_KEY
- Perplexity: PERPLEXITY_API_KEY
- Alert: SLACK_SIGNING_SECRET
- Telegram: TELEGRAM_BOT_TOKEN
- Contentful: CONTENTFUL_DELIVERY_TOKEN, CONTENTFUL_MANAGEMENT_TOKEN, CONTENTFUL_WEBHOOK_SECRET
- Supabase monitoring: SUPABASE_SERVICE_ROLE_KEY
- Security: AIKIDO_API_KEY
- Auth: none (uses Lovable built-in AI)
- Design: none (uses Lovable built-in AI)
- Granola: GRANOLA_API_KEY
- Drop: AUTODS_API_KEY, AUTODS_STORE_ID
- Print: PRINTFUL_API_KEY
- Mail: RESEND_API_KEY
- Churn: none (uses Lovable built-in AI)
- Repurpose: none (uses Lovable built-in AI)
- Trend: none (uses Lovable built-in AI)
- Intel: none (uses Lovable built-in AI)
- Watch: GITHUB_TOKEN (repo scope), GITHUB_REPO
- Fix: GITHUB_TOKEN (repo scope), GITHUB_REPO
- Build: GITHUB_TOKEN (repo scope), GITHUB_REPO
- Agents: GITHUB_TOKEN (repo scope), GITHUB_REPO

---

## 1. Database

Create these Supabase tables with RLS enabled:

**run_settings**
id (uuid, primary key, default gen_random_uuid()),
site_url (text),
brand_name (text),
business_description (text),
target_audience (text),
support_email (text),
active_engines (text),
master_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
created_at (timestamptz, default now())

**run_activity**
id (uuid, primary key, default gen_random_uuid()),
engine (text),
action (text),
result (text),
details (text),
created_at (timestamptz, default now())

**run_performance**
id (uuid, primary key, default gen_random_uuid()),
engine (text),
metric_name (text),
metric_value (numeric),
recorded_at (timestamptz, default now())

**run_errors**
id (uuid, primary key, default gen_random_uuid()),
engine (text),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

Also create all database tables for each activated engine using these exact table names. Every engine settings table must include a prompt_version (text, nullable) field in addition to the standard fields. Set the prompt_version value when seeding each engine settings table in step 4 of the setup submit using the current version strings from SPEC.md.

Blogger: blog_settings, blog_posts, blog_errors
SEO: seo_settings, seo_posts, seo_keywords (add source field: text), seo_errors
GEO: geo_settings, geo_posts, geo_queries (add source field: text), geo_citations, geo_errors
Store: store_settings, store_products, store_promotions, store_content, store_errors
Voice: voice_settings, voice_episodes, voice_errors
Pay: pay_settings, pay_products, pay_customers, pay_transactions, pay_subscriptions, pay_abandoned, pay_optimisation_log, pay_errors
SMS: sms_settings, sms_contacts, sms_messages, sms_sequences, sms_optouts, sms_optimisation_log, sms_errors
Stream: stream_settings, stream_sessions, stream_content, stream_clips, stream_transcripts, stream_optimisation_log, stream_errors
YouTube: youtube_settings, youtube_videos, youtube_content, youtube_comments, youtube_intelligence, youtube_performance, youtube_errors
Code: code_settings, code_commits, code_releases, code_content, code_roadmap, code_optimisation_log, code_errors
GitLab: gitlab_settings, gitlab_commits, gitlab_merge_requests, gitlab_releases, gitlab_content, gitlab_roadmap, gitlab_optimisation_log, gitlab_errors
Linear: linear_settings, linear_issues, linear_cycles, linear_projects, linear_content, linear_optimisation_log, linear_errors
Crawl: crawl_settings, crawl_targets, crawl_results, crawl_intel, crawl_leads, crawl_errors
Perplexity: perplexity_settings, perplexity_research, perplexity_citations, perplexity_content, perplexity_errors
Alert: alert_settings, alert_log, alert_errors
Telegram: telegram_settings, telegram_log, telegram_errors
Contentful: contentful_settings, contentful_entries, contentful_sync_log, contentful_errors
Supabase monitoring: supabase_settings, supabase_snapshots, supabase_milestones, supabase_content, supabase_errors
Security: security_settings, security_scans, security_vulnerabilities, security_reports, security_errors
Agents: agent_settings, agent_runs, agent_issues, agent_improvements, agent_errors
Auth: auth_settings, auth_errors
Design: design_settings, design_errors
Granola: granola_settings, granola_meetings, granola_content, granola_errors
Drop: drop_settings, drop_products, drop_content, drop_errors
Print: print_settings, print_products, print_content, print_errors
Mail: mail_settings, mail_campaigns, mail_subscribers, mail_errors
Churn: churn_settings, churn_signals, churn_actions, churn_errors
Repurpose: repurpose_settings, repurpose_jobs, repurpose_output, repurpose_errors
Trend: trend_settings, trend_topics, trend_content, trend_errors
Intel: intel_settings, intel_reports, intel_seeds, intel_errors
Watch: watch_settings, watch_runs, watch_issues, watch_errors
Fix: fix_settings, fix_runs, fix_improvements, fix_errors
Build: build_settings, build_runs, build_engines, build_errors

Create only the tables for engines the user activates.

---

## 2. Setup page

Create a multi-step setup page at /lazy-run-setup.

**Step 1 — Welcome**
Show: "Welcome to Lazy Run. In the next 5 minutes you will set up the autonomous operations layer for your Lovable site. After setup your site will publish content, rank on Google, appear in AI answers, take payments, text customers, and more — automatically, forever."
Next button.

**Step 2 — Choose engines**
Show engine cards grouped by category. Each card shows engine name, one-line description, and an on/off toggle. Default content engines on (Blogger, SEO, GEO). All others default off.

Group: Content Engines
- Lazy Blogger: Publishes SEO and GEO blog posts automatically every 15 minutes
- Lazy SEO: Discovers keywords and publishes ranking articles
- Lazy GEO: Publishes content cited by ChatGPT and Perplexity
- Lazy Crawl: Monitors competitors and feeds real intelligence into your content engines
- Lazy Perplexity: Researches your niche with live web data and tests brand citation rates
- Lazy Repurpose: Repurposes your existing content into new formats automatically
- Lazy Trend: Discovers trending topics and seeds your content engines with timely ideas

Group: Commerce Engines
- Lazy Store: Discovers products, writes listings, optimises conversion
- Lazy Pay: Installs Stripe with self-improving conversion optimisation
- Lazy SMS: Sends automated texts via Twilio that improve themselves
- Lazy Drop: Syncs products from AutoDS and publishes optimised dropshipping content
- Lazy Print: Syncs products from Printful and publishes print-on-demand content
- Lazy Mail: Sends automated email campaigns via Resend that improve themselves
- Lazy Churn: Detects churn signals and triggers automatic retention actions

Group: Media Engines
- Lazy Voice: Narrates every post in your voice via ElevenLabs
- Lazy Stream: Turns every Twitch stream into blog posts and SEO content
- Lazy YouTube: Monitors your YouTube channel and turns every video into a transcript, SEO article, GEO article, summary, and chapter markers — plus extracts comment intelligence

Group: Developer Engines
- Lazy Code: Turns every GitHub commit into a changelog and developer post
- Lazy GitLab: Turns every GitLab commit into a changelog and developer post
- Lazy Linear: Turns Linear issues and cycles into changelogs and product updates
- Lazy Auth: Adds secure authentication to your Lovable site with Supabase Auth
- Lazy Design: Upgrades your site's visual design and component library automatically
- Lazy Granola: Syncs meeting notes from Granola and publishes insights as content

Group: Channels
- Lazy Alert: Real-time Slack alerts for every engine event
- Lazy Telegram: Real-time Telegram alerts and bot commands for every engine
- Lazy Contentful: Two-way content sync between your Lovable site and Contentful
- Lazy Supabase: Monitors database milestones and publishes product update posts

Group: Security
- Lazy Security: Runs automated Aikido pentests, tracks vulnerabilities, and generates audit-ready reports

Group: Autonomous Agents
- Lazy Watch: Monitors all agent error tables every hour and opens GitHub issues with AI diagnosis
- Lazy Fix: Reads agent performance data every Sunday and opens GitHub PRs with prompt improvements
- Lazy Build: Writes and deploys new Lazy engines from a spec using Lovable AI
- Lazy Intel: Generates weekly competitive intelligence reports and seeds your content engines
- Lazy Agents: Four autonomous agents that monitor errors, improve prompts, write new engines, and generate weekly performance intelligence — all via GitHub PRs and issues

Below the cards show which API keys each selected engine requires.
Next button.

**Step 3 — Core settings**
Fields:
- Site URL
- Brand name
- Business description
- Target audience
- Support email

Include Suggest buttons that auto-fill related fields using the built-in Lovable AI.
Next button.

**Step 4 — API keys**
Show only the fields required by engines selected in step 2. Group by service:

Content engines: show note "Lazy Blogger, SEO, GEO, and Store use Lovable's built-in AI — no API key required."

Firecrawl section (if Lazy Crawl active): Firecrawl API key — stored as FIRECRAWL_API_KEY secret.

Perplexity section (if Lazy Perplexity active): Perplexity API key — stored as PERPLEXITY_API_KEY secret.

ElevenLabs section (if Lazy Voice active): API key stored as ELEVENLABS_API_KEY, Voice ID (default EXAVITQu4vr4xnSDxMaL).

Stripe section (if Lazy Pay active): Publishable Key as STRIPE_PUBLISHABLE_KEY, Secret Key as STRIPE_SECRET_KEY, Webhook Secret as STRIPE_WEBHOOK_SECRET.

Twilio section (if Lazy SMS active): Account SID as TWILIO_ACCOUNT_SID, Auth Token as TWILIO_AUTH_TOKEN, Phone Number.

Twitch section (if Lazy Stream active): Client ID as TWITCH_CLIENT_ID, Client Secret as TWITCH_CLIENT_SECRET, Username.

YouTube section (if Lazy YouTube active): YouTube API key — from Google Cloud Console with YouTube Data API v3 enabled. Stored as YOUTUBE_API_KEY. Supadata API key — from supadata.ai for transcript extraction. Stored as SUPADATA_API_KEY. YouTube Channel ID (starts with UC).

GitHub section (if Lazy Code active): Personal Access Token as GITHUB_TOKEN, Webhook Secret as GITHUB_WEBHOOK_SECRET, Username, Repository.

GitLab section (if Lazy GitLab active): Personal Access Token as GITLAB_TOKEN, Webhook Secret as GITLAB_WEBHOOK_SECRET, Username, Project path.

Linear section (if Lazy Linear active): API Key as LINEAR_API_KEY, Team ID.

Slack section (if Lazy Alert active): Slack Webhook URL, Signing Secret as SLACK_SIGNING_SECRET.

Telegram section (if Lazy Telegram active): Bot Token as TELEGRAM_BOT_TOKEN, Chat ID.

Contentful section (if Lazy Contentful active): Space ID, Delivery Token as CONTENTFUL_DELIVERY_TOKEN, Management Token as CONTENTFUL_MANAGEMENT_TOKEN, Webhook Secret as CONTENTFUL_WEBHOOK_SECRET.

Supabase monitoring section (if Lazy Supabase active): Project URL, Service Role Key as SUPABASE_SERVICE_ROLE_KEY.

Aikido section (if Lazy Security active):
- Aikido API key (password) — get at aikido.dev. Stored as AIKIDO_API_KEY secret.
- Aikido Project ID (text) — find in your Aikido project settings.
- Pentest frequency (select: Weekly / Monthly / Quarterly / Manual only)

AutoDS section (if Lazy Drop active): AutoDS API key stored as AUTODS_API_KEY, AutoDS Store ID stored as AUTODS_STORE_ID.

Printful section (if Lazy Print active): Printful API key stored as PRINTFUL_API_KEY.

Resend section (if Lazy Mail active): Resend API key stored as RESEND_API_KEY, From email address, From name.

Granola section (if Lazy Granola active): Granola API key stored as GRANOLA_API_KEY.

GitHub repo section (if Lazy Watch, Fix, or Build active): GitHub personal access token with repo scope — stored as GITHUB_TOKEN (reused if already set by Lazy Code). GitHub repo in format username/reponame — stored in each engine's settings table. Error threshold for Watch (number, default 3). Slack webhook URL (optional, from Lazy Alert settings).

Agents section (if Lazy Agents active):
- GitHub repo (text) — your LazyUnicorn prompts repo e.g. yourname/lazyunicorn. Stored in agent_settings.
- GITHUB_TOKEN — already set if using Lazy Code, Watch, Fix, or Build, otherwise stored as GITHUB_TOKEN secret with repo scope.
- Error threshold (number, default 3) — how many errors in an hour before opening a GitHub issue.
- Slack webhook URL (text, optional) — paste from Lazy Alert settings if installed.

Next button.

**Step 5 — Schedule**
Show a visual publishing schedule for active content engines. Selects for posts per day. Auto-stagger cron times so engines do not compete. Show a preview of the full weekly schedule as a timeline.
Launch button.

**On submit:**
1. Store all API keys as Supabase secrets
2. Save run_settings with active_engines as comma-separated list
3. Set setup_complete to true and prompt_version to 'v0.0.7'
4. Seed all engine-specific settings tables with provided values
5. Create all required database tables for active engines
6. For content engines immediately trigger: blog-publish, seo-discover, geo-discover
7. For Crawl if active immediately trigger crawl-run
8. For Perplexity if active immediately trigger perplexity-research
9. For Contentful if active immediately trigger contentful-pull
10. For Supabase if active immediately trigger supabase-monitor
11. For Security if active immediately trigger security-scan
12. For YouTube if active immediately trigger youtube-sync
13. For Agents if active immediately trigger agent-error-monitor
14. For Watch if active immediately trigger watch-monitor
15. For Granola if active immediately trigger granola-sync
16. For Drop if active immediately trigger drop-sync
17. For Print if active immediately trigger print-sync
18. For Repurpose if active immediately trigger repurpose-run
19. For Trend if active immediately trigger trend-scan
20. For Intel if active immediately trigger intel-weekly
21. Show loading: "Launching your autonomous operations layer..."
22. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Run', version: '0.0.11', site_url: site_url }) }) } catch(e) {}
23. Redirect to /admin with message: "Lazy Run is active. Your autonomous operations layer is running."

---

## 3. Master orchestrator edge functions

**run-orchestrator**
Cron: every 30 minutes — */30 * * * *

1. Read run_settings. If master_running is false or setup_complete is false exit.
2. Read active_engines as comma-separated list.
3. For each active engine check if it is time to run based on configured schedule.
4. Stagger execution with a 2-minute delay between each engine call.
5. Call the corresponding function for each engine due to run:

Content engines:
- Blogger: blog-publish
- SEO: seo-publish (seo-discover runs on its own Monday cron)
- GEO: geo-publish (geo-discover runs on its own cron)
- Crawl: crawl-run every 30 min, crawl-publish daily 6am
- Perplexity: perplexity-research daily 5am, perplexity-test-citations Sunday 10am, perplexity-improve-content Wednesday 9am

Commerce engines:
- Store: store-discover daily, store-optimise Sunday, store-content Tue/Fri, store-listings and store-prices daily
- Pay: pay-optimise Sunday, pay-recover daily
- SMS: sms-sequences-run every hour

Media engines:
- Voice: voice-narrate every 30 min
- Stream: stream-monitor every 5 min
- YouTube: youtube-sync every 30 min, youtube-extract-comments daily 4am, youtube-track-performance Monday 5am

Developer engines:
- Code: code-sync-roadmap every hour
- GitLab: gitlab-sync-roadmap every hour
- Linear: linear-sync-all every hour, linear-velocity-report Monday

Channels:
- Alert: alert-monitor every 5 min, alert-briefing daily 8am
- Telegram: telegram-monitor every 5 min, telegram-briefing daily 8am
- Contentful: contentful-pull every hour, contentful-push every 30 min
- Supabase: supabase-monitor every hour, supabase-weekly-report Monday
- Security: security-scan every hour (checks if pentest is due), security-poll every 10 min (checks scan status), security-monitor daily 3am

Developer engines:
- Auth: auth-setup (one-time on setup, not scheduled)
- Design: design-upgrade (one-time on setup, not scheduled)
- Granola: granola-sync every hour, granola-publish daily 9am

Commerce engines (additional):
- Drop: drop-sync daily 2am, drop-content Tue/Fri 9am, drop-optimise Sunday 10am
- Print: print-sync daily 2am, print-content Tue/Fri 9am, print-optimise Sunday 10am
- Mail: mail-campaign Mon/Wed/Fri 9am, mail-optimise Sunday 10am
- Churn: churn-analyse daily 3am, churn-trigger every 6 hours

Content engines (additional):
- Repurpose: repurpose-run daily 10am
- Trend: trend-scan daily 6am, trend-seed Tue/Thu 9am

Autonomous Agents:
- Intel: intel-weekly Monday 5am, intel-seed Wed/Fri 10am
- Watch: watch-monitor every hour
- Fix: fix-analyse Sunday 11pm
- Build: build-engine (triggered manually via admin, not scheduled)
- Agents: agent-error-monitor every hour, agent-prompt-improver Sunday 11pm, agent-performance-intel Monday 6am

6. Log each execution to run_activity: engine, action, result, details.
7. Log failures to run_errors.

**run-weekly-report**
Cron: every Monday at 7am UTC — 0 7 * * 1

1. Read run_settings. If master_running is false exit.
2. Collect last 7 days metrics from every active engine:
- Blogger: blog_posts count
- SEO: seo_posts count, seo_keywords count, keyword sources breakdown
- GEO: geo_posts count, citation rate, query sources breakdown
- Store: store_products count, active promotions
- Pay: pay_transactions succeeded count, MRR from pay_subscriptions
- SMS: sms_messages sent count, response rate from sms_sequences
- Voice: voice_episodes count
- Stream: stream_sessions processed, stream_content count
- YouTube: youtube_videos processed, youtube_content count, youtube_intelligence count, top performing video
- Code: code_commits processed, code_content count
- GitLab: gitlab_commits processed, gitlab_content count
- Linear: linear_issues completed, linear_content count
- Crawl: crawl_targets active, crawl_intel count, crawl_leads count
- Perplexity: perplexity_research count, brand citation rate from perplexity_citations
- Alert: alert_log count, success rate
- Telegram: telegram_log count
- Contentful: contentful_entries synced, contentful_sync_log push count
- Supabase: supabase_milestones reached, supabase_content count
- Security: current security score from latest security_scans, open critical count, open high count from security_vulnerabilities, last pentest date
- Agents: agent_runs count by agent, issues opened, PRs opened, improvements merged
- Granola: granola_meetings synced, granola_content count
- Drop: drop_products count, drop_content count
- Print: print_products count, print_content count
- Mail: mail_campaigns sent, mail_subscribers count
- Churn: churn_signals detected, churn_actions triggered
- Repurpose: repurpose_jobs count, repurpose_output count
- Trend: trend_topics discovered, trend_content count
- Intel: intel_reports count, intel_seeds count
- Watch: watch_issues opened, watch_issues resolved
- Fix: fix_improvements count, fix_runs PRs opened

3. Call the built-in Lovable AI:
"Write a weekly performance report for [brand_name]. Metrics from the last 7 days: [metrics list]. Write a friendly report under 300 words. Cover what the engines accomplished, the best performing engine, any areas for improvement, projection for next week. Write in second person. Return only the report text."
4. If Lazy Alert is installed send to Slack via alert-send.
5. If Lazy Telegram is installed send via telegram-send.
6. Send email to support_email with subject: "Your Lazy Run weekly report — [current date]".
7. Insert into run_activity with engine run, action weekly-report, result success.
Log errors to run_errors.

**run-health-check**
Cron: every hour — 0 * * * *

1. Read run_settings.
2. For each active engine query its errors table for errors in the last hour.
3. If any engine has more than 3 errors in the last hour: insert warning into run_activity with result error. If Lazy Alert is installed call alert-send with the warning. If Lazy Telegram is installed call telegram-send.
4. For Security engine: also check security_vulnerabilities for any new critical severity vulnerabilities found in the last hour. If found and Lazy Alert or Lazy Telegram is installed send an immediate alert regardless of error threshold.
5. For Agents engine: also check agent_issues for any new critical severity issues opened in the last hour. If found send alert.
6. For Watch engine: also check watch_issues for any new critical severity issues opened in the last hour. If found send alert.
6. Insert performance snapshot into run_performance for each engine.
Log errors to run_errors.

---

## 4. Install all engine edge functions

Install all edge functions for each active engine using these exact function names:
blog-publish, seo-discover, seo-publish, geo-discover, geo-publish, geo-test, store-discover, store-listings, store-prices, store-promote, store-optimise, store-content, voice-narrate, voice-rss, pay-checkout, pay-webhook, pay-optimise, pay-recover, pay-portal, sms-send, sms-receive, sms-status, sms-sequences-run, sms-optimise, stream-monitor, stream-process, stream-write-content, stream-optimise, youtube-sync, youtube-process, youtube-fetch-transcript, youtube-write-transcript, youtube-write-seo, youtube-write-geo, youtube-write-summary, youtube-generate-chapters, youtube-extract-comments, youtube-track-performance, github-webhook, code-sync-roadmap, code-write-content, code-optimise, gitlab-webhook, gitlab-sync-roadmap, gitlab-write-content, gitlab-optimise, linear-sync-all, linear-write-content, linear-velocity-report, linear-optimise, crawl-run, crawl-extract, crawl-publish, perplexity-research, perplexity-feed-engines, perplexity-test-citations, perplexity-improve-content, alert-send, alert-monitor, alert-briefing, alert-command, telegram-send, telegram-monitor, telegram-briefing, telegram-command, contentful-pull, contentful-webhook, contentful-push, supabase-monitor, supabase-publish-milestone, supabase-weekly-report, security-scan, security-poll, security-alert, security-generate-report, security-monitor, auth-setup, design-upgrade, granola-sync, granola-publish, drop-sync, drop-content, drop-optimise, print-sync, print-content, print-optimise, mail-send, mail-campaign, mail-optimise, churn-analyse, churn-trigger, repurpose-run, trend-scan, trend-seed, intel-weekly, intel-seed, watch-monitor, fix-analyse, fix-improve, build-engine, agent-error-monitor, agent-prompt-improver, agent-engine-writer, agent-performance-intel.

Only install functions for active engines.

---

## 5. Admin dashboard

Do not build a standalone /lazy-run-dashboard page. The unified admin dashboard lives at /admin and is built separately using the LazyUnicorn Admin Dashboard prompt.

Lazy Run's contribution to the admin is its data — run_activity, run_performance, run_errors, and run_settings are all read by the admin dashboard to power the overview page, activity feed, performance charts, and master controls.

On setup completion redirect to /admin with message: "Lazy Run is active. Your autonomous operations layer is running."

If /admin does not yet exist when Lazy Run is installed, create a temporary page at /admin that shows: the run_settings brand name, the master_running toggle connected to run_settings, a list of active engines from active_engines in run_settings each with their is_running status, the last 20 rows from run_activity, and a message: "Install the LazyUnicorn Admin Dashboard for the full control panel."

---

## 6. Public pages

Do not add any Lazy Run pages to public navigation.
Content published by individual engines appears through their own public routes.

---

## 7. Navigation

Add a single Admin link to site navigation pointing to /admin.
This replaces any existing admin links.
Do not expose any setup routes in public navigation.



## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

