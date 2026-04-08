# Keystone Plumbing & Drain — AI Case Study
**Built by Forrest Analytics Group LLC**

A complete AI implementation portfolio piece: four working AI products built on a synthetic Philadelphia plumbing company's operational dataset. Every demo is live, every number is real, and nothing is mocked at the data layer.

---

## What's Inside

| Product | Description | Command |
|---------|-------------|---------|
| **01 Daily Briefing** | 6am SMS with yesterday's revenue, schedule, A/R, reviews | `python products/01_daily_briefing/generate_briefing.py` |
| **02 Review Reply** | AI-drafted replies + 1-click approval + pattern analysis | `streamlit run products/02_review_reply/app.py` |
| **03 Re-Engagement** | 5-segment customer outreach with projected revenue | `streamlit run products/03_reengagement/app.py` |
| **04 Voice Receptionist** | 24/7 call agent with booking + emergency escalation | `python products/04_voice_receptionist/scripted_demo.py` |
| **Keystone Site** | Demo landing page with interactive modals | `cd keystone_site && npm run dev` |
| **Case Study Page** | FAG case study for forrestanalyticsgroup.com | `cd forrest_case_study && npm run dev` |

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- An Anthropic API key

### 2. Clone and configure
```bash
cd keystone-case-study
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the tests (no API key needed)
```bash
python -m pytest products/ -v
```
All 27 tests should pass.

### 5. Run Product 1 — Daily Briefing
```bash
python products/01_daily_briefing/generate_briefing.py --date 2026-04-07
```
This will generate a briefing using real data from the dataset and Claude.

### 6. Run the Streamlit demos
```bash
# Review Reply Manager
streamlit run products/02_review_reply/app.py

# Re-Engagement Dashboard
streamlit run products/03_reengagement/app.py

# Daily Briefing Viewer
streamlit run products/01_daily_briefing/app.py
```

### 7. Run the Voice Receptionist demo
```bash
python products/04_voice_receptionist/scripted_demo.py
```
Runs all 4 scripted scenarios through the live Claude agent. Results logged to `products/04_voice_receptionist/call_log.jsonl`.

### 8. Launch the Keystone website
```bash
cd keystone_site
npm install
npm run dev
# Open http://localhost:3000
```

### 9. Launch the case study page
```bash
cd forrest_case_study
npm install
npm run dev
# Open http://localhost:3000
```

---

## Directory Structure

```
keystone-case-study/
├── .env.example                  ← Copy to .env, add API key
├── requirements.txt
├── README.md                     ← This file
├── DECISIONS.md                  ← Architectural decisions log
├── DEMO.md                       ← 5-minute video walkthrough script
│
├── data/
│   └── Keystone_Plumbing_Sample_Dataset.xlsx   ← Source of truth
│
├── shared/
│   ├── data_loader.py            ← Typed DataFrame accessors
│   ├── claude_client.py          ← Anthropic SDK wrapper (cache + retry)
│   └── brand.py                  ← Keystone voice, brand constants, system prompts
│
├── products/
│   ├── 01_daily_briefing/
│   │   ├── generate_briefing.py  ← CLI: python generate_briefing.py --date YYYY-MM-DD
│   │   ├── app.py                ← Streamlit: iMessage viewer
│   │   ├── test_briefing.py      ← 6 tests
│   │   └── output/               ← {date}.json + {date}.txt (generated)
│   │
│   ├── 02_review_reply/
│   │   ├── draft_replies.py      ← CLI: drafts replies for all unresponded reviews
│   │   ├── patterns.py           ← Pattern analyzer (tech coaching report)
│   │   ├── app.py                ← Streamlit: approval queue
│   │   ├── test_review_reply.py  ← 7 tests
│   │   ├── drafts.jsonl          ← Generated draft store
│   │   └── approvals.jsonl       ← Approved replies log
│   │
│   ├── 03_reengagement/
│   │   ├── segment.py            ← 5-segment engine + revenue projector
│   │   ├── app.py                ← Streamlit: dashboard
│   │   ├── test_reengagement.py  ← 7 tests
│   │   └── output/               ← {segment_name}.csv (generated)
│   │
│   └── 04_voice_receptionist/
│       ├── agent.py              ← ReceptionistAgent class (real Claude + tools)
│       ├── scripted_demo.py      ← 4-scenario scripted demo
│       ├── demo_script.md        ← Marketing video script
│       ├── test_receptionist.py  ← 7 tests
│       ├── call_log.jsonl        ← Tool call log (generated)
│       └── audio/                ← MP3 files (ElevenLabs, optional)
│
├── keystone_site/                ← Next.js 14 demo site
│   └── app/
│       ├── page.tsx              ← Main page (Hero, Services, AI Demo, Testimonials)
│       ├── lib/demo-data.ts      ← Pre-generated demo data
│       └── components/
│           ├── ModalBase.tsx
│           ├── BriefingModal.tsx
│           ├── ReviewModal.tsx
│           ├── ReengagementModal.tsx
│           └── ReceptionistModal.tsx
│
└── forrest_case_study/           ← Next.js 14 case study page for FAG website
    └── app/
        └── page.tsx              ← Full case study (pain points, products, ROI, CTA)
```

---

## Dataset Overview

| Sheet | Rows | Key Fields |
|-------|------|------------|
| Customers | 850 | ID, Name, Type, Phone, Email, Address, Lead Source |
| Jobs | 2,400 | Job Type, Status, Revenue, Tech, Margin, Rating |
| Invoices | 2,266 | Total, Paid, Days to Pay, Status |
| Calls | 3,200 | Answered, After Hours, Intent, Booked, Converted |
| Reviews | 420 | Platform, Stars, Review Text, Responded, Tech Mentioned |
| Technicians | 8 | Name, License, Level, Experience, Avg Rating |
| Parts Inventory | 25 | Description, Category, Unit Cost, On Hand |
| Summary KPIs | — | Pre-computed top-line metrics |

---

## Key Dataset Facts
- Date range: April 2024 – April 2026
- Total revenue: $3.29M (2-year)
- Missed-call revenue risk: $621K
- Unanswered reviews: 78
- David Chen: most negative review mentions (3 in last 90 days)

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | Anthropic API key for Claude |
| `ELEVENLABS_API_KEY` | ❌ Optional | ElevenLabs TTS for voice receptionist audio |
| `ELEVENLABS_VOICE_ID_DAWN` | ❌ Optional | Custom voice ID for Dawn |
| `DATA_PATH` | ❌ Optional | Override dataset path |

---

## Deploy to Vercel

Both Next.js apps are pre-configured for Vercel deployment:
```bash
cd keystone_site
vercel --prod

cd forrest_case_study
vercel --prod
```

No environment variables needed — both apps use pre-generated static data.

---

## Built With
- [Anthropic Claude](https://anthropic.com) — claude-sonnet-4-6
- [Streamlit](https://streamlit.io) — owner-approval UIs
- [Next.js 14](https://nextjs.org) — demo websites
- [Tailwind CSS](https://tailwindcss.com) — styling
- [pandas](https://pandas.pydata.org) — dataset processing
- [Rich](https://rich.readthedocs.io) — terminal output

---

*© 2026 Forrest Analytics Group LLC — AI for service businesses*
*[forrestanalyticsgroup.com](https://forrestanalyticsgroup.com)*
