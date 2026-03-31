# Infinity PPP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Infinity PPP — a global, public-facing PPP project directory with AI-powered ingestion, a Mapbox map, and an admin curation panel.

**Architecture:** Supabase holds all data (6 tables) and runs 4 edge functions for ingestion, enrichment, geocoding, and deduplication. Lovable builds the React SPA for both the public directory and admin panel. Confidence scoring auto-publishes high-quality records and routes uncertain ones to a human review queue.

**Tech Stack:** Lovable (React SPA), Supabase (Postgres + Edge Functions + Auth), Mapbox GL JS, World Bank PPI API, IsDB API.

---

## File / Component Map

| Component | Responsibility |
|---|---|
| Supabase: `ppp_projects` | Live published project records |
| Supabase: `ppp_raw` | Staging table for all ingested records |
| Supabase: `ppp_review_queue` | Low-confidence records pending human review |
| Supabase: `ppp_sources` | Configurable source registry |
| Supabase: `ppp_errors` | Error log for ingestion and enrichment |
| Supabase: `ppp_settings` | Single-row config (thresholds, toggles) |
| Supabase Edge Fn: `ppp-crawl` | Daily crawl of all active sources |
| Supabase Edge Fn: `ppp-enrich` | AI enrichment + confidence scoring + routing |
| Supabase Edge Fn: `ppp-geocode` | Resolves lat/lng for projects missing coordinates |
| Supabase Edge Fn: `ppp-dedup` | Weekly duplicate detection |
| Lovable: Homepage `/` | Hero, stats bar, map, filter bar, project grid |
| Lovable: `/projects/[id]` | Project detail — all fields, timeline, parties, map pin |
| Lovable: `/admin` | Protected admin shell with nav |
| Lovable: `/admin/queue` | Review queue — approve/reject low-confidence records |
| Lovable: `/admin/projects` | Projects table — inline edit, manual entry |
| Lovable: `/admin/sources` | Sources CRUD + crawl-now trigger |
| Lovable: `/admin/runs` | Run controls, run history, error log |
| Lovable: `/admin/settings` | Confidence threshold, auto-publish toggle |

---

## Phase 1 — Foundation

### Task 1: Supabase — Create all tables

**Files:**
- Run in Supabase SQL Editor

- [ ] **Step 1: Open Supabase SQL Editor and run the full schema**

```sql
-- ppp_settings (single-row config)
create table ppp_settings (
  id uuid primary key default gen_random_uuid(),
  confidence_threshold numeric default 0.8,
  auto_publish_enabled boolean default true,
  is_running boolean default true,
  prompt_version text,
  created_at timestamptz default now()
);

insert into ppp_settings (confidence_threshold, auto_publish_enabled, is_running, prompt_version)
values (0.8, true, true, 'v0.0.1');

-- ppp_sources
create table ppp_sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  url text not null,
  type text not null check (type in ('api', 'scrape', 'manual')),
  region text,
  is_active boolean default true,
  last_crawled_at timestamptz,
  crawl_frequency_hours integer default 24,
  record_count integer default 0,
  created_at timestamptz default now()
);

-- ppp_projects (live directory)
create table ppp_projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  country text,
  region text,
  sector text check (sector in ('energy','transport','water','health','education','telecoms','social infrastructure')),
  status text check (status in ('pipeline','procurement','awarded','financial-close','operational','completed','cancelled')),
  total_value_usd numeric,
  public_contribution_usd numeric,
  private_investment_usd numeric,
  currency_original text,
  government_sponsor text,
  private_operator text,
  lenders text,
  advisors text,
  announcement_date date,
  tender_date date,
  award_date date,
  financial_close_date date,
  completion_date date,
  lat numeric,
  lng numeric,
  source_url text,
  source_name text,
  confidence_score numeric,
  is_verified boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- ppp_raw (staging)
create table ppp_raw (
  id uuid primary key default gen_random_uuid(),
  name text,
  country text,
  region text,
  sector text,
  status text,
  total_value_usd numeric,
  public_contribution_usd numeric,
  private_investment_usd numeric,
  currency_original text,
  government_sponsor text,
  private_operator text,
  lenders text,
  advisors text,
  announcement_date date,
  tender_date date,
  award_date date,
  financial_close_date date,
  completion_date date,
  lat numeric,
  lng numeric,
  source_url text,
  source_name text,
  confidence_score numeric,
  raw_payload jsonb,
  processing_status text default 'pending' check (processing_status in ('pending','processed','failed')),
  created_at timestamptz default now()
);

-- ppp_review_queue
create table ppp_review_queue (
  id uuid primary key default gen_random_uuid(),
  ppp_raw_id uuid references ppp_raw(id) on delete cascade,
  extracted_fields jsonb,
  confidence_score numeric,
  reviewer_notes text,
  reviewed_by text,
  reviewed_at timestamptz,
  review_action text check (review_action in ('approved','rejected')),
  created_at timestamptz default now()
);

-- ppp_errors
create table ppp_errors (
  id uuid primary key default gen_random_uuid(),
  function_name text,
  error_message text,
  raw_id uuid,
  error_type text default 'system',
  created_at timestamptz default now()
);

-- Unique constraint for upsert deduplication in ppp-enrich
alter table ppp_projects add constraint ppp_projects_source_url_name_key unique (source_url, name);

-- Full-text search index on ppp_projects
create index ppp_projects_fts on ppp_projects using gin (
  to_tsvector('english', coalesce(name,'') || ' ' || coalesce(country,'') || ' ' || coalesce(government_sponsor,'') || ' ' || coalesce(private_operator,''))
);

-- updated_at trigger for ppp_projects
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger ppp_projects_updated_at
  before update on ppp_projects
  for each row execute function update_updated_at();
```

- [ ] **Step 2: Enable RLS on all tables**

```sql
alter table ppp_projects enable row level security;
alter table ppp_raw enable row level security;
alter table ppp_review_queue enable row level security;
alter table ppp_sources enable row level security;
alter table ppp_errors enable row level security;
alter table ppp_settings enable row level security;

-- Public can read ppp_projects only
create policy "Public read ppp_projects"
  on ppp_projects for select
  using (true);

-- All other tables: service role only (edge functions use service role key)
-- No additional policies needed — service role bypasses RLS by default
```

- [ ] **Step 3: Seed initial sources**

```sql
insert into ppp_sources (name, url, type, region, is_active, crawl_frequency_hours) values
  ('World Bank PPI API', 'https://ppi.worldbank.org/api/projects', 'api', 'Global', true, 24),
  ('IsDB Project Database', 'https://www.isdb.org/projects', 'scrape', 'MENA/OIC', true, 24),
  ('MEED Projects', 'https://www.meed.com/projects', 'scrape', 'MENA', true, 24),
  ('Reuters Infrastructure', 'https://www.reuters.com/business/infrastructure', 'scrape', 'Global', true, 24);
```

- [ ] **Step 4: Verify tables exist**

In the Supabase Table Editor, confirm these tables are visible: `ppp_projects`, `ppp_raw`, `ppp_review_queue`, `ppp_sources`, `ppp_errors`, `ppp_settings`.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-03-31-infinity-ppp.md
git commit -m "feat: add Infinity PPP implementation plan"
```

---

### Task 2: Bootstrap Lovable project

**Files:**
- New Lovable project at lovable.dev

- [ ] **Step 1: Create a new Lovable project**

Go to lovable.dev → New Project → name it "Infinity PPP".

- [ ] **Step 2: Connect Supabase**

In Lovable, click the Supabase integration button and connect the Supabase project created in Task 1. Lovable will import the schema automatically.

- [ ] **Step 3: Add Mapbox token as Supabase secret**

In Supabase → Edge Functions → Secrets, add:
- `MAPBOX_PUBLIC_TOKEN` — your Mapbox public (pk.) token from mapbox.com

- [ ] **Step 4: Paste this bootstrapping prompt into Lovable**

```
Set up the Infinity PPP project with the following foundation:

1. Install and configure mapbox-gl and react-map-gl packages.

2. Create a Supabase client utility that uses the connected project's URL and anon key for public queries, and the service role key (via Supabase secrets) for edge functions only.

3. Set up React Router with these routes:
   - / → HomePage
   - /projects/:id → ProjectDetailPage
   - /admin → AdminLayout (protected)
   - /admin/queue → ReviewQueuePage
   - /admin/projects → ProjectsTablePage
   - /admin/sources → SourcesPage
   - /admin/runs → RunControlsPage
   - /admin/settings → SettingsPage

4. Create an AdminLayout component that:
   - Checks Supabase Auth session on mount
   - Redirects to /admin/login if not authenticated
   - Shows a left sidebar nav with links to: Queue (with badge showing ppp_review_queue count where review_action is null), Projects, Sources, Runs, Settings
   - Has a "Logout" button

5. Create a /admin/login page with email + password form that calls supabase.auth.signInWithPassword().

6. Create a placeholder HomePage, ProjectDetailPage, ReviewQueuePage, ProjectsTablePage, SourcesPage, RunControlsPage, SettingsPage — each showing just its page title for now.

Do not build any features yet — just the routing, auth guard, admin nav shell, and Mapbox/Supabase setup.
```

- [ ] **Step 5: Verify in preview**

- Navigate to `/` — should render "HomePage"
- Navigate to `/admin` — should redirect to `/admin/login`
- Login with your Supabase admin credentials — should enter admin and show nav sidebar
- All 5 admin nav links should be visible

---

## Phase 2 — Public Directory

### Task 3: Homepage — hero, stats bar, layout

**Files:**
- Lovable: `HomePage` component

- [ ] **Step 1: Paste this prompt into Lovable**

```
Build the Infinity PPP homepage at /.

Layout (top to bottom):
1. Navbar — "Infinity PPP" logo left, search input center (placeholder: "Search projects, countries, operators..."), no login link
2. Hero section — large headline: "The Global PPP Intelligence Platform", subheadline: "Real-time directory of Public-Private Partnership projects worldwide", dark background
3. Stats bar — 4 stats displayed horizontally, each queried live from ppp_projects:
   - Total Projects (count of all rows)
   - Total Value (sum of total_value_usd formatted as "$X.XB" or "$X.XM")
   - Countries Covered (count of distinct country values)
   - Last Updated (max(updated_at) formatted as relative time e.g. "2 hours ago")
4. Map section — placeholder div with id="map" and class="w-full h-96 bg-slate-200" and text "Map loading..." centered — we will replace this in Task 4
5. Filter bar — horizontal row of dropdowns: Region, Country, Sector, Status, Value Range, Year Range — all multi-select where applicable. A "Reset Filters" button on the right.
6. Project grid — below the filter bar, shows project cards (build in Task 5)

Make the page responsive. Use a clean, professional dark-navy and white color scheme appropriate for an institutional data product.
```

- [ ] **Step 2: Verify in preview**

- Stats bar shows 4 boxes (values will be 0 or null since no data yet — that's expected)
- Filter bar renders with dropdown placeholders
- Page is responsive on mobile

---

### Task 4: Map component with clustered pins

**Files:**
- Lovable: `MapView` component used on HomePage

- [ ] **Step 1: Paste this prompt into Lovable**

```
Replace the map placeholder on the homepage with a full interactive Mapbox map component called MapView.

MapView receives a `projects` prop (array of ppp_projects rows) and a `filters` prop (current filter state).

Requirements:
1. Use react-map-gl with the Mapbox token from the environment (VITE_MAPBOX_TOKEN — we will set this in .env).
2. Show clustered circle markers. Use Mapbox's built-in clustering (cluster: true on the GeoJSON source). Cluster circles should be sized by point count.
3. Individual (unclustered) pins are colored by status:
   - pipeline → #3B82F6 (blue)
   - procurement → #EAB308 (yellow)
   - awarded → #F97316 (orange)
   - financial-close → #8B5CF6 (purple)
   - operational → #22C55E (green)
   - completed → #6B7280 (grey)
   - cancelled → #EF4444 (red)
4. Clicking a pin shows a popup with: project name, country, status badge, total value, and a "View Details →" link to /projects/[id].
5. Clicking a cluster zooms in to expand it.
6. Map style: mapbox://styles/mapbox/dark-v11
7. Default viewport: center [20, 20], zoom 2 (shows the whole world).
8. When `filters` change, the displayed pins update to only show filtered projects.

Also: create a .env.local entry VITE_MAPBOX_TOKEN and set it to the Mapbox public token from Supabase secrets. Add VITE_MAPBOX_TOKEN to the Lovable environment variables panel.
```

- [ ] **Step 2: Verify in preview**

- Map renders with dark basemap
- No errors in browser console about Mapbox token
- Add one test row to `ppp_projects` in Supabase with lat=25.2048, lng=55.2708 (Dubai), name="Test Project", status="operational"
- Verify a green pin appears on the map near Dubai
- Click the pin — popup should show "Test Project"
- Delete the test row after verification

---

### Task 5: Filters + project grid

**Files:**
- Lovable: `FilterBar` component, `ProjectCard` component, `ProjectGrid` component on HomePage

- [ ] **Step 1: Paste this prompt into Lovable**

```
Build the filter bar and project grid on the homepage. These should share a single filter state that updates both the map and the grid simultaneously.

FilterBar requirements:
- Region dropdown: populated from distinct region values in ppp_projects
- Country dropdown: populated from distinct country values, searchable
- Sector multi-select: fixed options — energy, transport, water, health, education, telecoms, social infrastructure
- Status multi-select: fixed options — pipeline, procurement, awarded, financial-close, operational, completed, cancelled
- Value Range: two number inputs (min USD, max USD) with "M" / "B" suffix hints
- Year Range: two year inputs (from, to) filtering on announcement_date
- "Reset Filters" button clears all filters
- Active filter count badge on a "Filters" button for mobile collapse

When any filter changes, re-query ppp_projects from Supabase applying all active filters as WHERE clauses. Pass the filtered results to both MapView and ProjectGrid.

ProjectCard requirements (used in ProjectGrid):
- Project name (bold, truncated at 2 lines)
- Country flag emoji + country name
- Sector icon (use a simple icon set — lucide-react has relevant icons: Zap for energy, Truck for transport, Droplets for water, Heart for health, GraduationCap for education, Wifi for telecoms, Building2 for social infrastructure)
- Status badge (pill, colored by status using the same color scheme as the map pins)
- Total value formatted as "$X.XB" / "$X.XM" / "Value undisclosed" if null
- Private operator name if present, greyed out if not
- Clicking a card navigates to /projects/[id]

ProjectGrid:
- 3-column grid on desktop, 2-column on tablet, 1-column on mobile
- 50 cards per page with prev/next pagination
- Sort controls: "Sort by: Value ↓ / Value ↑ / Date (newest) / Date (oldest)"
- Shows "X projects found" count above the grid
```

- [ ] **Step 2: Wire the navbar search input to FTS**

Add to the Lovable prompt:

```
Wire the homepage search input to Supabase full-text search.

When the user types in the search input (debounce 300ms), query ppp_projects using:
  .textSearch('fts_column', searchTerm, { type: 'websearch', config: 'english' })

Since Lovable doesn't expose the computed tsvector column directly, use a Postgres function instead. Add this to Supabase SQL Editor:

  create or replace function search_ppp_projects(search_term text)
  returns setof ppp_projects as $$
    select * from ppp_projects
    where to_tsvector('english',
      coalesce(name,'') || ' ' || coalesce(country,'') || ' ' ||
      coalesce(government_sponsor,'') || ' ' || coalesce(private_operator,'')
    ) @@ websearch_to_tsquery('english', search_term)
    order by updated_at desc
    limit 100
  $$ language sql stable;

Call it via: supabase.rpc('search_ppp_projects', { search_term: query })

When search is active, results replace the filter-based query results in both the map and the grid. Clearing the search reverts to showing all projects (with current filters applied).
```

- [ ] **Step 3: Seed 5 test projects for visual verification**

Run in Supabase SQL Editor:

```sql
insert into ppp_projects (name, country, region, sector, status, total_value_usd, private_operator, announcement_date, lat, lng, source_name, confidence_score) values
  ('Riyadh Metro Line 7', 'Saudi Arabia', 'MENA', 'transport', 'operational', 4200000000, 'BACS Consortium', '2013-04-01', 24.7136, 46.6753, 'Test', 1.0),
  ('Noor Abu Dhabi Solar Plant', 'UAE', 'MENA', 'energy', 'operational', 870000000, 'Marubeni / EDF', '2016-03-01', 23.7161, 54.0044, 'Test', 1.0),
  ('Egypt New Administrative Capital Water', 'Egypt', 'MENA', 'water', 'awarded', 3100000000, 'Orascom Construction', '2019-06-01', 30.0444, 31.2357, 'Test', 1.0),
  ('Lagos Ring Road PPP', 'Nigeria', 'Sub-Saharan Africa', 'transport', 'procurement', 1500000000, null, '2022-01-01', 6.5244, 3.3792, 'Test', 0.9),
  ('Mumbai Coastal Road', 'India', 'South Asia', 'transport', 'awarded', 2300000000, 'HCC-Tata JV', '2018-11-01', 19.0760, 72.8777, 'Test', 0.95);
```

- [ ] **Step 3: Verify in preview**

- 5 project cards appear in the grid
- 5 pins appear on the map in correct locations
- Clicking "MENA" region filter → 3 cards remain, 3 pins on map
- Clicking "energy" sector filter → 1 card, 1 pin
- Reset Filters → all 5 return
- Sort by Value ↓ → Riyadh Metro ($4.2B) is first

---

### Task 6: Project detail page

**Files:**
- Lovable: `ProjectDetailPage` at `/projects/:id`

- [ ] **Step 1: Paste this prompt into Lovable**

```
Build the project detail page at /projects/:id.

On mount, query ppp_projects for the row matching the id param.

Layout sections (top to bottom):

1. Breadcrumb: "Home → [Country] → [Project Name]"

2. Header block:
   - Project name (large heading)
   - Status badge + sector badge side by side
   - Country flag + country name + region
   - is_verified badge: "✓ Verified" in green if true

3. Key figures row (4 boxes):
   - Total Project Value (total_value_usd)
   - Public Contribution (public_contribution_usd)
   - Private Investment (private_investment_usd)
   - Original Currency (currency_original)
   Each box shows "—" if the value is null.

4. Parties section (2-column):
   Left: Government Sponsor, Private Operator
   Right: Lenders, Advisors
   Each shows "Not disclosed" if null.

5. Timeline visualization:
   Show 5 milestone markers in a horizontal line:
   Announcement → Tender → Award → Financial Close → Completion
   Each milestone shows its date below if present, greyed out if null.
   The current status determines how far along the line is "filled in".

6. Map section:
   Small Mapbox map (height 300px) centered on the project's lat/lng with a single pin.
   If lat/lng is null, show "Location not available".

7. Source attribution:
   "Source: [source_name]" with a link to source_url (opens in new tab).
   "Last updated: [updated_at formatted as date]"

8. Feedback link:
   "Is this data incorrect?" — clicking opens a small modal with a text area.
   On submit, insert into ppp_errors: { function_name: 'user_report', error_message: [user text], raw_id: null, error_type: 'user_report' }.
   Show "Thank you — we'll review this." on success.

9. Back button: "← Back to directory" navigates to /.
```

- [ ] **Step 2: Verify in preview**

- Click a project card from the homepage
- Detail page loads with all fields
- Timeline shows filled milestones where dates exist
- Mini-map shows pin at project location
- "Is this data incorrect?" modal opens, submitting inserts a row into `ppp_errors`
- Back button returns to homepage

---

## Phase 3 — Admin Panel

### Task 7: Review queue

**Files:**
- Lovable: `ReviewQueuePage` at `/admin/queue`

- [ ] **Step 1: Seed one test review queue item**

```sql
-- First insert a raw record
insert into ppp_raw (name, country, sector, status, total_value_usd, source_url, source_name, confidence_score, processing_status, raw_payload)
values ('Test Low Confidence Project', 'Jordan', 'water', 'pipeline', 500000000, 'https://example.com', 'Reuters', 0.55, 'processed', '{"raw": "test"}');

-- Then insert a queue item referencing it
insert into ppp_review_queue (ppp_raw_id, extracted_fields, confidence_score)
select id,
  jsonb_build_object('name','Test Low Confidence Project','country','Jordan','sector','water','status','pipeline','total_value_usd',500000000),
  0.55
from ppp_raw where name = 'Test Low Confidence Project';
```

- [ ] **Step 2: Paste this prompt into Lovable**

```
Build the Review Queue page at /admin/queue.

Query ppp_review_queue where review_action is null, ordered by created_at desc. Join with ppp_raw to show source context.

For each queue item, show a card with:
- Confidence score as a colored badge: ≥0.7 → yellow "Review", <0.7 → red "Low confidence"
- Source name and URL (from ppp_raw via ppp_raw_id)
- All extracted_fields displayed as an editable form:
  - name (text input)
  - country (text input)
  - region (text input)
  - sector (select: energy/transport/water/health/education/telecoms/social infrastructure)
  - status (select: pipeline/procurement/awarded/financial-close/operational/completed/cancelled)
  - total_value_usd (number input)
  - public_contribution_usd (number input)
  - private_investment_usd (number input)
  - currency_original (text input)
  - government_sponsor (text input)
  - private_operator (text input)
  - lenders (text input)
  - advisors (text input)
  - announcement_date (date input)
  - award_date (date input)
  - financial_close_date (date input)
  - completion_date (date input)

Three action buttons per card:
- "Approve" (green) — inserts the (possibly edited) extracted_fields into ppp_projects, sets ppp_review_queue.review_action = 'approved', reviewed_at = now()
- "Reject" (red) — opens a small modal asking for a rejection note, then sets review_action = 'rejected', reviewer_notes = [note], reviewed_at = now()
- "Skip" (grey) — collapses the card without acting

"Bulk Approve All" button at top — approves all visible queue items using their extracted_fields as-is.

Show "Queue empty — nothing to review." when there are no pending items.

Update the sidebar queue badge count after each action.
```

- [ ] **Step 3: Verify in preview**

- Queue shows the seeded test item
- Edit the name field and click Approve — verify the edited project appears in `ppp_projects` in Supabase
- Verify `ppp_review_queue` row now has `review_action = 'approved'`
- Queue shows "Queue empty" after approval

---

### Task 8: Projects table + manual entry

**Files:**
- Lovable: `ProjectsTablePage` at `/admin/projects`

- [ ] **Step 1: Paste this prompt into Lovable**

```
Build the Projects Table page at /admin/projects.

Section 1 — Manual Entry form (collapsible, collapsed by default, opened by "+ Add Project" button):
Fields: name (required), country (required), region, sector (required), status (required), total_value_usd, public_contribution_usd, private_investment_usd, currency_original, government_sponsor, private_operator, lenders, advisors, announcement_date, tender_date, award_date, financial_close_date, completion_date, lat, lng, source_url, source_name.
On submit: insert directly into ppp_projects with is_verified = true, confidence_score = 1.0.
Show success toast "Project added." and refresh the table.

Section 2 — Projects Table:
- Searchable (text input filters name, country, operator)
- Filterable by sector and status (dropdowns)
- Columns: Name, Country, Sector, Status, Total Value, Operator, Verified, Updated, Actions
- Each row is inline-editable: clicking a cell opens an input. Tab or blur saves the change via UPDATE to ppp_projects.
- "Verified" column shows a toggle — clicking it flips is_verified and saves.
- Actions column: "Delete" button — sets status = 'cancelled' (soft delete) and shows a confirmation dialog "Mark as Cancelled?" before proceeding.
- Pagination: 50 rows per page.
- Show total project count above the table.
```

- [ ] **Step 2: Verify in preview**

- Click "+ Add Project" — form expands
- Fill in name="Manual Test", country="Kuwait", sector="energy", status="pipeline" — submit
- Row appears in table
- Click the name cell — edit it, tab away — Supabase row updates
- Click the Verified toggle — `is_verified` flips in Supabase
- Click Delete — confirm → status changes to "cancelled" in Supabase

---

### Task 9: Sources manager + run controls + settings

**Files:**
- Lovable: `SourcesPage`, `RunControlsPage`, `SettingsPage`

- [ ] **Step 1: Paste this prompt into Lovable**

```
Build three admin pages:

--- SOURCES PAGE at /admin/sources ---

Show a table of all ppp_sources rows with columns: Name, URL, Type, Region, Active, Last Crawled, Record Count, Actions.

"+ Add Source" button opens a form: name, url, type (select: api/scrape/manual), region, crawl_frequency_hours (number, default 24). On submit, insert into ppp_sources.

Each row has:
- Active toggle — flips is_active and saves
- "Crawl Now" button — calls the ppp-crawl edge function with a body of { source_id: [id] }. Show a loading spinner while running. Toast "Crawl complete." on success.
- Edit button — opens inline edit mode for name, url, region
- Delete button — deletes the row after confirmation

--- RUN CONTROLS PAGE at /admin/runs ---

Four trigger buttons in a row:
- "Run Crawl" → invoke ppp-crawl edge function (no body)
- "Run Enrich" → invoke ppp-enrich edge function
- "Run Geocode" → invoke ppp-geocode edge function
- "Run Dedup" → invoke ppp-dedup edge function

Each button shows a spinner while running. Log the result (success/error) in a scrollable output panel below the buttons.

Below the trigger buttons:
- Error log table: query ppp_errors ordered by created_at desc, limit 100. Columns: Time, Function, Error Message, Type. Auto-refreshes every 30 seconds.

--- SETTINGS PAGE at /admin/settings ---

Form bound to the single ppp_settings row:
- Confidence Threshold (number input, 0–1, step 0.05)
- Auto-publish Enabled (toggle)
- Is Running (toggle)
- Prompt Version (read-only text)

"Save" button updates the ppp_settings row. Show success toast on save.
```

- [ ] **Step 2: Verify in preview**

- Sources page shows the 4 seeded sources
- Toggle a source inactive — `is_active` flips in Supabase
- Settings page loads the current confidence_threshold (0.8)
- Change it to 0.75 and Save — verify the value updates in Supabase
- Run Controls page shows 4 buttons (edge functions don't exist yet — they will return 404, that's expected)

---

## Phase 4 — Ingestion Pipeline

### Task 10: `ppp-crawl` edge function

**Files:**
- Create: Supabase Edge Function `ppp-crawl`

- [ ] **Step 1: Create the edge function in Supabase**

In Supabase → Edge Functions → New Function → name: `ppp-crawl`. Paste:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

Deno.serve(async (req) => {
  try {
    const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {}
    const specificSourceId = body.source_id ?? null

    // Load active sources (or specific source if source_id provided)
    const query = supabase.from('ppp_sources').select('*').eq('is_active', true)
    if (specificSourceId) query.eq('id', specificSourceId)
    const { data: sources, error: sourcesError } = await query
    if (sourcesError) throw sourcesError

    let totalInserted = 0

    for (const source of sources ?? []) {
      try {
        let rawRecords: any[] = []

        if (source.type === 'api' && source.url.includes('worldbank')) {
          // World Bank PPI API pagination
          let page = 1
          let hasMore = true
          while (hasMore) {
            const res = await fetch(`${source.url}?page=${page}&pageSize=100`)
            const json = await res.json()
            const projects = json.projects ?? json.data ?? []
            if (projects.length === 0) { hasMore = false; break }
            rawRecords.push(...projects.map((p: any) => ({
              name: p.projectName ?? p.name,
              country: p.country ?? p.countryName,
              sector: normalizeSector(p.sector ?? p.primarySector),
              status: normalizeStatus(p.status ?? p.projectStatus),
              total_value_usd: parseFloat(p.totalProjectCost ?? p.investment ?? 0) || null,
              announcement_date: p.financialClosureDate ?? p.startDate ?? null,
              source_url: `https://ppi.worldbank.org/project/${p.id ?? p.projectId}`,
              source_name: source.name,
              raw_payload: p,
            })))
            page++
            if (page > 50) hasMore = false // safety limit
          }
        } else {
          // Generic scrape: fetch page HTML, store as raw text for ppp-enrich to parse
          const res = await fetch(source.url, {
            headers: { 'User-Agent': 'InfinityPPP/1.0 (ppp-directory research bot)' }
          })
          const html = await res.text()
          // Extract text content (strip tags)
          const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
          rawRecords = [{ source_url: source.url, source_name: source.name, raw_payload: { html_text: text.slice(0, 50000) } }]
        }

        // Deduplicate and insert
        for (const record of rawRecords) {
          if (!record.name && !record.source_url) continue
          // Check if already exists in ppp_raw or ppp_projects
          const { count } = await supabase
            .from('ppp_raw')
            .select('id', { count: 'exact', head: true })
            .eq('source_url', record.source_url ?? '')
            .eq('name', record.name ?? '')
          if ((count ?? 0) > 0) continue

          const { error: insertError } = await supabase.from('ppp_raw').insert({
            ...record,
            processing_status: 'pending',
          })
          if (insertError) {
            await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: insertError.message, error_type: 'system' })
          } else {
            totalInserted++
          }
        }

        // Update last_crawled_at and record_count
        await supabase.from('ppp_sources').update({
          last_crawled_at: new Date().toISOString(),
          record_count: (source.record_count ?? 0) + rawRecords.length
        }).eq('id', source.id)

      } catch (sourceErr: any) {
        await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: `Source ${source.name}: ${sourceErr.message}`, error_type: 'system' })
      }
    }

    // Trigger ppp-enrich
    fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ppp-enrich`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` }
    }).catch(() => {})

    return new Response(JSON.stringify({ ok: true, inserted: totalInserted }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: err.message, error_type: 'system' })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})

function normalizeSector(raw: string | null): string | null {
  if (!raw) return null
  const r = raw.toLowerCase()
  if (r.includes('energy') || r.includes('power') || r.includes('solar') || r.includes('wind')) return 'energy'
  if (r.includes('transport') || r.includes('road') || r.includes('rail') || r.includes('port') || r.includes('airport')) return 'transport'
  if (r.includes('water') || r.includes('sanitation') || r.includes('sewage')) return 'water'
  if (r.includes('health') || r.includes('hospital')) return 'health'
  if (r.includes('education') || r.includes('school') || r.includes('university')) return 'education'
  if (r.includes('telecom') || r.includes('broadband') || r.includes('fiber')) return 'telecoms'
  return 'social infrastructure'
}

function normalizeStatus(raw: string | null): string | null {
  if (!raw) return null
  const r = raw.toLowerCase()
  if (r.includes('pipeline') || r.includes('identified') || r.includes('preparation')) return 'pipeline'
  if (r.includes('procurement') || r.includes('tender') || r.includes('bid')) return 'procurement'
  if (r.includes('award') || r.includes('signed')) return 'awarded'
  if (r.includes('financial close') || r.includes('financial-close')) return 'financial-close'
  if (r.includes('operat') || r.includes('active')) return 'operational'
  if (r.includes('complet') || r.includes('closed')) return 'completed'
  if (r.includes('cancel') || r.includes('terminat')) return 'cancelled'
  return 'pipeline'
}
```

- [ ] **Step 2: Set the cron schedule**

In Supabase → Edge Functions → `ppp-crawl` → Cron → set to `0 6 * * *` (daily at 6am UTC).

- [ ] **Step 3: Test manually**

In Supabase → Edge Functions → `ppp-crawl` → Test. Or call:
```bash
curl -X POST https://[your-project-ref].supabase.co/functions/v1/ppp-crawl \
  -H "Authorization: Bearer [service-role-key]"
```

Expected response: `{ "ok": true, "inserted": N }` where N ≥ 0.

Check `ppp_raw` in Supabase Table Editor — new rows should appear with `processing_status = 'pending'`.

---

### Task 11: `ppp-enrich` edge function

**Files:**
- Create: Supabase Edge Function `ppp-enrich`

- [ ] **Step 1: Create the edge function**

In Supabase → Edge Functions → New Function → name: `ppp-enrich`. Paste:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

Deno.serve(async (_req) => {
  try {
    const { data: settings } = await supabase.from('ppp_settings').select('*').single()
    const threshold = settings?.confidence_threshold ?? 0.8
    const autoPublish = settings?.auto_publish_enabled ?? true

    const { data: pendingRecords } = await supabase
      .from('ppp_raw')
      .select('*')
      .eq('processing_status', 'pending')
      .limit(100)

    let enriched = 0, queued = 0, failed = 0

    for (const record of pendingRecords ?? []) {
      try {
        // If already has structured fields (from API), skip AI and just score
        const hasStructuredData = record.name && record.country && record.sector && record.status

        let extracted = {
          name: record.name,
          country: record.country,
          region: record.region ?? inferRegion(record.country),
          sector: record.sector,
          status: record.status,
          total_value_usd: record.total_value_usd,
          public_contribution_usd: record.public_contribution_usd,
          private_investment_usd: record.private_investment_usd,
          currency_original: record.currency_original,
          government_sponsor: record.government_sponsor,
          private_operator: record.private_operator,
          lenders: record.lenders,
          advisors: record.advisors,
          announcement_date: record.announcement_date,
          tender_date: record.tender_date,
          award_date: record.award_date,
          financial_close_date: record.financial_close_date,
          completion_date: record.completion_date,
          lat: record.lat,
          lng: record.lng,
          source_url: record.source_url,
          source_name: record.source_name,
        }

        if (!hasStructuredData && record.raw_payload?.html_text) {
          // AI extraction for scraped records
          const aiPrompt = `Extract PPP project data from this text. Return ONLY a valid JSON object with these fields (use null for unknown): name, country, region, sector (one of: energy/transport/water/health/education/telecoms/social infrastructure), status (one of: pipeline/procurement/awarded/financial-close/operational/completed/cancelled), total_value_usd (number, USD), public_contribution_usd, private_investment_usd, currency_original, government_sponsor, private_operator, lenders, advisors, announcement_date (YYYY-MM-DD), tender_date, award_date, financial_close_date, completion_date. Extract as many projects as you can find — return an array of objects.\n\nText:\n${record.raw_payload.html_text.slice(0, 8000)}`

          // Use Supabase AI (built-in)
          const aiResponse = await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ai-complete`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}`
            },
            body: JSON.stringify({ prompt: aiPrompt })
          })

          if (aiResponse.ok) {
            const aiData = await aiResponse.json()
            const parsed = JSON.parse(aiData.text ?? aiData.content ?? '[]')
            const projects = Array.isArray(parsed) ? parsed : [parsed]

            // Insert additional extracted projects as separate raw records
            for (let i = 1; i < projects.length; i++) {
              await supabase.from('ppp_raw').insert({
                ...projects[i],
                source_url: record.source_url,
                source_name: record.source_name,
                raw_payload: record.raw_payload,
                processing_status: 'pending'
              })
            }
            if (projects[0]) extracted = { ...extracted, ...projects[0] }
          }
        }

        // Score confidence
        const score = computeConfidenceScore(extracted, record.source_name ?? '')

        await supabase.from('ppp_raw').update({ processing_status: 'processed', confidence_score: score }).eq('id', record.id)

        if (autoPublish && score >= threshold && extracted.name) {
          // Upsert into ppp_projects
          const { error: upsertErr } = await supabase.from('ppp_projects').upsert({
            ...extracted,
            confidence_score: score,
            updated_at: new Date().toISOString(),
          }, { onConflict: 'source_url,name' })
          if (upsertErr) throw upsertErr
          enriched++
        } else if (extracted.name || extracted.country) {
          // Route to review queue
          await supabase.from('ppp_review_queue').insert({
            ppp_raw_id: record.id,
            extracted_fields: extracted,
            confidence_score: score,
          })
          queued++
        }

      } catch (recordErr: any) {
        await supabase.from('ppp_errors').insert({ function_name: 'ppp-enrich', error_message: recordErr.message, raw_id: record.id, error_type: 'system' })
        await supabase.from('ppp_raw').update({ processing_status: 'failed' }).eq('id', record.id)
        failed++
      }
    }

    // Trigger geocode
    fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ppp-geocode`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` }
    }).catch(() => {})

    return new Response(JSON.stringify({ ok: true, enriched, queued, failed }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-enrich', error_message: err.message, error_type: 'system' })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})

function computeConfidenceScore(fields: Record<string, any>, sourceName: string): number {
  const requiredFields = ['name', 'country', 'sector', 'status']
  const optionalFields = ['total_value_usd', 'government_sponsor', 'private_operator', 'announcement_date', 'region']

  const requiredScore = requiredFields.filter(f => fields[f]).length / requiredFields.length
  const optionalScore = optionalFields.filter(f => fields[f]).length / optionalFields.length

  // Source type bonus
  const sourceBonus = sourceName.toLowerCase().includes('world bank') || sourceName.toLowerCase().includes('isdb') ? 0.15 : 0

  return Math.min(1, requiredScore * 0.6 + optionalScore * 0.25 + sourceBonus)
}

function inferRegion(country: string | null): string | null {
  if (!country) return null
  const mena = ['Saudi Arabia','UAE','Egypt','Jordan','Morocco','Tunisia','Algeria','Libya','Iraq','Syria','Lebanon','Yemen','Oman','Kuwait','Bahrain','Qatar','Palestine','Israel']
  const ssa = ['Nigeria','Kenya','Ghana','Ethiopia','South Africa','Tanzania','Rwanda','Uganda']
  const sa = ['India','Pakistan','Bangladesh','Sri Lanka','Nepal']
  const sea = ['Indonesia','Vietnam','Philippines','Thailand','Malaysia','Myanmar']
  if (mena.includes(country)) return 'MENA'
  if (ssa.includes(country)) return 'Sub-Saharan Africa'
  if (sa.includes(country)) return 'South Asia'
  if (sea.includes(country)) return 'Southeast Asia'
  return null
}
```

- [ ] **Step 2: Test manually**

Insert a test pending raw record, then invoke `ppp-enrich`:

```sql
insert into ppp_raw (name, country, sector, status, total_value_usd, source_url, source_name, processing_status, raw_payload)
values ('Kuwait Al-Zour Refinery', 'Kuwait', 'energy', 'operational', 14000000000, 'https://test.com/alzour', 'World Bank PPI', 'pending', '{}');
```

Then call:
```bash
curl -X POST https://[your-project-ref].supabase.co/functions/v1/ppp-enrich \
  -H "Authorization: Bearer [service-role-key]"
```

Expected: the Al-Zour Refinery row appears in `ppp_projects` (high confidence — World Bank source with all required fields). `ppp_raw.processing_status` changes to `processed`.

---

### Task 12: `ppp-geocode` edge function

**Files:**
- Create: Supabase Edge Function `ppp-geocode`

- [ ] **Step 1: Create the edge function**

In Supabase → Edge Functions → New Function → name: `ppp-geocode`. Paste:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

// Country centroids fallback
const COUNTRY_CENTROIDS: Record<string, [number, number]> = {
  'Saudi Arabia': [23.8859, 45.0792], 'UAE': [23.4241, 53.8478], 'Egypt': [26.8206, 30.8025],
  'Jordan': [30.5852, 36.2384], 'Morocco': [31.7917, -7.0926], 'Tunisia': [33.8869, 9.5375],
  'Algeria': [28.0339, 1.6596], 'Iraq': [33.2232, 43.6793], 'Kuwait': [29.3759, 47.9774],
  'Qatar': [25.3548, 51.1839], 'Bahrain': [26.0275, 50.5500], 'Oman': [21.4735, 55.9754],
  'Nigeria': [9.0820, 8.6753], 'Kenya': [-0.0236, 37.9062], 'India': [20.5937, 78.9629],
  'Pakistan': [30.3753, 69.3451], 'Indonesia': [-0.7893, 113.9213], 'Vietnam': [14.0583, 108.2772],
}

Deno.serve(async (_req) => {
  try {
    const mapboxToken = Deno.env.get('MAPBOX_PUBLIC_TOKEN')

    const { data: projects } = await supabase
      .from('ppp_projects')
      .select('id, name, country, lat, lng')
      .or('lat.is.null,lng.is.null')
      .limit(200)

    let resolved = 0, fallback = 0

    for (const project of projects ?? []) {
      let lat: number | null = null, lng: number | null = null

      // Try Mapbox geocoding
      if (mapboxToken) {
        try {
          const query = encodeURIComponent(`${project.name}, ${project.country}`)
          const res = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${query}.json?access_token=${mapboxToken}&limit=1`)
          const geo = await res.json()
          if (geo.features?.[0]) {
            [lng, lat] = geo.features[0].center
            resolved++
          }
        } catch (_e) { /* fall through to centroid */ }
      }

      // Fallback to country centroid
      if ((lat === null || lng === null) && project.country) {
        const centroid = COUNTRY_CENTROIDS[project.country]
        if (centroid) {
          [lat, lng] = centroid
          fallback++
        }
      }

      if (lat !== null && lng !== null) {
        await supabase.from('ppp_projects').update({ lat, lng }).eq('id', project.id)
      }
    }

    return new Response(JSON.stringify({ ok: true, resolved, fallback }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-geocode', error_message: err.message, error_type: 'system' })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})
```

- [ ] **Step 2: Test manually**

Insert a project with no coordinates:
```sql
insert into ppp_projects (name, country, sector, status, source_name, confidence_score)
values ('Test No Coords', 'Jordan', 'water', 'pipeline', 'Manual', 1.0);
```

Invoke `ppp-geocode`. Check that the row now has `lat` and `lng` values in Supabase (either Mapbox result or Jordan centroid: 30.5852, 36.2384).

---

### Task 13: `ppp-dedup` edge function + cron

**Files:**
- Create: Supabase Edge Function `ppp-dedup`

- [ ] **Step 1: Enable pg_trgm extension in Supabase**

```sql
create extension if not exists pg_trgm;
```

- [ ] **Step 2: Create the edge function**

In Supabase → Edge Functions → New Function → name: `ppp-dedup`. Paste:

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

Deno.serve(async (_req) => {
  try {
    // Use Postgres similarity to find near-duplicates within the same country
    const { data: duplicates, error } = await supabase.rpc('find_ppp_duplicates')
    if (error) throw error

    let flagged = 0
    for (const pair of duplicates ?? []) {
      // Insert a review queue item flagging the duplicate
      const existing = await supabase
        .from('ppp_review_queue')
        .select('id')
        .eq('ppp_raw_id', pair.id_b)
        .single()

      if (!existing.data) {
        // Insert a raw record shell to reference
        const { data: rawShell } = await supabase.from('ppp_raw').insert({
          name: pair.name_b,
          country: pair.country,
          source_name: 'dedup-detector',
          processing_status: 'processed',
          raw_payload: { duplicate_of: pair.id_a }
        }).select().single()

        if (rawShell) {
          await supabase.from('ppp_review_queue').insert({
            ppp_raw_id: rawShell.id,
            extracted_fields: { name: pair.name_b, country: pair.country },
            confidence_score: 0,
            reviewer_notes: `Potential duplicate of project ID ${pair.id_a} ("${pair.name_a}"). Similarity: ${Math.round(pair.similarity * 100)}%`,
          })
          flagged++
        }
      }
    }

    return new Response(JSON.stringify({ ok: true, flagged }), {
      headers: { 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-dedup', error_message: err.message, error_type: 'system' })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})
```

- [ ] **Step 3: Create the `find_ppp_duplicates` Postgres function**

```sql
create or replace function find_ppp_duplicates()
returns table (
  id_a uuid, name_a text,
  id_b uuid, name_b text,
  country text, similarity float
) as $$
  select
    a.id as id_a, a.name as name_a,
    b.id as id_b, b.name as name_b,
    a.country,
    similarity(a.name, b.name) as similarity
  from ppp_projects a
  join ppp_projects b
    on a.country = b.country
    and a.id < b.id
    and similarity(a.name, b.name) > 0.85
$$ language sql stable;
```

- [ ] **Step 4: Set the cron schedule**

In Supabase → Edge Functions → `ppp-dedup` → Cron → set to `0 6 * * 0` (weekly, Sundays at 6am UTC).

- [ ] **Step 5: Test manually**

Insert two near-duplicate projects:
```sql
insert into ppp_projects (name, country, sector, status, source_name, confidence_score) values
  ('Riyadh Metro Phase 2', 'Saudi Arabia', 'transport', 'pipeline', 'Test', 0.9),
  ('Riyadh Metro Phase II', 'Saudi Arabia', 'transport', 'pipeline', 'Test', 0.9);
```

Invoke `ppp-dedup`. Check `ppp_review_queue` — a new item should appear with `reviewer_notes` mentioning "Potential duplicate".

- [ ] **Step 6: Final commit**

```bash
git add docs/
git commit -m "feat: complete Infinity PPP implementation plan"
```

---

## Post-Launch Checklist

- [ ] Delete all test/seed rows from `ppp_projects` and `ppp_raw` before going live
- [ ] Set up Supabase Auth — create admin user via Supabase dashboard (Authentication → Users → Invite user)
- [ ] Confirm `MAPBOX_PUBLIC_TOKEN` is set in Supabase secrets
- [ ] Trigger `ppp-crawl` manually to seed initial data from World Bank PPI
- [ ] Monitor `ppp_errors` after first crawl for any source issues
- [ ] Review and approve first batch in `/admin/queue`
- [ ] Set a custom domain for the Lovable project
