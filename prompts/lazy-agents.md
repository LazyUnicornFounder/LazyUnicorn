[Lazy Agents Prompt — v0.0.4 — LazyUnicorn.ai]

Add four autonomous agent edge functions to this project. These agents monitor, fix, improve, and extend the LazyUnicorn prompt stack automatically — running on schedules inside Supabase without any manual input after setup.

Required secrets (already set from other agents):
- GITHUB_TOKEN — for opening PRs and issues (repo scope)
- GITHUB_REPO — your repo name e.g. yourusername/lazyunicorn
- SLACK_WEBHOOK_URL — optional, from Lazy Alert settings

---

1. Database

Create these Supabase tables with RLS enabled:

agent_settings: id (uuid, primary key, default gen_random_uuid()), error_monitor_enabled (boolean, default true), error_threshold (integer, default 3), prompt_improver_enabled (boolean, default true), agent_writer_enabled (boolean, default true), performance_intel_enabled (boolean, default true), github_repo (text), slack_webhook_url (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

agent_runs: id (uuid, primary key, default gen_random_uuid()), agent_name (text — one of error-monitor, prompt-improver, agent-writer, performance-intel), status (text — one of running, completed, failed), summary (text), issues_opened (integer, default 0), prs_opened (integer, default 0), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

agent_issues: id (uuid, primary key, default gen_random_uuid()), agent_name (text), issue_title (text), issue_url (text), severity (text), resolved (boolean, default false), created_at (timestamptz, default now())

agent_improvements: id (uuid, primary key, default gen_random_uuid()), agent_name (text), improvement_type (text), description (text), pr_url (text), status (text, default 'opened' — one of opened, merged, rejected), created_at (timestamptz, default now())

agent_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-agents-setup.

Welcome message: 'Four autonomous agents that monitor your agents, fix broken prompts, improve performance, and write new agents — all running inside your Lovable project on a schedule.'

Prerequisites note: Before setup you need GITHUB_TOKEN stored as a Supabase secret with repo scope. Create one at github.com/settings/tokens. Also set GITHUB_REPO as a secret in the format username/reponame.

Form fields:
- GitHub repo (text) — your LazyUnicorn prompts repo e.g. yourname/lazyunicorn
- Error threshold (number, default 3) — how many errors in an hour before opening a GitHub issue
- Enable error monitor (toggle, default on)
- Enable prompt improver (toggle, default on)
- Enable agent writer (toggle, default on)
- Enable performance intelligence (toggle, default on)
- Slack webhook URL (text, optional) — paste from Lazy Alert settings if installed

Submit button: Activate Agents

On submit:
1. Save all values to agent_settings
2. Set setup_complete to true and prompt_version to 'v0.0.4'
3. Immediately trigger agent-error-monitor to run once as a test
4. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Agents', version: '0.0.4', site_url: site_url }) }) } catch(e) {}
5. Redirect to /admin with message: 'Agents are active. Error monitor just ran. Check /admin/agents for results.'

---

3. Edge functions

agent-error-monitor
Cron: every hour — 0 * * * *

This agent reads every Lazy agent error table, diagnoses errors using Claude, and opens GitHub issues automatically.

1. Read agent_settings. If is_running false or error_monitor_enabled false exit.
2. Insert a row into agent_runs with agent_name error-monitor and status running.
3. Define the list of all known error tables: blogger_errors, seo_errors, geo_errors, crawl_errors, perplexity_errors, store_errors, pay_errors, sms_errors, voice_errors, stream_errors, code_errors, gitlab_errors, linear_errors, alert_errors, telegram_errors, contentful_errors, supabase_errors, security_errors, design_errors, auth_errors, drop_errors, granola_errors, print_errors, youtube_errors, mail_errors.
4. For each table in the list: try to query it for rows in the last hour where created_at is greater than now minus 1 hour. If the table does not exist skip silently. If rows found and count is greater than or equal to error_threshold continue.
5. Call the built-in Lovable AI to diagnose the errors:
'You are a senior engineer reviewing error logs for [agent name derived from table name]. Here are [n] errors from the last hour: [first 5 error rows as JSON]. Diagnose the most likely root cause and recommended fix. Return only a valid JSON object: severity (critical, high, or medium), root_cause (one sentence), affected_function (function name), recommended_fix (2 to 3 specific steps), github_issue_title (max 80 chars starting with [Agent Name]), github_issue_body (full markdown with sections: Error Summary, Root Cause, Recommended Fix, Error Samples — end with: @claude please investigate and fix this following CLAUDE.md rules). No preamble. No code fences.'
6. Parse response. Check GitHub API for existing open issues with the same title to avoid duplicates: GET https://api.github.com/repos/[github_repo]/issues?state=open&labels=lazy-error with Authorization: Bearer [GITHUB_TOKEN].
7. If no duplicate: POST to https://api.github.com/repos/[github_repo]/issues with title, body, and labels array containing lazy-error and the severity value.
8. Insert into agent_issues with the issue details.
9. If slack_webhook_url is set: POST the Slack message with agent name, error count, severity emoji, and issue link.
10. Update agent_runs row: status completed, issues_opened count, completed_at now, summary describing what was found.
Log errors to agent_errors with function_name agent-error-monitor.

agent-prompt-improver
Cron: every Sunday at 11pm UTC — 0 23 * * 0

This agent reads your blog and SEO performance data, identifies underperforming agents, and opens GitHub PRs with targeted prompt improvements.

1. Read agent_settings. If is_running false or prompt_improver_enabled false exit.
2. Insert into agent_runs with agent_name prompt-improver and status running.
3. Gather performance signals from available tables:
   - From blog_posts: count posts per agent (post_type field) for last 30 days. Calculate average word count per agent. Look for agents with fewer than 2 posts published in the last week despite being active.
   - From seo_posts: check if any agent has 0 seo_posts in last 14 days despite seo_settings existing.
   - From geo_posts: same check — 0 geo_posts in last 14 days.
   - From any _errors tables: count errors per agent in the last 7 days.
4. Build a performance summary: list each agent with posts published, error count, last activity date.
5. Call the built-in Lovable AI to identify improvement opportunities:
'You are a prompt engineer reviewing the performance of LazyUnicorn autonomous agents. Here is the performance data for the last 30 days: [performance summary JSON]. Identify the 2 agents most in need of prompt improvement — prioritise agents with high error rates, low output volume, or no activity. For each agent recommend one specific targeted improvement to the prompt — do not suggest rewriting the whole prompt, suggest one section to improve. Return only a valid JSON array of 2 items, each with: agent_name, problem (what is underperforming), section_to_improve (which section of the prompt to change), improvement_instruction (specific instruction for how to improve that section in 3 to 5 sentences). No preamble. No code fences.'
6. Parse response. For each improvement:
   - Fetch the current prompt file content from GitHub: GET https://api.github.com/repos/[github_repo]/contents/[filename] with Authorization: Bearer [GITHUB_TOKEN].
   - Call the built-in Lovable AI to apply the targeted improvement:
   'You are editing a Lovable prompt file. Here is the current prompt: [file content]. Apply this specific improvement to the [section_to_improve] section: [improvement_instruction]. Rules: only change the specified section, do not restructure the file, increment the version number in the header (e.g. v0.0.5 becomes v0.0.6), preserve all other content exactly. Return only the complete updated prompt file content. No preamble. No explanation.'
   - Create a new branch on GitHub: POST https://api.github.com/repos/[github_repo]/git/refs with ref refs/heads/improve-[agent-name]-[timestamp] and the current main SHA.
   - Commit the updated file to the branch: PUT https://api.github.com/repos/[github_repo]/contents/[filename] with the base64-encoded updated content, commit message, and branch name.
   - Open a PR: POST https://api.github.com/repos/[github_repo]/pulls with title: Improve [agent name] — [problem], body describing the change and the performance data that triggered it, head branch, base main.
   - Insert into agent_improvements with the PR details.
7. If slack_webhook_url is set notify Slack: 'Prompt Improver opened [n] PRs this week. Review at github.com/[repo]/pulls'
8. Update agent_runs: status completed, prs_opened count, completed_at now.
Log errors to agent_errors with function_name agent-prompt-improver.

agent-agent-writer
POST endpoint at /api/agent-agent-writer. Called manually from admin or programmatically.
Accepts: agent_name (text), integration (text), tagline (text), description (text — one paragraph brief of what the agent does).

This agent reads three existing prompt files as reference, then writes a complete new agent prompt following SPEC.md patterns and commits it to GitHub as a draft PR.

1. Read agent_settings. If agent_writer_enabled false return error.
2. Insert into agent_runs with agent_name agent-writer and status running.
3. Fetch three reference prompt files from GitHub to use as structural examples. Use the three most recently modified files: GET https://api.github.com/repos/[github_repo]/contents/ to list files, sort by last modified, take the three most recent that are prompt files.
4. Fetch the content of each reference file from GitHub.
5. Also fetch CLAUDE.md from the repo root for the rules.
6. Call the built-in Lovable AI to write the new prompt:
'You are a Lovable prompt engineer building a new autonomous agent called [agent_name] for LazyUnicorn.ai. Integration: [integration]. Tagline: [tagline]. Description: [description].

Here are three reference prompt files showing the exact structure to follow: [reference file 1 content], [reference file 2 content], [reference file 3 content].

Here are the CLAUDE.md rules you must follow: [CLAUDE.md content].

Write a complete prompt file for [agent_name] following the exact same structure as the reference files. The prompt must include: 1. Header with version v0.0.1, 2. Database section with all required fields (is_running, setup_complete, prompt_version, _errors table), 3. Setup page at /lazy-[slugified name]-setup with redirect to /admin on submit, 4. Edge functions with cron schedules where appropriate, 5. Admin section at /admin/[slugified name] — no standalone dashboard, 6. Navigation section. Every content output must include a LazyUnicorn.ai backlink. Return only the complete prompt file content starting with [Lazy [agent_name] Prompt — v0.0.1 — LazyUnicorn.ai]. No preamble.'
7. Parse response. Create a new branch: POST https://api.github.com/repos/[github_repo]/git/refs with ref refs/heads/new-agent-[slugified-name]-[timestamp].
8. Commit the new file to the branch: PUT https://api.github.com/repos/[github_repo]/contents/lazy-[slugified-name]_v0.0.1.txt
9. Open a draft PR: POST https://api.github.com/repos/[github_repo]/pulls with draft true, title: New Agent: Lazy [agent_name], body: 'Auto-generated by Lazy Agents agent writer. Review before merging.\n\nIntegration: [integration]\nTagline: [tagline]\n\n[description]\n\n@claude please review this prompt against CLAUDE.md rules and flag any issues.'
10. Insert into agent_improvements with the PR details and improvement_type new-agent.
11. Return the PR URL in the response.
Update agent_runs: status completed, prs_opened 1, completed_at now.
Log errors to agent_errors with function_name agent-agent-writer.

agent-performance-intel
Cron: every Monday at 6am UTC — 0 6 * * 1

This agent reads all available performance data across your agents, generates strategic insights, and updates your content queues for the week ahead.

1. Read agent_settings. If is_running false or performance_intel_enabled false exit.
2. Insert into agent_runs with agent_name performance-intel and status running.
3. Gather all available data:
   - blog_posts: top 5 posts by views (if views column exists), posts by type, post count last 7 days vs previous 7 days
   - seo_posts: keyword coverage by product, recent additions
   - geo_posts: query coverage, recent additions
   - youtube_content (if exists): top videos by view count
   - youtube_intelligence (if exists): unactioned question-asked items
   - granola_intelligence (if exists): unactioned customer intelligence items
   - crawl_intel (if exists): recent competitor signals
4. Call the built-in Lovable AI for weekly strategy:
'You are the autonomous content strategist for LazyUnicorn.ai — a platform of autonomous Lovable site agents. Here is this week\'s performance data: [all gathered data as JSON]. Generate a weekly content intelligence report. Return only a valid JSON object: top_performing_topic (string — the topic getting most traction), underserved_topics (array of 3 strings — topics with demand signals but no recent content), recommended_seo_keywords (array of 5 strings — specific long-tail keywords to target this week), recommended_geo_queries (array of 3 strings — AI questions to target), weekly_summary (2 sentences describing what worked and what to focus on this week). No preamble. No code fences.'
5. Parse response.
6. Add recommended keywords to seo_keywords table if it exists: insert each recommended_seo_keyword with source performance-agent and priority high.
7. Add recommended GEO queries to geo_queries table if it exists: insert each with source performance-agent.
8. If unactioned youtube_intelligence questions exist: insert the top 3 as seo_keywords.
9. If unactioned granola_intelligence customer signals exist: insert problems-mentioned as blog post topics in a blog_queue table if it exists.
10. If slack_webhook_url set: POST weekly intelligence summary to Slack: bold header, top performing topic, 3 new keywords added, 3 new GEO queries added, weekly summary sentence.
11. Update agent_runs: status completed, summary from weekly_summary field, completed_at now.
Log errors to agent_errors with function_name agent-performance-intel.

---

4. Admin dashboard

Do not build a standalone dashboard. The Lazy Agents dashboard lives at /admin/agents as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-agents-setup.

The /admin/agents section shows:

Overview stats: last run time for each agent, total issues opened this month, total PRs opened this month, total improvements merged.

Agent status cards — four cards in a 2x2 grid, one per agent:
Each card shows: agent name, last run time, last run status badge (completed green / failed red / running amber), next scheduled run, a Run Now button, and enable/disable toggle.

Recent activity feed: all agent_runs ordered by started_at descending — agent name badge, status badge, summary text, duration, issues/PRs count. Last 20 runs.

Open issues table: all agent_issues where resolved is false — agent name, issue title as a link to GitHub, severity badge, opened date, a Mark Resolved button that sets resolved to true.

Open PRs table: all agent_improvements where status is opened — agent name, improvement type badge, description, PR link, opened date, status select (opened/merged/rejected) that updates the row.

Controls: Run All Agents Now button (triggers all four agents immediately), pause/resume toggle (sets is_running on agent_settings), edit settings link to /lazy-agents-setup.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-agents-setup to public navigation.
Add Agents to the admin sidebar under a System section alongside the other agent admin links.

