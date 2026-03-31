Build a complete web application called **Infinity PPP** — a global real-time directory of Public-Private Partnership (PPP) projects. This is a full-stack app using React (frontend) and Supabase (database + edge functions).

---

## 1. Database

Create these Supabase tables with RLS enabled:

**ppp_settings:** id (uuid, primary key, default gen_random_uuid()), confidence_threshold (numeric, default 0.8), auto_publish_enabled (boolean, default true), is_running (boolean, default true), prompt_version (text, default 'v0.0.1'), created_at (timestamptz, default now())

Seed one row: confidence_threshold=0.8, auto_publish_enabled=true, is_running=true, prompt_version='v0.0.1'

**ppp_sources:** id (uuid, primary key, default gen_random_uuid()), name (text), url (text), type (text — one of api/scrape/manual), region (text), is_active (boolean, default true), last_crawled_at (timestamptz), crawl_frequency_hours (integer, default 24), record_count (integer, default 0), created_at (timestamptz, default now())

Seed 4 rows:
- World Bank PPI API | https://ppi.worldbank.org/api/projects | api | Global | true | 24
- IsDB Project Database | https://www.isdb.org/projects | scrape | MENA/OIC | true | 24
- MEED Projects | https://www.meed.com/projects | scrape | MENA | true | 24
- Reuters Infrastructure | https://www.reuters.com/business/infrastructure | scrape | Global | true | 24

**ppp_projects:** id (uuid, primary key, default gen_random_uuid()), name (text), country (text), region (text), sector (text — one of energy/transport/water/health/education/telecoms/social infrastructure), status (text — one of pipeline/procurement/awarded/financial-close/operational/completed/cancelled), total_value_usd (numeric), public_contribution_usd (numeric), private_investment_usd (numeric), currency_original (text), government_sponsor (text), private_operator (text), lenders (text), advisors (text), announcement_date (date), tender_date (date), award_date (date), financial_close_date (date), completion_date (date), lat (numeric), lng (numeric), source_url (text), source_name (text), confidence_score (numeric), is_verified (boolean, default false), created_at (timestamptz, default now()), updated_at (timestamptz, default now())

Add unique constraint: (source_url, name)
Add updated_at trigger that sets updated_at = now() on every update.
Add full-text search function:
```sql
create or replace function search_ppp_projects(search_term text)
returns setof ppp_projects as $$
  select * from ppp_projects
  where to_tsvector('english',
    coalesce(name,'') || ' ' || coalesce(country,'') || ' ' ||
    coalesce(government_sponsor,'') || ' ' || coalesce(private_operator,'')
  ) @@ websearch_to_tsquery('english', search_term)
  order by updated_at desc limit 100
$$ language sql stable;
```

**ppp_raw:** id (uuid, primary key, default gen_random_uuid()), name (text), country (text), region (text), sector (text), status (text), total_value_usd (numeric), public_contribution_usd (numeric), private_investment_usd (numeric), currency_original (text), government_sponsor (text), private_operator (text), lenders (text), advisors (text), announcement_date (date), tender_date (date), award_date (date), financial_close_date (date), completion_date (date), lat (numeric), lng (numeric), source_url (text), source_name (text), confidence_score (numeric), raw_payload (jsonb), processing_status (text, default 'pending' — one of pending/processed/failed), created_at (timestamptz, default now())

**ppp_review_queue:** id (uuid, primary key, default gen_random_uuid()), ppp_raw_id (uuid, foreign key → ppp_raw on delete cascade), extracted_fields (jsonb), confidence_score (numeric), reviewer_notes (text), reviewed_by (text), reviewed_at (timestamptz), review_action (text — one of approved/rejected), created_at (timestamptz, default now())

**ppp_errors:** id (uuid, primary key, default gen_random_uuid()), function_name (text), error_message (text), raw_id (uuid), error_type (text, default 'system'), created_at (timestamptz, default now())

RLS policies:
- ppp_projects: public SELECT allowed (no auth required)
- All other tables: authenticated users only

Note: Store MAPBOX_PUBLIC_TOKEN as a Supabase secret. Never store in the database.

---

## 2. Routing

Set up React Router with these routes:
- `/` → HomePage
- `/projects/:id` → ProjectDetailPage
- `/admin/login` → AdminLoginPage
- `/admin` → AdminLayout (auth-protected, redirects to /admin/login if no session)
- `/admin/queue` → ReviewQueuePage
- `/admin/projects` → ProjectsTablePage
- `/admin/sources` → SourcesPage
- `/admin/runs` → RunControlsPage
- `/admin/settings` → SettingsPage

AdminLayout: left sidebar nav with links to Queue (with badge showing pending review count), Projects, Sources, Runs, Settings. Logout button calls supabase.auth.signOut() and redirects to /admin/login.

AdminLoginPage: email + password form, calls supabase.auth.signInWithPassword(), on success redirects to /admin/queue.

---

## 3. Homepage `/`

### Layout (top to bottom):

**Navbar:** "Infinity PPP" logo left. Search input center (placeholder: "Search projects, countries, operators...") — on input (debounce 300ms) call supabase.rpc('search_ppp_projects', { search_term }) and update both map and grid with results. Clearing search reverts to full filtered view.

**Hero:** Dark navy background. Large headline: "The Global PPP Intelligence Platform". Subheadline: "Real-time directory of Public-Private Partnership projects worldwide."

**Stats bar:** 4 live stats queried from ppp_projects:
- Total Projects (count)
- Total Value (sum of total_value_usd, formatted as "$4.2B" / "$850M")
- Countries Covered (count distinct country)
- Last Updated (max updated_at as relative time e.g. "2 hours ago")

**Map:** Full-width interactive Mapbox map (height: 480px). Use react-map-gl. Map style: mapbox://styles/mapbox/dark-v11. Default view: center [20, 20], zoom 2. Use the MAPBOX_PUBLIC_TOKEN environment variable.

Show clustered circle markers using Mapbox's built-in clustering (cluster: true on GeoJSON source). Cluster circles sized by point count.

Individual pins colored by status:
- pipeline → #3B82F6
- procurement → #EAB308
- awarded → #F97316
- financial-close → #8B5CF6
- operational → #22C55E
- completed → #6B7280
- cancelled → #EF4444

Clicking a pin shows a popup: project name, status badge, total value, "View Details →" link to /projects/[id]. Clicking a cluster zooms in. Map updates when filters or search change.

**Filter bar:** Horizontal row below the map:
- Region (multi-select, populated from distinct region values)
- Country (multi-select, searchable, populated from distinct country values)
- Sector (multi-select: energy/transport/water/health/education/telecoms/social infrastructure)
- Status (multi-select: pipeline/procurement/awarded/financial-close/operational/completed/cancelled)
- Value Range (two number inputs: min/max USD)
- Year Range (two year inputs filtering on announcement_date)
- "Reset Filters" button

All filters and search share one state. Changing any filter re-queries ppp_projects and updates both map and grid simultaneously.

**Project grid:** Cards, 3-column desktop / 2-column tablet / 1-column mobile. 50 per page with pagination. Sort controls: Value ↓ / Value ↑ / Newest / Oldest. "X projects found" count above grid.

Each card shows:
- Project name (bold, 2-line truncation)
- Country flag emoji + country name
- Sector icon (use lucide-react: Zap=energy, Truck=transport, Droplets=water, Heart=health, GraduationCap=education, Wifi=telecoms, Building2=social infrastructure)
- Status badge (pill, colored by status)
- Total value ("$4.2B" / "$850M" / "Value undisclosed" if null)
- Private operator name if present

Clicking a card navigates to /projects/[id].

---

## 4. Project Detail Page `/projects/:id`

Query ppp_projects for the row matching :id.

Layout:
1. Breadcrumb: Home → [Country] → [Project Name]
2. Header: project name (large heading), status badge + sector badge, country flag + name + region, "✓ Verified" badge in green if is_verified = true
3. Key figures (4 boxes): Total Value, Public Contribution, Private Investment, Original Currency — show "—" if null
4. Parties (2-column): left = Government Sponsor + Private Operator, right = Lenders + Advisors — show "Not disclosed" if null
5. Timeline (horizontal): Announcement → Tender → Award → Financial Close → Completion. Each milestone shows its date if present, greyed out if null. Fill the line up to the current status stage.
6. Map (300px height): Mapbox map centered on project lat/lng with one pin. Show "Location not available" if lat/lng is null.
7. Source attribution: "Source: [source_name]" linked to source_url (new tab). "Last updated: [updated_at]"
8. Feedback: "Is this data incorrect?" link opens a modal with a textarea. On submit, insert into ppp_errors: { function_name: 'user_report', error_message: [user text], error_type: 'user_report' }. Show "Thank you — we'll review this."
9. Back button: "← Back to directory" → /

---

## 5. Admin — Review Queue `/admin/queue`

Query ppp_review_queue where review_action is null, ordered by created_at desc.

For each item show a card:
- Confidence score badge: ≥0.7 → yellow "Review", <0.7 → red "Low confidence"
- Source name and URL (from ppp_raw via ppp_raw_id join)
- Editable form pre-filled from extracted_fields: name, country, region, sector (select), status (select), total_value_usd, public_contribution_usd, private_investment_usd, currency_original, government_sponsor, private_operator, lenders, advisors, announcement_date, tender_date, award_date, financial_close_date, completion_date

Actions:
- "Approve" (green): insert the (possibly edited) fields into ppp_projects, set review_action='approved', reviewed_at=now()
- "Reject" (red): modal asking for rejection note, then set review_action='rejected', reviewer_notes=[note], reviewed_at=now()
- "Skip" (grey): collapse card without acting

"Bulk Approve All" button at top — approves all visible items using extracted_fields as-is.

Update sidebar queue badge after each action. Show "Queue empty — nothing to review." when empty.

---

## 6. Admin — Projects Table `/admin/projects`

**"+ Add Project" button** (collapsed by default) opens a form: name (required), country (required), region, sector (required), status (required), total_value_usd, public_contribution_usd, private_investment_usd, currency_original, government_sponsor, private_operator, lenders, advisors, announcement_date, tender_date, award_date, financial_close_date, completion_date, lat, lng, source_url, source_name.

On submit: insert into ppp_projects with is_verified=true, confidence_score=1.0. Toast "Project added." and refresh table.

**Table:**
- Search input filters name/country/operator
- Sector and status dropdowns
- Columns: Name, Country, Sector, Status, Total Value, Operator, Verified, Updated, Actions
- Inline-editable cells (click to edit, blur/tab saves via UPDATE)
- Verified column: toggle that flips is_verified
- Actions: "Delete" sets status='cancelled' after confirmation dialog
- 50 rows per page, show total count

---

## 7. Admin — Sources `/admin/sources`

Table of all ppp_sources: Name, URL, Type, Region, Active, Last Crawled, Record Count, Actions.

"+ Add Source" form: name, url, type (select: api/scrape/manual), region, crawl_frequency_hours (default 24).

Each row:
- Active toggle (flips is_active)
- "Crawl Now" button: calls ppp-crawl edge function with body { source_id: [id] }, shows spinner, toasts result
- Edit: inline edit name/url/region
- Delete: removes row after confirmation

---

## 8. Admin — Run Controls `/admin/runs`

Four buttons: "Run Crawl" / "Run Enrich" / "Run Geocode" / "Run Dedup" — each invokes the corresponding edge function (ppp-crawl / ppp-enrich / ppp-geocode / ppp-dedup). Show spinner while running, log result in a scrollable output panel below.

Error log table below: query ppp_errors ordered by created_at desc, limit 100. Columns: Time, Function, Error Message, Type. Auto-refresh every 30 seconds.

---

## 9. Admin — Settings `/admin/settings`

Form bound to the single ppp_settings row:
- Confidence Threshold (number input, 0–1, step 0.05)
- Auto-publish Enabled (toggle)
- Is Running (toggle)
- Prompt Version (read-only)

"Save" button updates the row. Success toast on save.

---

## 10. Edge Functions

Create these four Supabase Edge Functions:

---

### `ppp-crawl`
Cron: `0 6 * * *` (daily 6am UTC). Also callable manually with optional body `{ source_id }`.

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

    let query = supabase.from('ppp_sources').select('*').eq('is_active', true)
    if (specificSourceId) query = query.eq('id', specificSourceId)
    const { data: sources, error: sourcesError } = await query
    if (sourcesError) throw sourcesError

    let totalInserted = 0

    for (const source of sources ?? []) {
      try {
        let rawRecords: any[] = []

        if (source.type === 'api' && source.url.includes('worldbank')) {
          let page = 1
          let hasMore = true
          while (hasMore) {
            const res = await fetch(`${source.url}?page=${page}&pageSize=100`)
            const json = await res.json()
            const projects = json.projects ?? json.data ?? []
            if (!projects.length) { hasMore = false; break }
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
            if (page > 50) hasMore = false
          }
        } else {
          const res = await fetch(source.url, {
            headers: { 'User-Agent': 'InfinityPPP/1.0 (global ppp directory research bot)' }
          })
          const html = await res.text()
          const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
          rawRecords = [{ source_url: source.url, source_name: source.name, raw_payload: { html_text: text.slice(0, 50000) } }]
        }

        for (const record of rawRecords) {
          if (!record.name && !record.source_url) continue
          const { count } = await supabase
            .from('ppp_raw')
            .select('id', { count: 'exact', head: true })
            .eq('source_url', record.source_url ?? '')
            .eq('name', record.name ?? '')
          if ((count ?? 0) > 0) continue

          const { error: insertError } = await supabase.from('ppp_raw').insert({
            ...record, processing_status: 'pending'
          })
          if (insertError) {
            await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: insertError.message })
          } else {
            totalInserted++
          }
        }

        await supabase.from('ppp_sources').update({
          last_crawled_at: new Date().toISOString(),
          record_count: (source.record_count ?? 0) + rawRecords.length
        }).eq('id', source.id)

      } catch (e: any) {
        await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: `Source ${source.name}: ${e.message}` })
      }
    }

    fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ppp-enrich`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` }
    }).catch(() => {})

    return new Response(JSON.stringify({ ok: true, inserted: totalInserted }), { headers: { 'Content-Type': 'application/json' } })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-crawl', error_message: err.message })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})

function normalizeSector(raw: string | null): string | null {
  if (!raw) return null
  const r = raw.toLowerCase()
  if (r.includes('energy') || r.includes('power') || r.includes('solar') || r.includes('wind')) return 'energy'
  if (r.includes('transport') || r.includes('road') || r.includes('rail') || r.includes('port') || r.includes('airport')) return 'transport'
  if (r.includes('water') || r.includes('sanitation')) return 'water'
  if (r.includes('health') || r.includes('hospital')) return 'health'
  if (r.includes('education') || r.includes('school')) return 'education'
  if (r.includes('telecom') || r.includes('broadband')) return 'telecoms'
  return 'social infrastructure'
}

function normalizeStatus(raw: string | null): string | null {
  if (!raw) return null
  const r = raw.toLowerCase()
  if (r.includes('pipeline') || r.includes('identified')) return 'pipeline'
  if (r.includes('procurement') || r.includes('tender') || r.includes('bid')) return 'procurement'
  if (r.includes('award') || r.includes('signed')) return 'awarded'
  if (r.includes('financial close')) return 'financial-close'
  if (r.includes('operat') || r.includes('active')) return 'operational'
  if (r.includes('complet') || r.includes('closed')) return 'completed'
  if (r.includes('cancel') || r.includes('terminat')) return 'cancelled'
  return 'pipeline'
}
```

---

### `ppp-enrich`
Triggered by ppp-crawl on completion. Also callable manually.

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
      .from('ppp_raw').select('*').eq('processing_status', 'pending').limit(100)

    let enriched = 0, queued = 0, failed = 0

    for (const record of pendingRecords ?? []) {
      try {
        const hasStructuredData = record.name && record.country && record.sector && record.status

        let extracted: any = {
          name: record.name, country: record.country,
          region: record.region ?? inferRegion(record.country),
          sector: record.sector, status: record.status,
          total_value_usd: record.total_value_usd,
          public_contribution_usd: record.public_contribution_usd,
          private_investment_usd: record.private_investment_usd,
          currency_original: record.currency_original,
          government_sponsor: record.government_sponsor,
          private_operator: record.private_operator,
          lenders: record.lenders, advisors: record.advisors,
          announcement_date: record.announcement_date,
          tender_date: record.tender_date, award_date: record.award_date,
          financial_close_date: record.financial_close_date,
          completion_date: record.completion_date,
          lat: record.lat, lng: record.lng,
          source_url: record.source_url, source_name: record.source_name,
        }

        if (!hasStructuredData && record.raw_payload?.html_text) {
          const aiPrompt = `Extract PPP project data from this text. Return ONLY a valid JSON array of objects. Each object must have these fields (use null for unknown): name, country, region, sector (one of: energy/transport/water/health/education/telecoms/social infrastructure), status (one of: pipeline/procurement/awarded/financial-close/operational/completed/cancelled), total_value_usd (number USD or null), public_contribution_usd, private_investment_usd, currency_original, government_sponsor, private_operator, lenders, advisors, announcement_date (YYYY-MM-DD or null), tender_date, award_date, financial_close_date, completion_date. Extract every distinct project mentioned. No preamble. No code fences.\n\nText:\n${record.raw_payload.html_text.slice(0, 8000)}`

          const aiRes = await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ai-complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` },
            body: JSON.stringify({ prompt: aiPrompt })
          })

          if (aiRes.ok) {
            const aiData = await aiRes.json()
            const rawText = aiData.text ?? aiData.content ?? '[]'
            const projects = JSON.parse(rawText)
            const arr = Array.isArray(projects) ? projects : [projects]
            for (let i = 1; i < arr.length; i++) {
              await supabase.from('ppp_raw').insert({
                ...arr[i], source_url: record.source_url, source_name: record.source_name,
                raw_payload: record.raw_payload, processing_status: 'pending'
              })
            }
            if (arr[0]) extracted = { ...extracted, ...arr[0] }
          }
        }

        const score = computeScore(extracted, record.source_name ?? '')
        await supabase.from('ppp_raw').update({ processing_status: 'processed', confidence_score: score }).eq('id', record.id)

        if (autoPublish && score >= threshold && extracted.name) {
          await supabase.from('ppp_projects').upsert(
            { ...extracted, confidence_score: score, updated_at: new Date().toISOString() },
            { onConflict: 'source_url,name' }
          )
          enriched++
        } else if (extracted.name || extracted.country) {
          await supabase.from('ppp_review_queue').insert({
            ppp_raw_id: record.id, extracted_fields: extracted, confidence_score: score
          })
          queued++
        }
      } catch (e: any) {
        await supabase.from('ppp_errors').insert({ function_name: 'ppp-enrich', error_message: e.message, raw_id: record.id })
        await supabase.from('ppp_raw').update({ processing_status: 'failed' }).eq('id', record.id)
        failed++
      }
    }

    fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/ppp-geocode`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` }
    }).catch(() => {})

    return new Response(JSON.stringify({ ok: true, enriched, queued, failed }), { headers: { 'Content-Type': 'application/json' } })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-enrich', error_message: err.message })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})

function computeScore(f: any, sourceName: string): number {
  const req = ['name','country','sector','status'].filter(k => f[k]).length / 4
  const opt = ['total_value_usd','government_sponsor','private_operator','announcement_date','region'].filter(k => f[k]).length / 5
  const bonus = sourceName.toLowerCase().includes('world bank') || sourceName.toLowerCase().includes('isdb') ? 0.15 : 0
  return Math.min(1, req * 0.6 + opt * 0.25 + bonus)
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

---

### `ppp-geocode`
Triggered by ppp-enrich on completion. Also callable manually.

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const CENTROIDS: Record<string, [number, number]> = {
  'Saudi Arabia': [23.8859, 45.0792], 'UAE': [23.4241, 53.8478], 'Egypt': [26.8206, 30.8025],
  'Jordan': [30.5852, 36.2384], 'Morocco': [31.7917, -7.0926], 'Tunisia': [33.8869, 9.5375],
  'Algeria': [28.0339, 1.6596], 'Iraq': [33.2232, 43.6793], 'Kuwait': [29.3759, 47.9774],
  'Qatar': [25.3548, 51.1839], 'Bahrain': [26.0275, 50.5500], 'Oman': [21.4735, 55.9754],
  'Libya': [26.3351, 17.2283], 'Lebanon': [33.8547, 35.8623], 'Syria': [34.8021, 38.9968],
  'Yemen': [15.5527, 48.5164], 'Israel': [31.0461, 34.8516], 'Palestine': [31.9522, 35.2332],
  'Nigeria': [9.0820, 8.6753], 'Kenya': [-0.0236, 37.9062], 'Ghana': [7.9465, -1.0232],
  'Ethiopia': [9.1450, 40.4897], 'South Africa': [-30.5595, 22.9375], 'Tanzania': [-6.3690, 34.8888],
  'India': [20.5937, 78.9629], 'Pakistan': [30.3753, 69.3451], 'Bangladesh': [23.6850, 90.3563],
  'Indonesia': [-0.7893, 113.9213], 'Vietnam': [14.0583, 108.2772], 'Philippines': [12.8797, 121.7740],
  'Thailand': [15.8700, 100.9925], 'Malaysia': [4.2105, 101.9758],
}

Deno.serve(async (_req) => {
  try {
    const token = Deno.env.get('MAPBOX_PUBLIC_TOKEN')
    const { data: projects } = await supabase
      .from('ppp_projects').select('id,name,country,lat,lng')
      .or('lat.is.null,lng.is.null').limit(200)

    let resolved = 0, fallback = 0

    for (const p of projects ?? []) {
      let lat: number | null = null, lng: number | null = null

      if (token) {
        try {
          const q = encodeURIComponent(`${p.name}, ${p.country}`)
          const res = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${q}.json?access_token=${token}&limit=1`)
          const geo = await res.json()
          if (geo.features?.[0]) { [lng, lat] = geo.features[0].center; resolved++ }
        } catch (_e) {}
      }

      if (lat === null && p.country && CENTROIDS[p.country]) {
        [lat, lng] = CENTROIDS[p.country]
        fallback++
      }

      if (lat !== null && lng !== null) {
        await supabase.from('ppp_projects').update({ lat, lng }).eq('id', p.id)
      }
    }

    return new Response(JSON.stringify({ ok: true, resolved, fallback }), { headers: { 'Content-Type': 'application/json' } })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-geocode', error_message: err.message })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})
```

---

### `ppp-dedup`
Cron: `0 6 * * 0` (weekly, Sundays 6am UTC). Also callable manually.

First run this SQL in Supabase to enable similarity matching:
```sql
create extension if not exists pg_trgm;

create or replace function find_ppp_duplicates()
returns table(id_a uuid, name_a text, id_b uuid, name_b text, country text, similarity float) as $$
  select a.id, a.name, b.id, b.name, a.country, similarity(a.name, b.name)
  from ppp_projects a join ppp_projects b
    on a.country = b.country and a.id < b.id and similarity(a.name, b.name) > 0.85
$$ language sql stable;
```

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

Deno.serve(async (_req) => {
  try {
    const { data: duplicates, error } = await supabase.rpc('find_ppp_duplicates')
    if (error) throw error

    let flagged = 0
    for (const pair of duplicates ?? []) {
      const { data: existing } = await supabase
        .from('ppp_review_queue').select('id')
        .eq('reviewer_notes', `Potential duplicate of project ID ${pair.id_a}`).single()
      if (existing) continue

      const { data: rawShell } = await supabase.from('ppp_raw').insert({
        name: pair.name_b, country: pair.country, source_name: 'dedup-detector',
        processing_status: 'processed', raw_payload: { duplicate_of: pair.id_a }
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

    return new Response(JSON.stringify({ ok: true, flagged }), { headers: { 'Content-Type': 'application/json' } })
  } catch (err: any) {
    await supabase.from('ppp_errors').insert({ function_name: 'ppp-dedup', error_message: err.message })
    return new Response(JSON.stringify({ ok: false, error: err.message }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
})
```

Set cron for ppp-dedup: `0 6 * * 0`
Set cron for ppp-crawl: `0 6 * * *`

---

## 11. Design

Use a clean, institutional design language throughout:
- Color scheme: dark navy (#0F172A) and white, with slate greys for secondary elements
- Typography: clean sans-serif, professional
- Status badges: use the pin colors defined above consistently everywhere (map, cards, detail page, admin)
- The public site should feel like a serious data product, not a startup landing page
- The admin panel should feel like an internal tool — functional, dense, efficient
