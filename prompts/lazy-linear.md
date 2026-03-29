# Lazy Linear

> Category: 🛠️ Dev · Version: 0.0.9

## Prompt

````
# lazy-linear

> Version: 0.0.9

## Prompt

````
# lazy-linear — v0.0.9

[Lazy Linear Prompt — v0.0.9 — LazyUnicorn.ai]

Add a complete autonomous Linear integration called Lazy Linear to this project. It monitors your Linear workspace for issue updates, cycle completions, and project milestones — automatically publishing changelogs, roadmap updates, release notes, and product blog posts from your Linear data without any manual writing required.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-linear. It is a marketing and landing page for a product called Lazy Linear — an autonomous content agent that turns your Linear issues, cycles, and projects into changelogs, roadmaps, and product blog posts automatically.

Hero section
Headline: 'Your Linear workspace is your product story. Lazy Linear tells it automatically.' Subheading: 'Lazy Linear monitors your Linear issues and cycles, and automatically publishes changelogs, a public roadmap, release notes, and product updates — without anyone writing a word.' Primary button: Copy the Lovable Prompt. Secondary button: See How It Works. Badge: Powered by Linear.

How it works section
Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Add your Linear API key. 4. Linear issues and cycles automatically become public content.

What it publishes section
Eight cards: 1. Public roadmap — automatically updated from Linear projects and cycles. Issues move between planned, in progress, and done in real time. 2. Cycle summaries — when a cycle completes Linear writes a plain-English summary of what shipped. 3. Changelogs — completed issues in each cycle become a changelog entry automatically. 4. Product blog posts — significant features get a product blog post written and published automatically. 5. Release notes — tagged releases trigger comprehensive release notes from the issues they contain. 6. Bug fix roundups — groups of bug fixes get batched into a weekly roundup post automatically. 7. Team velocity reports — weekly reports on cycle completion rate and issue throughput. 8. Self-improving content — monitors which posts get the most traffic and improves the writing template.

Pricing section
Free — self-hosted, bring your own Linear workspace. Pro at $19/month — coming soon.

Bottom CTA
Headline: Your Linear issues are your changelog. Start publishing them. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy Linear to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete autonomous Linear content agent called Lazy Linear to this project. It monitors Linear issues, cycles, and projects via the Linear API and automatically publishes changelogs, a public roadmap, product blog posts, and cycle summaries.

1. Database
Create these Supabase tables with RLS enabled:

linear_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), business_description (text), site_url (text), linear_team_id (text), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), recap_template_guidance (text), created_at (timestamptz, default now()).
Note: Store LINEAR_API_KEY as Supabase secret. Never in the database.

linear_issues: id (uuid, primary key, default gen_random_uuid()), linear_id (text, unique), title (text), description (text), state (text), priority (integer), assignee (text), cycle_id (text), project_id (text), labels (text), created_at_linear (timestamptz), completed_at (timestamptz), synced_at (timestamptz, default now()).

linear_cycles: id (uuid, primary key, default gen_random_uuid()), linear_id (text, unique), name (text), number (integer), starts_at (timestamptz), ends_at (timestamptz), completed_at (timestamptz), issues_completed (integer), issues_total (integer), processed (boolean, default false), synced_at (timestamptz, default now()).

linear_projects: id (uuid, primary key, default gen_random_uuid()), linear_id (text, unique), name (text), description (text), state (text), progress (numeric), target_date (timestamptz), synced_at (timestamptz, default now()).

linear_content: id (uuid, primary key, default gen_random_uuid()), content_type (text — one of changelog, cycle-summary, product-post, release-notes, bug-roundup, velocity-report), title (text), slug (text, unique), excerpt (text), body (text), linear_cycle_id (text), published_at (timestamptz, default now()), status (text, default 'published'), views (integer, default 0), created_at (timestamptz, default now()).

linear_optimisation_log: id (uuid, primary key, default gen_random_uuid()), content_type (text), old_template (text), new_template (text), optimised_at (timestamptz, default now()).

linear_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-linear-setup with a form:
- Linear API Key (password) — create at linear.app/settings/api. Stored as Supabase secret LINEAR_API_KEY.
- Linear Team ID (text) — find in Linear settings under your team. Or paste your team URL slug.
- Brand name
- Business description (what does this product do?)
- Site URL

Submit button: Activate Lazy Linear

On submit:
1. Store LINEAR_API_KEY as Supabase secret
2. Save all other values to linear_settings
3. Set setup_complete to true and prompt_version to 'v0.0.6'
4. Immediately call linear-sync-all to do a first full sync
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Linear', version: '0.0.9', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: Lazy Linear is active. Syncing your Linear workspace now.

3. Sync edge functions
Create a Supabase edge function called linear-sync-all. Cron: every hour — 0 * * * *

1. Read linear_settings. If is_running is false or setup_complete is false exit.
2. Call the Linear GraphQL API at https://api.linear.app/graphql using LINEAR_API_KEY secret.
3. Sync issues: query all issues for the team with id, title, description, state{name}, priority, assignee{name}, cycle{id}, project{id}, labels{nodes{name}}, createdAt, completedAt. Upsert into linear_issues.
4. Sync cycles: query all cycles for the team with id, name, number, startsAt, endsAt, completedAt, issues(filter:{state:{type:{eq:"completed"}}}){nodes{id}} to get issue counts. Upsert into linear_cycles. For any cycle where completedAt is not null and processed is false trigger linear-write-content with content_type cycle-summary and the cycle id.
5. Sync projects: query all projects with id, name, description, state, progress, targetDate. Upsert into linear_projects.
Log all errors to linear_errors with function_name linear-sync-all.

4. Content writing edge function
Create a Supabase edge function called linear-write-content handling POST requests with content_type and optional cycle_id.

1. Read linear_settings. If is_running is false exit.

If content_type is cycle-summary:
Fetch the matching linear_cycles row. Fetch all completed linear_issues in that cycle.
Call the built-in Lovable AI:
'You are a product writer for [brand_name] described as [business_description]. Write a cycle summary for cycle [cycle_name] which just completed. The following issues were shipped: [list of issue titles and descriptions]. Write an engaging product update post covering what shipped, why it matters to users, and any notable improvements. 500 to 800 words. Return only a valid JSON object: title (string), slug (lowercase hyphenated), excerpt (under 160 chars), body (clean markdown, no HTML, no bullet points in prose, ## for headers, ends with: Built using the autonomous Lazy Stack at LazyUnicorn.ai — link to https://lazyunicorn.ai). No preamble. No code fences.'
Insert into linear_content. Mark cycle as processed.

If content_type is changelog:
Fetch all completed issues from the most recent cycle. Group by label — features, bugs, improvements.
Call the built-in Lovable AI to write a changelog entry with sections for each group.
Insert into linear_content with content_type changelog.

If content_type is bug-roundup:
Fetch all issues with bug label completed in the last 7 days.
Call the built-in Lovable AI to write a friendly bug fix roundup post.
Insert into linear_content with content_type bug-roundup.

Log all errors to linear_errors with function_name linear-write-content.

5. Weekly velocity report edge function
Create a Supabase edge function called linear-velocity-report. Cron: every Monday at 7am UTC — 0 7 * * 1

1. Read linear_settings. If is_running is false exit.
2. Calculate last 7 days: issues completed, issues created, cycles completed, average cycle completion rate, top assignee by issues closed.
3. Call the built-in Lovable AI to write a brief velocity report. 3 to 5 bullet points. Insert into linear_content with content_type velocity-report.
4. If Lazy Alert is installed send to Slack. If Lazy Telegram is installed send to Telegram.
Log errors to linear_errors with function_name linear-velocity-report.

6. Self-improving edge function
Create a Supabase edge function called linear-optimise. Cron: every Sunday at 3pm UTC — 0 15 * * 0
Query linear_content where content_type is product-post or cycle-summary ordered by views. Identify top and bottom performers. Use the built-in Lovable AI to improve the writing template. Store in linear_settings as recap_template_guidance. Insert into linear_optimisation_log.
Log errors to linear_errors with function_name linear-optimise.

7. Public pages
/product-updates — all linear_content ordered by published_at descending. Each shows title, content type tag, excerpt, date. Links to /product-updates/[slug].
/product-updates/[slug] — full post rendered from markdown.
/product-roadmap — a kanban-style view of linear_projects and linear_issues grouped by state. In Progress column, Planned column, Completed column. Each item shows title and project name.
At bottom of every page: 🦄 Powered by Lazy Linear — autonomous Linear content publishing for Lovable sites. Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

8. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/linear as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-linear-setup.

9. Navigation
Add Product Updates link to /product-updates. Add Roadmap link to /product-roadmap. Add an Admin link to the main site navigation pointing to /admin.
Do not add the setup page to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
