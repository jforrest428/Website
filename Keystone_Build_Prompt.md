# Keystone Plumbing AI Case Study — Build Prompt for Claude Code

> Paste this entire prompt into Claude Code in VS Code. Open the **`Forrest Intelligence`** folder as your project root. The dataset file `Keystone_Plumbing_Sample_Dataset.xlsx` and the case study doc `Keystone_AI_Products_Case_Study.docx` are already sitting in that folder.
>
> **Read them from the project root (`./Keystone_Plumbing_Sample_Dataset.xlsx` and `./Keystone_AI_Products_Case_Study.docx`) and, as your very first step, create the `keystone-case-study/` subfolder and copy the xlsx into `keystone-case-study/data/`.** Everything you build lives inside that subfolder so the parent Forrest Intelligence folder stays clean.
>
> **Put the `.env` file with `ANTHROPIC_API_KEY` (and optionally `ELEVENLABS_API_KEY`) inside `keystone-case-study/`, not the parent folder**, so all scripts pick it up automatically with `python-dotenv`.
>
> Expected final layout:
> ```
> Forrest Intelligence/
> ├── Keystone_Plumbing_Sample_Dataset.xlsx   (original, untouched)
> ├── Keystone_AI_Products_Case_Study.docx    (original, untouched)
> ├── Keystone_Build_Prompt.md                (this file)
> └── keystone-case-study/                    (everything you build goes here)
>     ├── .env
>     ├── data/
>     ├── shared/
>     ├── products/
>     ├── keystone_site/
>     └── forrest_case_study/
> ```

---

## Role and Mission

You are my senior full-stack engineer and AI product builder. I am Josh Forrest, owner of **Forrest Intelligence**. I'm building a high-quality sample case study around a fictional Philadelphia plumbing company called **Keystone Plumbing & Drain** to showcase four AI products to real small-business prospects (plumbers, HVAC, lawn care, electricians). The end result will live on my website `forrestintelligence.com` as a flagship case study and be the thing I send to every cold lead.

Your job is to build all of this end-to-end at production quality: a Keystone demo website, four working AI products powered by the Claude API and the sample dataset, a Forrest Intelligence case study page embedding the demos, and clean documentation. Do not stub or fake anything you can actually build. Where an integration is out of scope (e.g. real telephony), build a realistic scripted simulation that is visually and functionally convincing.

Work autonomously. Ask me a clarifying question only when a decision genuinely blocks you. Otherwise pick the strongest option, document your reasoning in a `DECISIONS.md` file, and keep moving.

---

## Repo Structure to Create

```
keystone-case-study/
├── README.md
├── DECISIONS.md
├── .env.example
├── data/
│   └── Keystone_Plumbing_Sample_Dataset.xlsx
├── shared/
│   ├── data_loader.py          # load xlsx into pandas DataFrames
│   ├── claude_client.py        # thin Anthropic SDK wrapper with retry + logging
│   └── brand.py                # Keystone voice, tone, brand constants
├── products/
│   ├── 01_daily_briefing/
│   ├── 02_review_reply/
│   ├── 03_reengagement/
│   └── 04_voice_receptionist/
├── keystone_site/              # Next.js 14 + Tailwind — Keystone demo landing page
└── forrest_case_study/         # Next.js page + MDX for the Forrest Intelligence case study
```

Use Python 3.11 for the AI product backends, FastAPI where an API surface is needed, Streamlit for quick owner-approval UIs, and Next.js 14 + Tailwind + shadcn/ui for both websites. Use the official `anthropic` Python SDK with model `claude-sonnet-4-6`. Store the API key in `.env` and load it with `python-dotenv`. Never hardcode secrets.

---

## Existing Assets You Must Use

The file `data/Keystone_Plumbing_Sample_Dataset.xlsx` contains real synthetic operational data for a fictional plumber. Sheets:

- **Customers** (850 rows): Customer ID, Name, Type, Phone, Email, Address, City, State, Zip, Lead Source, Created, Lifetime Jobs
- **Jobs** (2,400 rows): Job ID, Customer ID, Customer Name, Job Type, Category, Priority, Scheduled, Completed, Status, Tech ID, Tech Name, Hours, Revenue, Parts Cost, Labor Cost, COGS, Margin, Rating, City, Zip
- **Invoices** (2,266 rows): Invoice ID, Job ID, Customer ID, Customer Name, Invoice Date, Subtotal, Tax, Total, Paid, Paid Date, Days to Pay, Payment Method, Status
- **Calls** (3,200 rows): Call ID, Timestamp, Phone, Duration (min), Answered, After Hours, Lead Source, Intent, Booked, Converted, Revenue Attributed
- **Reviews** (420 rows): Review ID, Date, Platform, Stars, Review Text, Responded, Tech Mentioned
- **Technicians** (8 rows): Tech ID, Name, License, Level, Years Experience, Avg Rating
- **Parts Inventory** (~25 rows): Part ID, Description, Category, Unit Cost, On Hand
- **Summary KPIs**: precomputed top-line numbers

Every AI product must read real data from this file. No mocked JSON.

---

## The Four Products to Build

### Product 1 — Owner's Daily Briefing (build first — highest ROI per hour)

**What it does.** Every morning at 6am, an owner receives a plain-English, 60-second text message summarizing their business: yesterday's revenue vs same day last year, today's full schedule, anything overdue in A/R, any negative review that needs attention, any unusually big opportunity in the pipeline.

**Build:**
- Python script `products/01_daily_briefing/generate_briefing.py` that takes a `--date` flag (default: most recent date in the dataset).
- Pulls: yesterday's completed jobs + revenue, today's scheduled jobs, invoices >14 days old, 1–2 star reviews from the last 7 days that aren't responded to, any job >$5k in the pipeline.
- Builds a structured JSON context and passes it to Claude with a system prompt that enforces: warm owner-to-owner tone, plain English, no jargon, 180 words max, SMS-friendly formatting.
- Outputs both the raw context JSON and the final SMS text to `products/01_daily_briefing/output/{date}.json` and `.txt`.
- Also exposes `briefing_for_date(date) -> str` as an importable function.
- Add a tiny Streamlit viewer `app.py` that shows the last 30 days of briefings as a mock phone thread (iMessage-style bubbles) for the demo video.

**Acceptance:** I can run `python generate_briefing.py --date 2026-04-07` and get a briefing that is specific, accurate against the dataset, and reads like a real text from a smart ops person.

### Product 2 — Review Reply & Reputation Manager

**What it does.** Monitors all 420 reviews, drafts personalized, on-brand replies, and presents them to the owner for one-click approval. Flags patterns (e.g., repeat negative mentions of one tech).

**Build:**
- Python pipeline `products/02_review_reply/draft_replies.py` that loops the Reviews sheet, filters for reviews where Responded == 'No' OR (Stars <= 2 AND any flag), and drafts a reply for each.
- System prompt must enforce Keystone's voice: warm, accountable, specific to the review content, never defensive, offers a make-right on 1–2 star reviews, and signs off as "— Mike, Owner, Keystone Plumbing."
- Pattern analyzer `patterns.py`: groups the last 30 days of negative reviews by tech, surfaces any tech with 2+ negative mentions.
- Streamlit owner-approval UI `app.py` with three panes: review text + metadata on the left, drafted reply on the right (editable textarea), and Approve / Edit / Skip buttons. "Approved" writes to a local `approvals.jsonl` log.
- Include a small Tech Coaching Report view that shows the pattern analyzer output.

**Acceptance:** I can launch the Streamlit app, page through 10+ real reviews, see drafts that are noticeably better than generic canned replies, and the pattern analyzer correctly identifies the tech with the most negative mentions in the dataset.

### Product 3 — Customer Re-Engagement Engine

**What it does.** Segments the 850-customer list weekly, writes personalized outreach for each segment, projects recovered revenue.

**Build:**
- `products/03_reengagement/segment.py`: runs the segmentation. Required segments:
  1. Water heater installs > 5 years ago (look up job history)
  2. Sump pump customers where the install was before the last winter season
  3. Drain cleaning customers > 18 months since last service
  4. Annual maintenance lapsed > 13 months
  5. High-LTV customers ($3k+ lifetime) with no job in 9+ months
- For each customer in each segment, call Claude to generate a personalized SMS (≤160 chars) and a personalized email (subject + body), referencing the original service date and job type. Tone is friendly, specific, not salesy.
- Output to `products/03_reengagement/output/{segment_name}.csv` with columns: Customer ID, Name, Phone, Email, Last Service, Months Since, SMS Draft, Email Subject, Email Body.
- Projected revenue calculator that multiplies segment size × a reasonable reactivation rate (8–15%) × average job value for that job type.
- A Streamlit dashboard `app.py` showing segment sizes, projected recovered revenue, and a drill-down into sample messages per segment.

**Acceptance:** The dashboard shows all five segments, realistic projected numbers grounded in actual dataset values, and sample messages that reference real historical jobs from the dataset.

### Product 4 — 24/7 AI Voice Receptionist (Scripted Demo Version)

**What it does.** Answers inbound calls 24/7, diagnoses the issue, books an appointment, texts a confirmation, escalates emergencies.

**Build (two layers):**

*Layer A — the brain (real Claude implementation):*
- `products/04_voice_receptionist/agent.py` implements a `ReceptionistAgent` class with a `handle_turn(transcript_so_far, latest_user_message)` method that returns the next agent message.
- System prompt enforces: always greet as "Keystone Plumbing, this is Dawn, how can I help?", triage for emergencies (burst pipe, no water, sewage backup, no heat in winter, gas smell), collect name + address + phone + problem description, offer 3 concrete appointment slots, book one, confirm.
- Structured tool-use: define tools `get_available_slots(date_range)`, `book_appointment(customer, slot, issue)`, `send_sms_confirmation(phone, details)`. Implement them against the dataset (jobs sheet) as fakes that actually return realistic values and log to `call_log.jsonl`.
- Emergency escalation: if the model classifies an issue as emergency, it calls `escalate_to_oncall(tech_id, caller_info)` instead of normal booking.

*Layer B — the demo:*
- `products/04_voice_receptionist/scripted_demo.py` runs a scripted conversation (4 scenarios: after-hours burst pipe, daytime water heater quote, clogged drain routine booking, commercial property manager) through the agent and prints a beautiful transcript.
- Generate audio using ElevenLabs if an API key is present in `.env` (optional — skip gracefully if not). Save MP3 files to `products/04_voice_receptionist/audio/`.
- Produce a `demo_script.md` that a human can read over recorded audio for a marketing video.

**Acceptance:** Running `scripted_demo.py` produces four full transcripts where the agent correctly triages, books, and escalates. The tool calls write realistic entries to `call_log.jsonl`.

---

## Keystone Sample Website (`keystone_site/`)

Build a single-page Next.js 14 site using the App Router, Tailwind, and shadcn/ui components. This site is the *stage* for the AI products.

Sections, top to bottom:
1. **Hero:** "Keystone Plumbing & Drain — Philadelphia's trusted plumber since 2014." CTA: "Call Now" and "Book Online."
2. **Services grid:** plumbing, drain, water heaters, sewer, sump pumps, light HVAC. Icons from lucide-react.
3. **Live demo strip (the point of the whole site):** four interactive cards, one per AI product:
   - "Call our AI Receptionist" → opens a modal that plays the scripted demo transcript with typed-out messages + optional audio playback.
   - "See how we reply to reviews" → opens a modal showing the Review Reply Manager UI embedded as an iframe from the Streamlit app (or a static screenshot if the Streamlit isn't hosted).
   - "Watch us wake up dormant customers" → modal with the Re-Engagement dashboard + sample messages.
   - "Owner's Daily Briefing" → modal styled as an iMessage thread showing real briefings from the dataset.
4. **Testimonials:** two fake-but-realistic testimonials citing the AI products.
5. **Footer:** "Built by Forrest Intelligence — AI for service businesses" with a link back to `forrestintelligence.com`.

Use a warm, trustworthy color palette (navy + a pop of safety orange). Real-looking copy. Mobile-first responsive. The site should take under 500ms to load and feel like a real plumbing company's site, not a developer demo.

---

## Forrest Intelligence Case Study Page (`forrest_case_study/`)

A standalone Next.js page (or MDX component) that I can drop into my existing Forrest Intelligence website. Structure:

1. **Headline:** "How we'd rebuild a $2.1M plumbing company with AI — a Keystone Plumbing case study."
2. **The company** (pulled from the case study doc — short profile block).
3. **The pain points** — four hero stats pulled from the Summary KPIs sheet: 29% of calls missed, 55% review response rate, 42% dormant customers, 11-day average A/R. Each stat has a one-line consequence in dollars.
4. **Four product sections** — one per AI product. Each section has: headline copy (from the doc), how it works (3–4 sentences), a live embedded demo (Loom embed placeholder OR the interactive modal from the Keystone site), and the ROI math.
5. **Architecture diagram:** simple mermaid or SVG showing data → Claude → outputs.
6. **Download the dataset** button (links to the xlsx).
7. **Lead magnet CTA:** "How many calls did your shop miss last month? Book a free 15-minute audit."
8. Typography and layout should match a premium consulting site — think Basecamp, Linear, or Vercel marketing pages.

---

## Shared Quality Bar

- **Every Claude call** must use a well-structured system prompt, explicit output format, and temperature appropriate to the task (0.3 for briefings and replies, 0.7 for outreach messages).
- **Every script** must be runnable with one command and documented in the product's own `README.md`.
- **Every product** must have at least one end-to-end test that asserts the output is well-formed (Pydantic schemas preferred).
- **Logging:** use `rich` for CLI output so demos look professional when screen-recorded.
- **No placeholder content** in anything I'll ship. If you invent something (a tech name, a testimonial), make it realistic and consistent with the dataset.
- **Cost-aware:** cache Claude responses in `.cache/` keyed by input hash so re-running demos is free.

---

## Deliverables and Build Order

Build in this exact order and commit after each phase:

1. Repo scaffold + `shared/` utilities + `.env.example` + top-level README
2. **Product 1 — Daily Briefing** (ship first, screenshot for marketing)
3. **Product 2 — Review Reply Manager**
4. **Product 3 — Re-Engagement Engine**
5. **Product 4 — Voice Receptionist** (scripted demo layer first, then the agent layer)
6. **Keystone sample website** — wire in modals that surface each product's outputs
7. **Forrest Intelligence case study page**
8. `DECISIONS.md` summarizing every significant choice you made
9. A final `DEMO.md` with a step-by-step script for me to record a 5-minute walkthrough video

Before you start coding, read both `Keystone_Plumbing_Sample_Dataset.xlsx` and `Keystone_AI_Products_Case_Study.docx` carefully and summarize back to me in 10 bullets what you understand the mission to be. Then propose any decisions you'd like my input on in a single batched question. Then get to work.

When you finish, produce a `README.md` at the repo root with quickstart instructions, a gallery of screenshots, and the exact commands to run each demo.

Quality bar: everything I build here will be shown to paying small-business owners in Philadelphia. Make it look and feel like something built by a senior consulting firm, not a weekend project.
