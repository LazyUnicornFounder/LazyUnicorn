# Lazy Watch

> Category: ⚙️ Ops · Version: 0.0.3

## Prompt

````
# lazy-watch

> Version: 0.0.2

## Prompt

````
# lazy-watch — v0.0.1

[Lazy Watch Prompt — v0.0.1 — LazyUnicorn.ai]

Add an autonomous error monitoring agent called Lazy Watch to this project. It reads every Lazy agent error table in your Supabase project every hour, diagnoses issues using Lovable AI, opens GitHub issues with full diagnosis and fix recommendations, and pings Slack — all automatically with no manual input required after setup.

Required secrets:
- GITHUB_TOKEN — personal access token with repo scope from github.com/settings/tokens
- GITHUB_REPO — your prompts repo in format username/reponame
- SLACK_WEBHOOK_URL — optional, from Lazy Alert settings

---

1. Database

Create these Supabase tables with RLS enabled:

watch_settings: id (uuid, primary key, default gen_random_uuid()), github_repo (text), error_threshold (integer, default 3), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

watch_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), agents_checked (integer, default 0), issues_opened (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

watch_issues: id (uuid, primary key, default gen_random_uuid()), agent_name (text), issue_title (text), issue_url (text), severity (text — one of critical, high, medium), error_count (integer), resolved (boolean, default false), created_at (timestamptz, default now())

watch_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-watch-setup.

Welcome message: 'Lazy Watch monitors every Lazy agent in your stack every hour. When errors spike it uses Lovable AI to diagnose the root cause, opens a GitHub issue with a fix recommendation, and tags @claude to investigate — automatically, while you sleep.'

Prerequisites note: You need a GitHub personal access token with repo scope. Create one at github.com/settings/tokens. Set it as GITHUB_TOKEN in your Supabase secrets. Also set GITHUB_REPO as a secret in the format username/reponame pointing to your LazyUnicorn prompts repository.

Form fields:
- GitHub repo (text) — your LazyUnicorn prompts repo e.g. yourname/lazyunicorn
- Error threshold (number, default 3) — how many errors in one hour before opening a GitHub issue. Set lower (1 or 2) for high sensitivity, higher (5 or 10) for less noise.
- Slack webhook URL (text, optional) — paste from Lazy Alert settings if installed. Leave blank to skip Slack notifications.

Submit button: Activate Lazy Watch

On submit:
1. Save all values to watch_settings
2. Set setup_complete to true and prompt_version to 'v0.0.1'
3. Immediately trigger watch-monitor to run once as a connectivity test
4. Redirect to /admin with message: 'Lazy Watch is active. It just ran its first check. Visit /admin/watch to see results.'

---

3. Edge functions

watch-monitor
Cron: every hour — 0 * * * *

1. Read watch_settings. If is_running false or setup_complete false exit.
2. Insert a row into watch_runs with status running.
3. Define the full list of known Lazy agent error tables: blogger_errors, seo_errors, geo_errors, crawl_errors, perplexity_errors, store_errors, pay_errors, sms_errors, voice_errors, stream_errors, code_errors, gitlab_errors, linear_errors, alert_errors, telegram_errors, contentful_errors, supabase_errors, security_errors, design_errors, auth_errors, drop_errors, granola_errors, print_errors, youtube_errors, mail_errors, watch_errors.
4. For each table in the list:
   a. Try to query it: SELECT * FROM [table] WHERE created_at > now() - interval '1 hour'. If the table does not exist catch the error and skip silently — this means that agent is not installed.
   b. If row count is less than error_threshold skip.
   c. If row count is greater than or equal to error_threshold: proceed to diagnose.
5. For each agent with errors at or above threshold:
   a. Derive the agent name from the table name e.g. blogger_errors → Lazy Blogger.
   b. Call the built-in Lovable AI:
   'You are a senior Supabase edge function engineer reviewing error logs for [agent_name]. These are [n] errors from the last hour: [first 8 error rows as JSON — include function_name and error_message fields]. Diagnose the most likely root cause. Return only a valid JSON object: severity (critical if the agent is completely non-functional, high if partially broken, medium if occasional failures), root_cause (one sentence), affected_function (the edge function name most likely responsible), recommended_fix (3 specific actionable steps numbered 1 2 3), github_issue_title (under 80 chars starting with [Agent Name] — e.g. [Lazy Blogger] Edge function failing on AI response parsing), github_issue_body (full markdown GitHub issue body with sections: ## Error Summary showing count and timeframe, ## Root Cause, ## Recommended Fix as numbered list, ## Error Samples showing 3 representative errors in a code block, ## Next Steps ending with: @claude please investigate and fix this issue following all rules in CLAUDE.md). No preamble. No code fences.'
   c. Parse the JSON response.
   d. Check for duplicate open issues on GitHub to avoid noise: GET https://api.github.com/repos/[GITHUB_REPO]/issues?state=open&labels=lazy-error&per_page=50 with header Authorization: Bearer [GITHUB_TOKEN]. Check if any open issue title matches the generated title.
   e. If no duplicate exists: POST https://api.github.com/repos/[GITHUB_REPO]/issues with body: title from diagnosis, body from diagnosis, labels array containing lazy-error and the severity value (critical/high/medium).
   f. If the GitHub API returns 201 success: insert into watch_issues with all details. Increment issues_opened counter.
   g. If slack_webhook_url is set: POST to the webhook URL with a Slack message: severity emoji (🔴 critical / 🟠 high / 🟡 medium) followed by bold agent name, error count, and a link to the GitHub issue. Format: '[emoji] *[Agent Name]* — [n] errors in 1hr → <[issue_url]|View Issue>'.
6. Update watch_runs row: status completed, agents_checked count, issues_opened count, completed_at now, summary '[n] agents checked, [n] issues opened'.
Log all caught exceptions to watch_errors with function_name watch-monitor.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Watch lives at /admin/watch as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-watch-setup.

The /admin/watch section shows:

Status bar: last run time, last run status badge, next run time (next hour), total issues opened this month, a Run Now button that triggers watch-monitor immediately.

Run history table: all watch_runs ordered by started_at descending, last 20 rows. Columns: started time, status badge (completed green / failed red / running amber), agents checked, issues opened, summary, duration in minutes.

Open issues table: all watch_issues where resolved is false, ordered by created_at descending. Columns: agent name badge colour-coded by category, issue title as a clickable link to GitHub, severity badge (red/orange/yellow), error count, opened date, a Mark Resolved button that sets resolved to true and adds a resolved_at timestamp.

Agent coverage list: show all 26 known error table names. For each one show a status: Active (table exists and was checked in last run) or Not installed (table does not exist — agent not installed) in muted grey. This tells the user which agents are being monitored.

Settings: current error threshold with an edit button, GitHub repo, Slack webhook status (Connected / Not connected), is_running toggle.

Error log: all watch_errors ordered by created_at descending, last 20 rows. Collapsed by default, expand on click.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-watch-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
