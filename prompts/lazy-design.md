# Lazy Design

> Category: 🛠️ Dev · Version: 0.0.1

## Prompt

````
# lazy-design — v0.0.6

[Lazy Design Prompt — v0.0.6 — LazyUnicorn.ai]

Add a design upgrade engine called Lazy Design to this project. It automatically improves the visual design of your Lovable site by fetching pre-built UI components from 21st.dev and upgrading your pages section by section — hero, navigation, testimonials, features, CTA, and footer — without you browsing component libraries or writing design prompts manually.

Note: Lazy Design uses the 21st.dev component library and the built-in Lovable AI. No API keys required.

---

1. Database

Create these Supabase tables with RLS enabled:

design_settings: id (uuid, primary key, default gen_random_uuid()), brand_name (text), site_url (text), colour_scheme (text, default 'dark' — one of dark, light, bold, minimal), accent_colour (text, default '#f5c842'), font_style (text, default 'modern' — one of modern, editorial, technical, friendly), upgrade_frequency (text, default 'manual' — one of manual, weekly, monthly), auto_apply (boolean, default false), is_running (boolean, default true), setup_complete (boolean, default false), prompt_version (text, nullable), created_at (timestamptz, default now())

design_pages: id (uuid, primary key, default gen_random_uuid()), page_path (text), page_name (text), sections_detected (text), last_audited (timestamptz), upgrade_status (text, default 'pending' — one of pending, audited, upgraded), created_at (timestamptz, default now())

design_upgrades: id (uuid, primary key, default gen_random_uuid()), page_id (uuid), section_type (text — one of hero, navigation, testimonials, features, cta, footer, form, pricing), component_name (text), component_source_url (text), prompt_used (text), status (text, default 'suggested' — one of suggested, applied, rejected), applied_at (timestamptz), created_at (timestamptz, default now())

design_errors: id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), created_at (timestamptz, default now())

---

2. Setup page

Create a page at /lazy-design-setup.

Welcome message: 'Lovable builds your site. 21st.dev makes it beautiful. Lazy Design connects the two — automatically upgrading your hero, navigation, testimonials, and more with pre-built components that match your brand.'

Form fields:
- Brand name (text)
- Site URL (text)
- Colour scheme (select: Dark — near black background, light text / Light — white background, dark text / Bold — strong colour, white text / Minimal — clean white with one accent)
- Accent colour (colour picker, default #f5c842 gold)
- Font style (select: Modern — clean sans-serif / Editorial — serif headings / Technical — monospace elements / Friendly — rounded and approachable)
- Pages to upgrade — a checklist of detected pages. On load call design-audit to detect all routes in this project and display them as checkboxes. Default check: homepage, about, pricing, landing pages. Exclude: admin routes, setup pages, dashboard pages.
- Upgrade frequency (select: Manual only — I will trigger upgrades myself / Weekly — upgrade one section per week / Monthly — full design review monthly)
- Auto-apply upgrades (toggle, default off) — if on upgrades are applied automatically. If off upgrades are suggested and require your approval from the dashboard before applying.

Submit button: Start Upgrading

On submit:
1. Save all values to design_settings
2. Set setup_complete to true and prompt_version to 'v0.0.2'
3. For each checked page insert a row into design_pages
4. Immediately call design-audit for each checked page
5. Fire and forget — immediately before redirecting, send an install ping (do not await, wrap in try/catch so it never blocks): try { fetch('https://lazyunicorn.ai/api/register-install', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ engine: 'Lazy Design', version: '0.0.6', site_url: site_url }) }) } catch(e) {}
6. Redirect to /admin with message: 'Lazy Design is running. Your site is being audited. Upgrade suggestions will appear in your dashboard.'

---

3. Edge functions

design-audit
Triggered on setup and on schedule. Accepts page_id or runs for all design_pages where upgrade_status is pending.

1. Read design_settings. If is_running is false or setup_complete is false exit.
2. For each page to audit call the built-in Lovable AI:
'You are a UI/UX auditor reviewing a Lovable site page at [page_path] for [brand_name]. The site uses a [colour_scheme] colour scheme with accent colour [accent_colour] and [font_style] typography. Review the typical structure of a [page_name] page and identify which of these section types are likely present and could be upgraded with a pre-built component from 21st.dev: hero, navigation, testimonials, features, cta, footer, form, pricing. For each section present return the section type, a one-sentence description of what the current section likely looks like generically, and why a 21st.dev component upgrade would improve it. Return only a valid JSON array where each item has: section_type (string), current_description (string), upgrade_reason (string). No preamble. No code fences.'
3. Parse the response. Update design_pages with sections_detected and last_audited. Set upgrade_status to audited.
4. For each detected section call design-generate-suggestion with the page_id and section_type.
Log errors to design_errors with function_name design-audit.

design-generate-suggestion
Triggered by design-audit. Accepts page_id and section_type.

1. Read design_settings and the design_pages row.
2. Call the built-in Lovable AI to generate a 21st.dev component selection and a ready-to-paste Lovable prompt:
'You are a Lovable prompt engineer specialising in 21st.dev component integration. The site is for [brand_name] — a [colour_scheme] themed site with [accent_colour] accent and [font_style] typography. You need to upgrade the [section_type] section on the [page_name] page.

21st.dev has these component categories relevant to [section_type]:
- hero: animated heroes, gradient heroes, split heroes, video heroes, minimal heroes
- navigation: sticky navbars, transparent navbars, sidebar navs, mega menus
- testimonials: card grids, marquee scrollers, avatar testimonials, rating displays
- features: icon grids, alternating rows, bento grids, comparison tables
- cta: banner CTAs, centred CTAs, split CTAs, floating CTAs
- footer: minimal footers, link-heavy footers, newsletter footers, dark footers
- form: contact forms, waitlist forms, multi-step forms, inline forms
- pricing: toggle pricing, comparison cards, featured tier pricing

Write a specific Lovable prompt that:
1. Instructs the user to go to 21st.dev and search for [specific search term relevant to the section and style]
2. Tells them exactly what to look for — describe the ideal component visually
3. Explains how to select the Lovable prompt type on 21st.dev
4. Tells them exactly where to place the component in their project
5. Includes the brand colours [accent_colour] and tone [colour_scheme] for the component to inherit

Also write an AI-powered fallback: if the user cannot find a suitable component on 21st.dev, a complete self-contained prompt that builds the section from scratch matching the [colour_scheme] theme and [accent_colour] accent using Tailwind CSS and Framer Motion animations.

Return only a valid JSON object: component_name (string — descriptive name), search_term (string — what to search on 21st.dev), prompt_with_21stdev (string — the full prompt using 21st.dev), prompt_fallback (string — the self-contained build prompt). No preamble. No code fences.'

3. Parse response. Insert into design_upgrades with status suggested, page_id, section_type, component_name, component_source_url set to https://21st.dev/search?q=[search_term], prompt_used set to prompt_with_21stdev.
4. If auto_apply is true and status is suggested automatically call design-apply with the upgrade id.
Log errors to design_errors with function_name design-generate-suggestion.

design-apply
Triggered manually from dashboard or automatically if auto_apply is true. Accepts upgrade_id.

1. Read design_settings and the design_upgrades row.
2. Call the built-in Lovable AI with the stored prompt_used. This instructs Lovable to fetch the 21st.dev component or build the fallback and place it on the correct page.
3. Update design_upgrades status to applied, set applied_at to now.
4. Update the parent design_pages upgrade_status to upgraded.
Log errors to design_errors with function_name design-apply.

design-weekly-upgrade
Cron: every Monday at 10am UTC — 0 10 * * 1 (only runs if upgrade_frequency is weekly or monthly)

1. Read design_settings. If is_running false or upgrade_frequency is manual exit. If monthly only run on first Monday of the month.
2. Query design_upgrades where status is suggested ordered by created_at ascending. Take the first one — upgrade one section per run.
3. Call design-apply with that upgrade id.
4. If slack_webhook_url is set in any other engine settings send a Slack notification: 'Lazy Design upgraded your [section_type] section on [page_name]. View it at [site_url][page_path].'
Log errors to design_errors with function_name design-weekly-upgrade.

---

4. Admin dashboard section

Do not build a standalone dashboard. The Lazy Design dashboard lives at /admin/design as part of the unified LazyUnicorn admin panel.

If /admin does not yet exist add a placeholder at /admin pointing to /lazy-design-setup.

The /admin/design page should show:
- A page selector dropdown showing all design_pages
- For each selected page: a list of design_upgrades grouped by section_type
- Each upgrade card shows: section type badge, component name, status badge (suggested/applied/rejected), the prompt that will be used (collapsed, expand on click), and three buttons: Apply Now (calls design-apply), Preview Prompt (shows the full prompt in a modal for manual use), Reject (updates status to rejected)
- An Audit All Pages button that calls design-audit for all pages
- An Add Page button that adds a new design_pages row and triggers audit
- Error log from design_errors

---

5. Navigation

Add an Admin link to the main site navigation pointing to /admin.
Do not add /lazy-design-setup to public navigation.

## Backlink Badge
Add a small "Powered by Lazy Unicorn" backlink badge in the footer of every public-facing page. Use this exact HTML:
<a href="https://www.lazyunicorn.ai" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#0a0a08;color:#f0ead6;font-family:'Space Grotesk',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;border:1px solid rgba(240,234,214,0.2)">🦄 Powered by Lazy Unicorn</a>
Style it to sit at the bottom of the page footer, centered, with subtle opacity (60%) that increases to 100% on hover.
````

---
*Auto-synced from [Lazy Unicorn](https://lazyunicorn.co)*
