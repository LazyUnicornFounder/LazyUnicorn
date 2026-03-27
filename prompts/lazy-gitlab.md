# Lazy GitLab

> Category: 🛠️ Dev · Version: 0.0.5

## Prompt

````
[Lazy GitLab Prompt — v0.0.5 — LazyUnicorn.ai]

Add a complete autonomous GitLab content engine called Lazy GitLab to this project. It monitors a GitLab repository via webhooks, processes commits and merge requests, writes plain-English changelogs, release notes, developer blog posts, SEO articles, and maintains a public roadmap — all automatically with no manual input required after setup. Mirrors the Lazy Code engine but for GitLab.

---

MARKETING PAGE PROMPT — paste into LazyUnicorn project:

Add a new page at /lazy-gitlab. It is a marketing and landing page for a product called Lazy GitLab — an autonomous GitLab content engine that installs into any existing Lovable project with one prompt.

Hero section
Headline: 'One prompt turns every GitLab commit into a changelog, release notes, and a developer blog post — automatically.' Subheading: 'Lazy GitLab monitors your GitLab repository, reads your commits and merge requests, and publishes plain-English changelogs, release notes, SEO developer posts, and a public roadmap to your Lovable site — every time you push.' Primary button: Copy the Lovable Prompt. Secondary button: See How It Works. Badge: Powered by GitLab.

How it works section
Headline: Push to GitLab. Lazy GitLab handles the rest. Four steps: 1. Copy the setup prompt. 2. Paste into your Lovable project. 3. Add your GitLab credentials. 4. Push code as normal — changelog, release notes, and blog posts publish automatically.

What it installs section
Headline: Every commit becomes content. Eight cards: 1. Changelog — plain-English summary of every meaningful commit. 2. Release notes — written automatically for every tagged release. 3. Developer blog posts — a technical post for every significant feature. 4. Merge request summaries — every merged MR summarised in plain English. 5. Public roadmap — maintained from GitLab issues and milestones automatically. 6. SEO developer content — keyword-targeted articles from your commits. 7. Webhook handler — listens for GitLab push, merge, and release events. 8. Self-improving content — monitors which posts drive the most traffic and improves the writing template.

Pricing section
Two cards: Free — self-hosted, bring your own GitLab account. Pro at $19/month — coming soon.

Bottom CTA
Headline: Your commits are content. Lazy GitLab publishes them. Primary button: Copy the Lovable Prompt.

Navigation: Add Lazy GitLab to the LazyUnicorn navigation.

---

SETUP PROMPT — paste into user's Lovable project:

Add a complete autonomous GitLab content engine called Lazy GitLab to this project. It monitors a GitLab repository via webhooks, processes commits, merge requests, and releases, writes plain-English changelogs, release notes, developer blog posts, and SEO articles, and maintains a public roadmap — all automatically.

1. Database
Create these Supabase tables with RLS enabled:

gitlab_settings: id (uuid, primary key, default gen_random_uuid()), gitlab_username (text), gitlab_project_id (text), gitlab_project_path (text), site_url (text), business_name (text), project_description (text), tech_stack (text), is_running (boolean, default true), setup_complete (boolean, default false),
prompt_version (text, nullable), recap_template_guidance (text), created_at (timestamptz, default now()).
Note: Store GITLAB_TOKEN and GITLAB_WEBHOOK_SECRET as Supabase secrets. Never in the database.

gitlab_commits: id (uuid, primary key, default gen_random_uuid()), gitlab_sha (text, unique), message (text), author (text), files_changed (integer), branch (text), committed_at (timestamptz), plain_english_summary (text), significance (text), processed (boolean, default false), created_at (timestamptz, default now()).

gitlab_merge_requests: id (uuid, primary key, default gen_random_uuid()), gitlab_mr_id (text, unique), title (text), description (text), author (text), state (text), merged_at (timestamptz), source_branch (text), target_branch (text), plain_english_summary (text), processed (boolean, default false), created_at (timestamptz, default now()).

gitlab_releases: id (uuid, primary key, default gen_random_uuid()), gitlab_release_id (text, unique), tag_name (text), release_name (text), description (text), released_at (timestamptz), processed (boolean, default false), created_at (timestamptz, default now()).

gitlab_content: id (uuid, primary key, default gen_random_uuid()), content_type (text — one of changelog, release-notes, mr-summary, blog-post, seo-article), title (text), slug (text, unique), excerpt (text), body (text), target_keyword (text), published_at (timestamptz, default now()), status (text, default 'published'), views (integer, default 0), created_at (timestamptz, default now()).

gitlab_roadmap: id (uuid, primary key, default gen_random_uuid()), gitlab_issue_id (text, unique), title (text), body (text), status (text — one of planned, in-progress, completed), milestone (text), labels (text), opened_at (timestamptz), closed_at (timestamptz), updated_at (timestamptz, default now()).

gitlab_optimisation_log: id (uuid, primary key, default gen_random_uuid()), content_type (text), old_template (text), new_template (text), optimised_at (timestamptz, default now()).

gitlab_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now()).

2. Setup page
Create a page at /lazy-gitlab-setup with a form:
- GitLab Personal Access Token (password) — create at gitlab.com/-/profile/personal_access_tokens with api scope. Stored as Supabase secret GITLAB_TOKEN.
- GitLab Webhook Secret (password) — any random string. Stored as Supabase secret GITLAB_WEBHOOK_SECRET.
- GitLab Username
- Project ID or path (e.g. username/my-project)
- Project description
- Tech stack (comma separated)
- Business name
- Site URL

Submit button: Activate Lazy GitLab

On submit:
1. Store GITLAB_TOKEN and GITLAB_WEBHOOK_SECRET as Supabase secrets
2. Save all other values to gitlab_settings
3. Set setup_complete to true and prompt_version to 'v0.0.1'
4. Show instructions: Go to your GitLab project, Settings → Webhooks → Add new webhook. Set URL to [site_url]/api/gitlab-webhook. Set Secret Token to your webhook secret. Select Push events, Tag push events, Merge request events, Releases events. Click Add webhook.
5. Redirect to /admin with message: Lazy GitLab is active. Your next commit will be processed and published automatically.

3. Webhook edge function
Create a Supabase edge function called gitlab-webhook handling POST requests at /api/gitlab-webhook.

1. Verify the GitLab webhook token: compare the X-Gitlab-Token header to GITLAB_WEBHOOK_SECRET secret. Reject mismatches with 401.
2. Read the X-Gitlab-Event header.
3. For Push Hook events: extract commits array. For each commit check if it exists in gitlab_commits by gitlab_sha. If new insert into gitlab_commits. Call the built-in Lovable AI:
'You are a technical writer for [business_name] which is [project_description] built with [tech_stack]. Translate this GitLab commit into plain English. Commit message: [message]. Branch: [branch]. Return only a valid JSON object: summary (one to two plain English sentences), significance (one of minor, moderate, or significant). No preamble. No code fences.'
Update gitlab_commits with summary and significance. After processing all commits if any are significant trigger gitlab-write-content with content_type changelog.
4. For Merge Request Hook events where object_attributes.state is merged: insert into gitlab_merge_requests if not present. Trigger gitlab-write-content with content_type mr-summary and the MR id.
5. For Release Hook events: insert into gitlab_releases if not present. Trigger gitlab-write-content with content_type release-notes and the release id.
Log all errors to gitlab_errors with function_name gitlab-webhook.

Create a Supabase edge function called gitlab-sync-roadmap. Cron: every hour — 0 * * * *
1. Read gitlab_settings. If is_running is false or setup_complete is false exit.
2. Fetch issues from GitLab API: https://gitlab.com/api/v4/projects/[gitlab_project_id]/issues?state=all&per_page=100 using GITLAB_TOKEN secret.
3. For each issue upsert into gitlab_roadmap. Set status to in-progress if issue has in-progress label, completed if state is closed, otherwise planned.
Log errors to gitlab_errors with function_name gitlab-sync-roadmap.

4. Content writing edge function
Create a Supabase edge function called gitlab-write-content handling POST requests with content_type and optional release_id or mr_id.

1. Read gitlab_settings. If is_running is false exit.
2. If content_type is changelog: fetch significant and moderate commits where processed is false. Call the built-in Lovable AI to write a changelog entry. Insert into gitlab_content with content_type changelog. Mark commits as processed.
3. If content_type is mr-summary: fetch the matching gitlab_merge_requests row. Call the built-in Lovable AI:
'You are a technical writer for [business_name]. Write a plain-English merge request summary for: title [title], description [description], from branch [source_branch] to [target_branch]. Explain what changed and why it matters. Return only a valid JSON object: title (string), excerpt (under 160 chars), body (clean markdown 300 to 600 words). No preamble. No code fences.'
Insert into gitlab_content with content_type mr-summary. Mark MR as processed.
4. If content_type is release-notes: fetch the matching gitlab_releases row. Write comprehensive release notes and an SEO article. Insert both into gitlab_content. Mark release as processed.
Log all errors to gitlab_errors with function_name gitlab-write-content.

5. Self-improving edge function
Create a Supabase edge function called gitlab-optimise. Cron: every Sunday at 2pm UTC — 0 14 * * 0
Query gitlab_content where content_type is seo-article ordered by views descending. Take top 3 and bottom 3. Use the built-in Lovable AI to identify what makes high performers better and write improved guidance. Store in gitlab_settings as recap_template_guidance. Insert into gitlab_optimisation_log.
Log errors to gitlab_errors with function_name gitlab-optimise.

6. Public pages
/gitlab-changelog — all gitlab_content where content_type is changelog or release-notes. Timeline style with badges.
/gitlab-devblog — all gitlab_content where content_type is seo-article or blog-post. Links to /gitlab-devblog/[slug].
/gitlab-devblog/[slug] — full post rendered from markdown.
/gitlab-roadmap — all gitlab_roadmap rows grouped by status — In Progress, Planned, Completed.
At the bottom of every page add: 🦄 Powered by Lazy GitLab — autonomous GitLab content publishing for Lovable sites. Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

7. Admin

Do not build a standalone dashboard page for this engine. The dashboard lives at /admin/gitlab as part of the unified LazyUnicorn admin panel, which is built separately using the LazyUnicorn Admin Dashboard prompt.

If /admin does not yet exist on this project add a simple placeholder at /admin with the text: "Install the LazyUnicorn Admin Dashboard to manage all engines in one place." and a link to /lazy-gitlab-setup.

8. Navigation
Add Changelog link to /gitlab-changelog. Add Roadmap link to /gitlab-roadmap. Add an Admin link to the main site navigation pointing to /admin.
Do not add the setup page to public navigation.


## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
