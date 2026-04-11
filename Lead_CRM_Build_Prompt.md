# Lead CRM Builder — Claude Code Prompt

> Paste this entire prompt into Claude Code in VS Code. Open the **`Forrest Analytics Group LLC`** folder as your project root. Everything you build lives inside a new `lead-crm/` subfolder so the parent folder stays clean.
>
> Put your `.env` file with API keys inside `lead-crm/`, not the parent folder.
>
> Expected final layout:
> ```
> Forrest Analytics Group LLC/
> ├── lead-crm/
> │   ├── .env
> │   ├── README.md
> │   ├── requirements.txt
> │   ├── config.py
> │   ├── src/
> │   │   ├── sources/           # one module per data source
> │   │   ├── enrich.py          # email/website/contact enrichment
> │   │   ├── score.py           # AI-fit scoring
> │   │   ├── dedupe.py
> │   │   ├── export.py          # writes the Excel CRM
> │   │   └── main.py            # orchestrator
> │   ├── cache/                 # cached API responses so reruns are free
> │   ├── output/
> │   │   └── Forrest_Analytics_Lead_CRM.xlsx
> │   └── logs/
> ```

---

## Role and Mission

You are my senior data engineer. I am Josh Forrest, owner of **Forrest Analytics Group LLC**, a one-person AI consultancy in the Philadelphia metro. I sell four AI products to small service businesses: a 24/7 AI Voice Receptionist, a Review Reply & Reputation Manager, a Customer Re-Engagement Engine, and an Owner's Daily Briefing. My average deal is around $1,995/month with an $18,500 setup fee.

I need a working Python pipeline that builds me a **high-quality lead CRM of exactly 800 small service businesses** across the Philadelphia / South Jersey / Delaware / Main Line region, delivered as a polished Excel workbook I can work from tomorrow morning. These are the businesses I'll cold-email and cold-call. Quality matters ten times more than quantity — I'd rather have 800 hand-picked leads with accurate contact info than 8,000 garbage rows.

Your job: build the scraping + enrichment + scoring + export pipeline end-to-end, run it, and produce the final `.xlsx` file.

---

## Target Verticals (aim for roughly even distribution — ~65–70 per vertical)

1. Plumbing
2. HVAC
3. Lawn Care & Landscaping
4. Electrical
5. Cleaning (residential + commercial)
6. Pest Control
7. Roofing
8. Auto Repair (independent shops, not dealerships)
9. Salon & Spa
10. Painting
11. General Contracting / Remodeling
12. Property Management (small-to-mid portfolios)

---

## Target Geography

Focus on the Greater Philadelphia area, in roughly this priority order:

1. **Main Line + Western Suburbs** (Ardmore, Bryn Mawr, Wayne, Paoli, Malvern, West Chester, King of Prussia, Devon, Berwyn)
2. **Philadelphia proper** (all neighborhoods, but emphasize NE Philly, South Philly, NW Philly — blue-collar and middle-class zones where service businesses cluster)
3. **Bucks & Montgomery County** (Doylestown, Newtown, Lansdale, Blue Bell, Willow Grove)
4. **Delaware County** (Media, Havertown, Springfield)
5. **South Jersey** (Cherry Hill, Voorhees, Marlton, Mount Laurel, Haddonfield)
6. **Northern Delaware** (Wilmington, Newark, Hockessin)

Use zip codes as the actual search units — the file `config.py` should contain a curated list of ~60 zip codes covering the above regions, and the pipeline iterates verticals × zips.

---

## Data Sources (use in this priority order, all legal and ToS-compliant)

1. **Google Places API (Text Search + Place Details)** — primary source. Rich, accurate, includes phone, website, rating, review count, business hours. Requires `GOOGLE_PLACES_API_KEY` in `.env`. Budget-aware: cache every response to `cache/google_places/` keyed by query hash so reruns cost nothing.
2. **Yelp Fusion API** — secondary source for cross-validation and extra fields (price range, categories). Requires `YELP_API_KEY`.
3. **OpenStreetMap via Overpass API** — free fallback for coverage gaps, especially in smaller towns.
4. **Business website scraping** — for each lead with a website, fetch the homepage + `/contact` + `/about` and extract: owner name (if listed), direct email, additional phones, "years in business," service area, social links. Respect `robots.txt` and rate-limit to 1 req/sec per domain. Use `httpx` + `selectolax` for speed.
5. **Public state business registries** (PA Department of State corporations search, NJ Division of Revenue, DE Division of Corporations) — only if the owner name isn't discoverable from the website. These are public records.

**Do NOT** scrape LinkedIn, Facebook, Instagram, or any site where scraping violates ToS. Do NOT use stolen data broker lists. Do NOT guess or fabricate email addresses — if we can't find a real one, leave it blank and mark the lead for phone-first outreach.

---

## Quality Filters (aggressive — this is the whole point)

A business qualifies for the CRM only if it meets **all** of these:

- Has a phone number
- Has a Google listing with **at least 10 reviews** (proves they're a real operating business)
- Rating between **3.5 and 4.8** stars (too low = struggling or fake, too high + few reviews = new or suspicious)
- Is clearly a **small business**: no national chains, no franchises of 50+ locations, no enterprise. Filter out anything matching a configurable chain blocklist (Roto-Rooter, Mr. Rooter, ServiceMaster, Stanley Steemer, Merry Maids, Orkin, Terminix, etc.).
- Is **not permanently closed** (check `business_status`).
- Appears to have a website OR at minimum a Google Business Profile (pure phone-only leads go in a separate tab).
- For auto repair: independents only — filter out dealerships.
- For property management: portfolios that look small-to-mid (avoid giant REITs).

Then apply a **signal scoring layer** that ranks leads by how likely our AI products are to help them. See the scoring section below.

---

## Enrichment (for every lead that passes filters)

For each qualifying business, enrich with:

- Website URL (cleaned, normalized)
- Owner first name + last name (from website, state business registry, or LLM extraction from "About" page)
- Direct email (from contact page — never fabricated)
- Generic email (info@, contact@) as fallback
- Years in business (from "Since YYYY" on website)
- Number of employees estimate (from website clues or Google/Yelp categories)
- Service area (cities/zips mentioned)
- Whether they currently have online booking (yes/no)
- Whether they have a chatbot on their site (yes/no)
- Whether they respond to reviews (check last 5 Google reviews for owner responses)
- Social links (Facebook, Instagram — just the URLs, no scraping of content)
- Last 3 review snippets (for personalization in cold emails)

Use Claude (model: `claude-sonnet-4-6`) via the Anthropic Python SDK to extract owner names and emails from scraped HTML when regex won't do it. Keep temperature at 0.1 for extraction. Cache every LLM response.

---

## AI-Fit Scoring (0–100)

Write `src/score.py` with a transparent scoring function that produces an **AI Fit Score** from 0 to 100 for each lead. Higher = better fit for our four AI products. The scoring signals:

- **+20** if they have 50+ Google reviews (volume = they get calls)
- **+15** if rating is 4.0–4.5 (sweet spot: room to improve, not broken)
- **+15** if they do NOT currently respond to reviews (Review Reply Manager fit)
- **+15** if they have no online booking widget (Voice Receptionist fit)
- **+10** if their website looks dated (no SSL, no mobile meta tag, pre-2020 design cues)
- **+10** if they have 5+ years in business (established, have a customer list = Re-Engagement fit)
- **+5** if the owner's name is discoverable (better cold outreach)
- **+5** if their service area spans multiple zip codes (bigger operation, bigger budget)
- **+5** if they have emergency/24-7 messaging on their site (pain point = missed after-hours calls)

Sort the final CRM by AI Fit Score descending. Everything 70+ goes in a "Priority A" tab, 50–69 in "Priority B," below 50 in "Priority C."

For the top 50 leads (Priority A), also use Claude to generate a **2-sentence personalization hook** referencing something specific from their reviews or website — this is what I'll paste into cold emails.

---

## Excel Workbook Structure (this is the deliverable)

Use `openpyxl` to build `output/Forrest_Analytics_Lead_CRM.xlsx` with the following sheets. Format it professionally — frozen header rows, filters on every column, banded rows, column widths auto-fit, navy header background with white bold text, Forrest Analytics branding in the first cell of each sheet.

**Sheet 1 — Dashboard**
- Total leads, count by vertical, count by county, count by priority tier
- Top 10 leads by score
- Average AI Fit Score by vertical
- Simple bar chart (built with openpyxl's native chart API) showing leads per vertical
- A "How to use this CRM" callout box

**Sheet 2 — All Leads (master)**
Columns in this order: Lead ID, Priority (A/B/C), AI Fit Score, Business Name, Vertical, Owner Name, Phone, Email, Website, Street, City, State, Zip, County, Google Rating, Review Count, Years in Business, Employees (est.), Has Website, Has Online Booking, Responds to Reviews, Has Chatbot, Last Job Signal, Facebook URL, Instagram URL, Google Maps URL, Yelp URL, Personalization Hook, Outreach Status, Last Contacted, Next Action, Notes.

"Outreach Status" should be a data-validated dropdown: `Not Contacted / Emailed / Called / Replied / Meeting Booked / Proposal Sent / Won / Lost / Nurture`. Default every row to "Not Contacted."

"Next Action" dropdown: `Send Cold Email / Cold Call / LinkedIn Connect / Follow-up / Wait`. Default to "Send Cold Email" for Priority A, "Cold Call" for Priority B, blank for C.

**Sheet 3 — Priority A (Hot)** — filtered view of score ≥70, sorted descending
**Sheet 4 — Priority B (Warm)** — 50–69
**Sheet 5 — Priority C (Cold)** — under 50
**Sheet 6 — By Vertical** — pivot-style breakdown with a filter dropdown
**Sheet 7 — Cold Email Templates** — four pre-written cold email templates I can use, one per AI product, with `{{merge_fields}}` that match the columns on Sheet 2
**Sheet 8 — Source Log** — every API call made, cache hits, quality filter rejections (for transparency)

---

## Tech Stack

- Python 3.11
- `httpx` for HTTP, `selectolax` for HTML parsing, `tenacity` for retries
- `googlemaps` or raw HTTP for Places API
- `anthropic` SDK for LLM enrichment (model `claude-sonnet-4-6`)
- `openpyxl` for the Excel file (no pandas-to-excel — you need fine-grained formatting control)
- `pydantic` for lead schemas
- `rich` for beautiful CLI logging while it runs
- `python-dotenv` for env vars
- `diskcache` or simple JSON file cache for API responses

Rate-limit everything. Be respectful. Log every source, every decision, every filter rejection to `logs/run.log` so I can audit the output.

---

## Run Modes

`main.py` should support three modes:

- `--mode=scrape` : only fetch and cache raw results (no enrichment, no Excel)
- `--mode=enrich` : run website + LLM enrichment on cached results
- `--mode=export` : build the Excel file from enriched data
- `--mode=full` : run the whole pipeline end to end
- `--limit=N` : useful for testing — stop after N qualified leads per vertical

Default run: `python src/main.py --mode=full --target=800`

---

## Deliverables

1. The complete working pipeline in `lead-crm/`
2. A populated `output/Forrest_Analytics_Lead_CRM.xlsx` with exactly 800 leads (or as close to 800 as the quality filters allow — never pad with junk to hit the number)
3. A `README.md` with: setup steps, env vars required, how to get API keys, how to rerun, how to extend to new verticals or zip codes, and estimated API cost per run
4. A `DECISIONS.md` explaining any tradeoffs you made

---

## Acceptance Criteria

- The Excel file opens cleanly in Microsoft Excel on Windows and looks professionally formatted
- I can filter the All Leads sheet by vertical, county, or priority and immediately start calling
- At least 90% of rows have a valid phone number
- At least 60% of rows have a valid website
- At least 40% of rows have an owner first name
- Zero fabricated email addresses — every email is from a real contact page or public record
- The top 50 Priority A leads each have a unique, specific personalization hook
- Rerunning the pipeline uses cached data and costs $0 in new API calls

---

## Before You Start

Before writing any code, do these things in order:

1. Read this entire prompt and summarize back to me in 8 bullets what you're about to build
2. List every API key / credential you'll need from me and what each one costs at expected volume
3. Estimate total API cost for a full run (Google Places + Yelp + Claude enrichment)
4. Ask me any genuinely blocking questions in a single batched list
5. Then build the scaffold, then the sources, then enrichment, then scoring, then export, then run it

Quality bar: this CRM is the single asset that determines whether Forrest Analytics Group hits weekly revenue this quarter. Treat it like that.
