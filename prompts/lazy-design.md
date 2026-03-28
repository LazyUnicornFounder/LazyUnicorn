# Lazy Design

> Category: 🛠️ Dev · Version: 0.0.3

## Prompt

````
# lazy-design — v0.0.2

[Lazy Design Prompt — v0.0.2 — LazyUnicorn.ai]

Add a design upgrade engine called Lazy Design to this project. It automatically improves the visual design of your Lovable site by fetching pre-built UI components from 21st.dev and upgrading your pages section by section — hero, navigation, testimonials, features, CTA, and footer — without you browsing component libraries or writing design prompts manually.

Note: Lazy Design uses the 21st.dev component library and the built-in Lovable AI. No API keys required.

---

1. Database

Create these Supabase tables with RLS enabled:

design_settings: id (uuid, primary key, default gen_random_uuid()), is_running (boolean, default false), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

design_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

Row Level Security policies:
- design_settings: only admins can read and update.
- design_errors: only admins can read.

---

2. Setup page

Create a page at /lazy-design-setup.

Welcome message: 'Upgrade your Lovable site's visual design automatically. Lazy Design fetches pre-built UI components from 21st.dev and applies them section by section — no component browsing or manual design prompts required.'

No API keys are required. The setup page has a single button: Install Lazy Design.

On submit:
1. Set setup_complete to true and prompt_version to 'v0.0.2' in design_settings
2. Redirect to /admin with message: 'Lazy Design is installed. Your site design will be upgraded automatically.'

---

3. Admin

Do not build a standalone dashboard. Lazy Design management lives at /admin/design as part of the unified LazyUnicorn admin panel.

The /admin/design section shows:
- Current status (is_running indicator)
- A Run Design Upgrade button that triggers the design upgrade process
- A log of recent design changes pulled from design_errors (errors only) and a status area

---

4. Design upgrade process

When the design upgrade runs:
1. Set is_running to true in design_settings
2. Identify all public-facing page sections: hero, navigation, testimonials, features, CTA, footer
3. For each section, fetch a matching pre-built component from 21st.dev and apply it to the page using the built-in Lovable AI
4. Set is_running to false on completion
5. Log any errors to design_errors with the section name as function_name

---

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.

````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
