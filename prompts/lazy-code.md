# Lazy GitHub

> Category: 🛠️ Dev · Version: 0.0.6

## Prompt

````
# lazy-code

> Version: 0.0.5

## Prompt

````
# lazy-code — v0.0.4

[Lazy Code Prompt — v0.0.4 — LazyUnicorn.ai]

Add a complete autonomous GitHub content agent called Lazy Code to this project. It monitors a GitHub repository via webhooks, processes commits and releases, writes plain-English changelogs, release notes, developer blog posts, SEO articles, and maintains a public roadmap — all automatically with no manual input required after setup.

---

## 1. Database

Create these Supabase tables with RLS enabled:

**code_settings**
id (uuid, primary key, default gen_random_uuid()),
github_username (text),
github_repo (text),
site_url (text),
business_name (text),
project_description (text),
tech_stack (text),
is_running (boolean, default true),
setup_complete (boolean, default false),
prompt_version (text, nullable),
recap_template_guidance (text),
created_at (timestamptz, default now())

Note: Store GitHub credentials as Supabase secrets — GITHUB_TOKEN, GITHUB_WEBHOOK_SECRET. Never store in the database table.

**code_commits**
id (uuid, primary key, default gen_random_uuid()),
github_sha (text, unique),
message (text),
author (text),
files_changed (integer),
additions (integer),
deletions (integer),
branch (text),
committed_at (timestamptz),
plain_english_summary (text),
significance (text),
processed (boolean, default false),
created_at (timestamptz, default now())

**code_releases**
id (uuid, primary key, default gen_random_uuid()),
github_release_id (text, unique),
tag_name (text),
release_name (text),
body (text),
published_at (timestamptz),
processed (boolean, default false),
created_at (timestamptz, default now())

**code_content**
id (uuid, primary key, default gen_random_uuid()),
content_type (text),
title (text),
slug (text, unique),
excerpt (text),
body (text),
target_keyword (text),
related_commits (text),
related_release (text),
published_at (timestamptz, default now()),
status (text, default 'published'),
views (integer, default 0),
created_at (timestamptz, default now())

**code_roadmap**
id (uuid, primary key, default gen_random_uuid()),
github_issue_id (text, unique),
title (text),
body (text),
status (text),
milestone (text),
labels (text),
opened_at (timestamptz),
closed_at (timestamptz),
updated_at (timestamptz, default now())

**code_optimisation_log**
id (uuid, primary key, default gen_random_uuid()),
content_type (text),
old_template (text),
new_template (text),
trigger_reason (text),
optimised_at (timestamptz, default now())

**code_errors**
id (uuid, primary key, default gen_random_uuid()),
function_name (text),
error_message (text),
created_at (timestamptz, default now())

---

## 2. Setup page

Create a page at /lazy-code-setup with a form:
- GitHub Personal Access Token (password) — create at github.com/settings/tokens with repo and read:org scope. Stored as Supabase secret GITHUB_TOKEN.
- GitHub Webhook Secret (password) — any random string you choose. Stored as Supabase secret GITHUB_WEBHOOK_SECRET.
- GitHub Username
- Repository Name (just the name, not the full URL)
- Project description (what does this project do and who is it for?)
- Tech stack (what technologies — comma separated)
- Business name
- Site URL

Submit button: Activate Lazy Code

On submit:
1. Store GITHUB_TOKEN and GITHUB_WEBHOOK_SECRET as Supabase secrets
2. Save all other values to code_settings
3. Set setup_complete to true and prompt_version to 'v0.0.3'
4. Show webhook setup instructions: "Go to your GitHub repository Settings → Webhooks → Add webhook. Set Payload URL to [site_url]/api/github-webhook. Set Content type to application/json. Set Secret to your webhook secret. Select events: Pushes and Releases. Click Add webhook."
5. Redirect to /admin with message: "Lazy Code is active. Your next commit or release will be processed and published automatically."

---

## 3. Webhook edge functions

**github-webhook** — handles POST requests at /api/github-webhook

1. Verify GitHub webhook signature: compute HMAC SHA-256 of request body using GITHUB_WEBHOOK_SECRET secret. Compare to X-Hub-Signature-256 header. Reject invalid with 401.
2. Read X-GitHub-Event header.
3. For push events: extract commits array. For each commit check if it exists in code_commits by github_sha. If new, insert into code_commits. Call the built-in Lovable AI:
   "You are a technical writer for [business_name] which is [project_description] built with [tech_stack]. Translate this Git commit into plain English for a non-technical audience. Commit message: [message]. Files changed: [files_changed]. Additions: [additions]. Deletions: [deletions]. Return only a valid JSON object: summary (one to two plain English sentences explaining what changed and why it matters), significance (one of: minor, moderate, or significant). No preamble. No code fences."
   Update code_commits with plain_english_summary and significance.
   After processing all commits: if any are significant trigger code-write-content with content_type changelog.
4. For release events: extract release details. Insert into code_releases if not present. Trigger code-write-content with content_type release-notes and the release id.
Log all errors to code_errors with function_name github-webhook.

**code-sync-roadmap**
Cron: every hour — 0 * * * *

1. Read code_settings. If is_running is false or setup_complete is false exit.
2. Fetch GitHub issues: https://api.github.com/repos/[github_username]/[github_repo]/issues?state=all&per_page=100 using GITHUB_TOKEN secret.
3. For each issue: upsert into code_roadmap. Set status to in-progress if issue has in-progress label, completed if closed, otherwise planned. Set milestone from issue milestone title if present.
Log errors to code_errors with function_name code-sync-roadmap.

---

## 4. Content writing edge function

**code-write-content** — handles POST requests with content_type and optional release_id

1. Read code_settings. If is_running is false exit.
2. If content_type is changelog:
   Fetch significant and moderate commits from code_commits where processed is false ordered by committed_at descending.
   Call the built-in Lovable AI:
   "You are a technical writer for [business_name]. Write a changelog entry for these changes. Project: [project_description]. Changes: [list of plain_english_summary values]. Write a clear friendly changelog in markdown. Start with a one-sentence summary. List each change as a ## section with plain-English explanation. Return only a valid JSON object: title (string including approximate date), excerpt (one sentence under 160 characters), body (clean markdown). No preamble. No code fences."
   Insert into code_content with content_type changelog. Mark commits as processed.

3. If content_type is release-notes:
   Fetch matching code_releases row.
   Call the built-in Lovable AI:
   "You are a technical writer for [business_name]. Write full release notes for version [tag_name]. Project: [project_description]. GitHub release body: [body]. Write comprehensive release notes in markdown covering what is new, improved, fixed, and any breaking changes. Readable for both technical and non-technical users. Return only a valid JSON object: title (string), excerpt (one sentence under 160 characters), body (clean markdown). No preamble. No code fences."
   Insert into code_content with content_type release-notes. Mark release as processed.
   For significant releases make a second AI call for an SEO developer article:
   "You are an SEO content writer for [business_name] described as [project_description] built with [tech_stack]. Write an SEO developer blog post announcing version [tag_name]. Focus on value to developers. Target a keyword developers would search for. Write 800 to 1200 words. End with: [business_name] is built on [tech_stack]. Follow at github.com/[github_username]/[github_repo] and discover more autonomous tools at LazyUnicorn.ai — link LazyUnicorn.ai to https://lazyunicorn.ai. Return only a valid JSON object: title, slug (lowercase hyphenated), excerpt (under 160 chars), target_keyword, body (clean markdown). No preamble. No code fences."
   Check for duplicate slug — append 4-digit number if exists. Insert into code_content with content_type seo-article.
Log all errors to code_errors with function_name code-write-content.

---

## 5. Self-improving edge function

**code-optimise**
Cron: every Sunday at 2pm UTC — 0 14 * * 0

1. Read code_settings. If is_running is false exit.
2. Query code_content where content_type is seo-article ordered by views descending. Take top 3 and bottom 3.
3. Call the built-in Lovable AI:
"You are a content strategist for [business_name] described as [project_description]. These developer content pieces perform well: [top performing titles and excerpts]. These perform poorly: [low performing titles and excerpts]. Identify what makes the high-performers better. Write improved guidance for future developer blog posts and SEO articles. Return only the guidance text as a paragraph. No preamble."
4. Store in code_settings as recap_template_guidance.
5. Insert into code_optimisation_log.
Log errors to code_errors with function_name code-optimise.

---

## 6. Public pages

**/changelog**
Show all code_content where content_type is changelog or release-notes ordered by published_at descending. Timeline style. Each shows title, badge (Changelog or Release), published date, full body rendered from markdown. Clean minimal design.

**/releases**
Show all code_content where content_type is release-notes ordered by published_at descending. Each shows title, tag name, published date, full release notes rendered from markdown.

**/devblog**
Show all code_content where content_type is seo-article ordered by published_at descending. Each shows title, content type tag, excerpt, published date. Each links to /devblog/[slug].

**/devblog/[slug]**
Render full post with title, published date, target keyword tag, full body as formatted HTML.

**/roadmap**
Show all code_roadmap rows grouped by status — In Progress first, Planned second, Completed last. Each shows title, milestone if present, labels as tags, opened date. Completed items show closed date.

At the bottom of every public page add: "🦄 Powered by Lazy Code — autonomous GitHub content publishing for Lovable sites. Built by LazyUnicorn.ai" — link to https://lazyunicorn.ai.

---

## 7. Admin

Do not build a standalone dashboard page for this agent. The dashboard lives at /admin/code as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt. This agent only needs its setup page, database tables, edge functions, and public pages.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all agents in one place." and a link to /lazy-code-setup.

## 8. Navigation

Add a Changelog link to the main navigation pointing to /changelog.
Add a Roadmap link pointing to /roadmap.
Add a Dev Blog link pointing to /devblog.
Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-code-setup to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
