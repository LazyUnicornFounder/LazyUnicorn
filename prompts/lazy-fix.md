# lazy-fix — v0.0.4

[Lazy Fix Prompt — v0.0.4 — LazyUnicorn.ai]

Add an autonomous prompt improvement agent called Lazy Fix to this project. Every Sunday night it reads your agent performance data, identifies the two weakest-performing Lazy agents, makes targeted improvements to their prompts, and opens GitHub PRs for you to review Monday morning — all automatically.

Required secrets:
- GITHUB_TOKEN — personal access token with repo scope from github.com/settings/tokens
- GITHUB_REPO — your prompts repo in format username/reponame
- SLACK_WEBHOOK_URL — optional, from Lazy Alert settings

---

1. Database

Create these Supabase tables with RLS enabled:

fix_settings: id (uuid, primary key, default gen_random_uuid()), github_repo (text), slack_webhook_url (text), improvement_focus (text, default 'auto' — one of auto, output-volume, error-rate, content-quality), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

fix_runs: id (uuid, primary key, default gen_random_uuid()), status (text — one of running, completed, failed), agents_analysed (integer, default 0), prs_opened (integer, default 0), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

fix_improvements: id (uuid, primary key, default gen_random_uuid()), agent_name (text), problem_identified (text), section_improved (text), improvement_description (text), pr_url (text), pr_status (text, default 'open' — one of open, merged, rejected), prompt_version_before (text), prompt_version_after (text), created_at (timestamptz, default now())

fix_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-fix-setup.

Welcome message: 'Lazy Fix reads your agent performance data every Sunday night and quietly improves the weakest prompts. You wake up Monday to GitHub PRs ready to review — targeted, tested improvements written by Lovable AI, following your SPEC.md rules.'

Prerequisites note: You need GITHUB_TOKEN as a Supabase secret with repo scope (github.com/settings/tokens) and GITHUB_REPO set to your prompts repository in format username/reponame. Lazy Fix reads your Supabase data to identify performance issues — no additional API keys needed.

Form fields:
- GitHub repo (text) — your LazyUnicorn prompts repo e.g. yourname/lazyunicorn
- Improvement focus (select: Auto — let Lazy Fix decide what to improve / Output volume — prioritise agents publishing too little / Error rate — prioritise agents with most errors / Content quality — prioritise agents whose content could be better structured)
- Slack webhook URL (text, optional)

Submit button: Activate Lazy Fix

On submit:
1. Save all values to fix_settings
2. Set setup_complete to true and prompt_version to 'v0.0.1'
3. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Fix', version: '0.0.4', site_url: site_url }) }) } catch(e) {}
4. Redirect to /admin with message: 'Lazy Fix is active. It will run this Sunday at 11pm UTC and open PRs for your review Monday morning.'

---

3. Edge functions

fix-analyse
Cron: every Sunday at 11pm UTC — 0 23 * * 0

1. Read fix_settings. If is_running false or setup_complete false exit.
2. Insert into fix_runs with status running.
3. Gather performance signals from all available tables. For each check: try the query — if the table does not exist skip silently:
   - blog_posts: group by post_type, count rows in last 30 days, find post_types with fewer than 4 posts in last 14 days
   - seo_posts: count rows added in last 14 days
   - geo_posts: count rows added in last 14 days
   - For each known error table (blogger_errors, seo_errors, geo_errors, etc.): count rows in last 7 days
4. Build a performance JSON summary: array of objects each with agent_name, posts_last_14_days, errors_last_7_days, last_activity_date (most recent created_at from any output table for that agent).
5. Call the built-in Lovable AI to select the two agents to improve:
'You are a prompt engineer reviewing performance data for LazyUnicorn autonomous agents. Focus: [improvement_focus]. Here is the last 30 days of performance data: [performance JSON]. Select the 2 agents most in need of prompt improvement. Criteria: high error rates, low or zero output volume, long gap since last activity, or poor output structure. For each agent return: agent_name, problem (specific one-sentence description of what is underperforming), section_to_improve (which section of the prompt — e.g. the cron function, the AI prompt template, the database setup, the error handling), improvement_instruction (4 to 6 specific sentences describing exactly what to change and why — be precise, not generic). Return only a valid JSON array of exactly 2 objects. No preamble. No code fences.'
6. Parse response. For each of the 2 agents call fix-improve with the agent details.
7. Update fix_runs: status completed, agents_analysed count, prs_opened count, completed_at now.
Log errors to fix_errors with function_name fix-analyse.

fix-improve
Triggered by fix-analyse. Accepts agent_name, problem, section_to_improve, improvement_instruction.

1. Read fix_settings.
2. Derive the prompt filename from agent_name: convert to lowercase, replace spaces with hyphens, find the file in the GitHub repo. GET https://api.github.com/repos/[GITHUB_REPO]/contents/ with Authorization: Bearer [GITHUB_TOKEN]. Find the file matching lazy-[slugified-agent-name]_v*.txt.
3. Fetch the current file content: GET https://api.github.com/repos/[GITHUB_REPO]/contents/[filename]. Decode from base64.
4. Extract the current version number from the file header (e.g. v0.0.5).
5. Also fetch CLAUDE.md from the repo root for the rules.
6. Call the built-in Lovable AI to apply the targeted improvement:
'You are editing a LazyUnicorn Lovable prompt file. The file is for [agent_name]. Problem identified: [problem]. Section to improve: [section_to_improve]. Specific improvement to make: [improvement_instruction]. Rules from CLAUDE.md: [CLAUDE.md content]. Here is the current prompt file: [file content]. Apply the improvement to the [section_to_improve] section only. Do not restructure the rest of the file. Do not change anything outside the specified section. Increment the version number in the header by one patch version (e.g. v0.0.5 → v0.0.6). Return only the complete updated prompt file content. No preamble. No explanation.'
7. Parse response — the full updated file content.
8. Create a new branch: POST https://api.github.com/repos/[GITHUB_REPO]/git/refs body: ref refs/heads/fix-[slugified-agent-name]-[unix-timestamp], sha of current main branch (GET https://api.github.com/repos/[GITHUB_REPO]/git/ref/heads/main first).
9. Commit the updated file to the new branch: PUT https://api.github.com/repos/[GITHUB_REPO]/contents/[filename] with message Fix [agent_name]: [problem truncated to 60 chars], content base64-encoded updated file, branch the new branch name, sha the current file SHA from step 2.
10. Open a PR: POST https://api.github.com/repos/[GITHUB_REPO]/pulls with title: [agent_name] — [problem truncated], body: '## What changed\n\n[improvement_instruction]\n\n## Why\n\n[problem]\n\n## Section modified\n\n[section_to_improve]\n\n## Performance data that triggered this\n\nAuto-generated by Lazy Fix on [date]. Review the diff before merging.\n\n@claude please review this change against CLAUDE.md rules before merge.', head the new branch name, base main.
11. Insert into fix_improvements with all details including the old and new version numbers.
12. If slack_webhook_url is set: POST to Slack: '🔧 *Lazy Fix* opened a PR for [agent_name]: [problem] → <[pr_url]|Review PR>'
Log errors to fix_errors with function_name fix-improve.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Fix lives at /admin/fix as part of the unified LazyUnicorn admin panel.

The /admin/fix section shows:

Status bar: last run time, next run (next Sunday 11pm UTC), PRs opened this month, a Run Now button.

Run history: all fix_runs ordered by started_at descending, last 10 rows. Columns: date, status badge, agents analysed, PRs opened, summary, duration.

Improvements table: all fix_improvements ordered by created_at descending. Columns: agent name badge, problem description, section improved, version change (v0.0.5 → v0.0.6), PR link, PR status select (open/merged/rejected that updates the row). Filter by pr_status.

Settings: improvement focus selector, GitHub repo, Slack status, is_running toggle.

Error log: fix_errors last 20 rows, collapsed by default.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-fix-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.