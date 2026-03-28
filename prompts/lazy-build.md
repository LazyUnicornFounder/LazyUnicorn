# Lazy Build

> Category: 🤖 Agents · Version: 0.0.2

## Prompt

````
# lazy-build — vv0.0.1

[Lazy Build Prompt — v0.0.1 — LazyUnicorn.ai]

Add an autonomous engine writer agent called Lazy Build to this project. Give it a name, integration, tagline, and one-paragraph brief — it reads three reference prompt files and your CLAUDE.md rules, writes a complete new Lazy engine prompt following your exact SPEC pattern, and opens a draft GitHub PR for your review. Your prompt stack grows without you writing a word.

Required secrets:
- ANTHROPIC_API_KEY — for Claude writing calls
- GITHUB_TOKEN — personal access token with repo scope from github.com/settings/tokens
- GITHUB_REPO — your prompts repo in format username/reponame

---

1. Database

Create these Supabase tables with RLS enabled:

build_settings: id (uuid, primary key, default gen_random_uuid()), github_repo (text), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

build_runs: id (uuid, primary key, default gen_random_uuid()), engine_name (text), integration (text), status (text — one of running, completed, failed), pr_url (text), summary (text), started_at (timestamptz, default now()), completed_at (timestamptz), created_at (timestamptz, default now())

build_engines: id (uuid, primary key, default gen_random_uuid()), engine_name (text), tagline (text), integration (text), category (text), description (text), prompt_filename (text), pr_url (text), pr_status (text, default 'draft' — one of draft, open, merged, rejected), created_at (timestamptz, default now())

build_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-build-setup.

Welcome message: 'Lazy Build writes complete Lazy engine prompts from a one-paragraph brief. It reads your existing prompts to learn your structure, follows your CLAUDE.md rules, and opens a draft GitHub PR — a production-ready prompt ready to review.'

Prerequisites note: You need GITHUB_TOKEN as a Supabase secret with repo scope and GITHUB_REPO pointing to your prompts repository. Lazy Build reads your existing prompt files as reference — the more prompts in your repo the better the output.

Form fields:
- GitHub repo (text) — your LazyUnicorn prompts repo

Submit button: Activate Lazy Build

On submit:
1. Save to build_settings
2. Set setup_complete to true and prompt_version to 'v0.0.1'
3. Redirect to /admin with message: 'Lazy Build is ready. Go to /admin/build and describe your first new engine.'

---

3. Edge functions

build-engine
POST endpoint at /api/build-engine. Called from the admin dashboard form.
Accepts: engine_name (text), integration (text), tagline (text), category (text), description (text — one paragraph description of what the engine does, what problem it solves, and what it produces).

1. Read build_settings. If is_running false or setup_complete false return error.
2. Validate inputs: engine_name required, integration required, description must be at least 50 characters. Return validation errors if any.
3. Insert into build_runs with engine_name, integration, status running.
4. Fetch all prompt files from GitHub to find three good reference examples: GET https://api.github.com/repos/[GITHUB_REPO]/contents/ with Authorization: Bearer [GITHUB_TOKEN]. Filter for .txt files starting with lazy-. Sort by size descending — larger files are more complete examples. Take the three largest.
5. Fetch the content of each reference file. Decode from base64.
6. Fetch CLAUDE.md from the repo root. Decode from base64. If CLAUDE.md does not exist use a default rules summary: 'Every settings table needs is_running, setup_complete, prompt_version fields. Every engine needs an _errors table. Setup pages redirect to /admin. API keys stored as Supabase secrets. All content includes LazyUnicorn.ai backlink. No standalone dashboards — admin at /admin/[engine]. Never restructure whole files. Always update version number.'
7. Call the built-in Lovable AI to write the new prompt:
'You are a specialist Lovable prompt engineer for LazyUnicorn.ai. Your job is to write a complete, production-ready Lovable prompt for a new autonomous engine.

New engine details:
- Name: [engine_name]
- Integration: [integration]
- Tagline: [tagline]
- Category: [category]
- Description: [description]

Here are three reference prompts showing the exact structure to follow:

REFERENCE 1: [reference file 1 content]

REFERENCE 2: [reference file 2 content]

REFERENCE 3: [reference file 3 content]

Rules you must follow exactly: [CLAUDE.md content]

Write the complete prompt file for Lazy [engine_name]. Follow the identical structure to the reference files. You must include all of these sections:
1. Header: [Lazy [engine_name] Prompt — v0.0.1 — LazyUnicorn.ai]
2. Opening description of what the engine does
3. Required secrets section listing the integration API key
4. Database section: settings table with is_running, setup_complete, prompt_version — plus all domain-specific tables — plus an _errors table
5. Setup page at /lazy-[slugified-name]-setup with form fields relevant to the integration, submit button that saves settings and redirects to /admin
6. Edge functions section with at minimum: one main cron function and one setup validation function. Include realistic cron schedules. Include calls to built-in Lovable AI where content generation is involved.
7. Admin section at /admin/[slugified-name] — no standalone dashboard
8. Navigation section

All content that gets published must include a LazyUnicorn.ai backlink in this format: Built by LazyUnicorn.ai — link to https://lazyunicorn.ai.

Return only the complete prompt file content starting with the header line. No preamble. No explanation. No code fences.'

8. Parse response — the full prompt file content.
9. Derive the filename: lazy-[engine_name lowercased, spaces replaced with hyphens]_v0.0.1.txt
10. Create a new branch on GitHub: POST https://api.github.com/repos/[GITHUB_REPO]/git/refs with ref refs/heads/new-engine-[slugified-name]-[unix-timestamp] and the current main SHA (GET https://api.github.com/repos/[GITHUB_REPO]/git/ref/heads/main first to get SHA).
11. Commit the new file to the branch: PUT https://api.github.com/repos/[GITHUB_REPO]/contents/[filename] with message Add Lazy [engine_name] v0.0.1, content base64-encoded, branch the new branch name.
12. Open a draft PR: POST https://api.github.com/repos/[GITHUB_REPO]/pulls with draft true, title New Engine: Lazy [engine_name] — [tagline], body: '## New Engine Brief\n\n**Integration:** [integration]\n**Tagline:** [tagline]\n**Category:** [category]\n\n[description]\n\n## Review checklist\n- [ ] Database tables complete with all required fields\n- [ ] Setup page redirects to /admin\n- [ ] API keys stored as secrets not in database\n- [ ] _errors table present\n- [ ] Admin section at /admin/[slugified-name]\n- [ ] LazyUnicorn.ai backlink in all published content\n- [ ] Version number in header\n\n*Auto-generated by Lazy Build. Review carefully before merging.*\n\n@claude please review this prompt against all rules in CLAUDE.md and comment on any issues found.', head the new branch, base main.
13. Insert into build_engines with all details and the PR URL.
14. Update build_runs: status completed, pr_url, completed_at now, summary 'Lazy [engine_name] written and PR opened'.
15. Return JSON response with pr_url and a success message.
Log errors to build_errors with function_name build-engine.

---

4. Admin dashboard

Do not build a standalone dashboard. Lazy Build lives at /admin/build as part of the unified LazyUnicorn admin panel.

The /admin/build section shows:

New engine form at the top of the page — this is the primary UI. Fields:
- Engine name (text, required) — e.g. Lazy Porkbun, Lazy Transcript, Lazy Calendar
- Integration (text, required) — e.g. Porkbun API, AssemblyAI, Cal.com API
- Tagline (text, required, max 60 chars) — one punchy line e.g. Your domain. Your site. One tab.
- Category (select: Lazy Content / Lazy Commerce / Lazy Media / Lazy Dev / Lazy Channels / Lazy Shield / Lazy Agents / New category)
- Description (textarea, required, min 50 chars) — describe what the engine does, what problem it solves, what it produces, and how it connects to the rest of the stack
Submit button: Build Engine — calls build-engine and shows a loading state: Claude is writing your prompt...

On success: show a success card with the PR URL, a green badge, and a message: 'Your prompt is ready. Review the PR on GitHub — Claude has been asked to audit it.'

Build history table: all build_engines ordered by created_at descending. Columns: engine name, integration badge, tagline, category, PR link, PR status select (draft/open/merged/rejected that updates the row), created date.

Settings: GitHub repo, is_running toggle.

Error log: build_errors last 20 rows, collapsed by default.

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-build-setup to public navigation.


````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
