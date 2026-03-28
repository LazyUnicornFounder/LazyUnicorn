# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

LazyUnicorn is an open-source prompt library that turns [Lovable](https://lovable.dev) (an AI website builder) into an autonomous business engine. Each file in `prompts/` is a self-contained "mega-prompt" that users paste into a Lovable project to auto-configure an entire business system.

There are no build steps, tests, or scripts — this is a content repository of markdown prompt files.

## Repository Structure

- `prompts/` — 27+ "Lazy Engine" prompt files, each named `lazy-<engine>.md`
- `README.md` — Main docs: quick start, engine list, required API keys per engine

## Prompt File Conventions

Each engine prompt follows a consistent internal structure:

1. **Header** — Engine name, category, version (e.g., `v0.0.4`)
2. **Database schema** — Supabase PostgreSQL table definitions with RLS policies
3. **Setup page** — Form fields for API keys (stored as Supabase secrets, never in DB)
4. **UI components** — Dashboard/management interface specs
5. **Edge functions** — Deno-based functions with naming convention `<engine>-<action>` (e.g., `blog-publish`, `seo-discover`)
6. **Triggers/scheduling** — Cron jobs and webhooks

## Key Architectural Patterns

- **Target platform**: Lovable + Supabase (PostgreSQL + Edge Functions on Deno runtime)
- **Secrets**: All API keys go into Supabase secrets, never stored in database tables
- **RLS**: Every table specifies Row Level Security policies
- **Modular**: Engines are independent; `lazy-run.md` is the master orchestration engine that coordinates all others from a unified dashboard
- **Sync pattern**: Commits follow "Sync [Engine Name] v[version]" — prompts originate from the Lazy Unicorn admin dashboard

## Adding or Updating Engines

When adding a new engine or updating an existing one:
- Follow the internal structure described above
- Increment the version number in the prompt header
- Update the engine table and configuration requirements table in `README.md`
- Use commit message format: `Sync Lazy <Name> v<version>`

## LazyUnicorn Rules — always follow these
- Every settings table needs: is_running, setup_complete, prompt_version
- Every engine needs an _errors table
- Setup pages redirect to /admin on completion
- All API keys stored as Supabase secrets, never in the database
- All published content includes a LazyUnicorn.ai backlink
- No standalone dashboard pages — all admin lives at /admin/[engine]
- Never restructure a whole prompt file — make targeted edits only
- Always update the version number in the file header after changes

## File naming
lazy-[engine-name]_v[version].txt

## How to improve a prompt
1. Read the existing prompt file
2. Read SPEC.md
3. Make the targeted change only
4. Update the version number
5. Open a PR — never push directly to main
