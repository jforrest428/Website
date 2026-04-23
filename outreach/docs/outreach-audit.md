# Outreach System Audit — Forrest Intelligence
**Date:** April 10, 2026  
**System:** PhD researcher / professor cold outreach for analytics consulting leads  
**Files audited:** `outreach.py`, `Director Outreach Template.md`, `leads_template.csv`, `.env.example`, `requirements.txt`

---

## Executive Summary — Top 5 Changes and Expected Impact

| # | Change | Expected Impact |
|---|--------|----------------|
| 1 | **University diversity logic** (hard cap 2/institution, 8-institution minimum, 3-day cooldown) | Eliminates spam-pattern detection; if 5 professors at the same school compare notes, they don't all share the same email on the same day |
| 2 | **Rewrote all email templates** (no AI tells, contractions, varied lengths 60-100w, no bullets) | Passes the "real person wrote this" test; academic recipients are the best spam-detectors alive |
| 3 | **Subject line rotation** (5+ patterns, always lowercase, specific to their work) | First impression; "Data Analytics Support — Penn State" vs. "quick question about your health disparities research" |
| 4 | **Added 3rd follow-up + restructured timing** (Day 4, Day 8, Day 14 graceful close) | 3-touch sequence with proper spacing; most replies come on FU1 or FU2 |
| 5 | **Random 30-90s send delays + `research_focus`/`recent_work` fields** | Delays prevent domain-level rate-limiting; personalization fields allow referencing actual work instead of just "your research" |

---

## Current State (v1 — Before This Audit)

### Architecture
- Single Python script (`outreach.py`) with SQLite backend
- SMTP send via Gmail (`jf10747454@sju.edu` — SJU address, not business domain)
- Three static template functions: `template_initial`, `template_follow_up_1`, `template_follow_up_2`
- CLI with `--import-leads`, `--send`, `--dry-run`, `--mark-replied`, `--status`
- Leads schema: `id, name, organization, email, status, initial_sent_at, follow_up_1_at, follow_up_2_at, created_at`

### Lead Selection (v1)
```python
rows = conn.execute(
    "SELECT id, name, organization, email FROM leads WHERE status = 'pending' LIMIT ?",
    (DAILY_LIMIT,)
).fetchall()
```
No diversity logic. Top 20 rows in creation order. If you imported 50 Penn State leads, you'd send 20 Penn State emails in one day.

### Follow-Up Schedule (v1)
- FU1: Day 3 (`FOLLOW_UP_1_DAYS=3`)
- FU2: Day 7 (`FOLLOW_UP_2_DAYS=7`)
- No FU3

### Templates (v1)
**Initial email subject:** `"Data Analytics Support — {organization}"`  
**Initial email body (verbatim):**
```
Hi {name},

I came across {organization} and wanted to reach out. I run Forrest Intelligence,
a boutique analytics consulting firm that helps graduate researchers and organizations
with statistical analysis, survey design, and applied data work.

If you're working on research that involves data analysis — or have a project where
cleaner data or clearer results would make a difference — I'd love to learn more.
I offer a free 15-minute call to see if there's a fit.

Would you be open to a quick conversation?

Best,
Joshua Forrest
Forrest Intelligence
forrestintelligence.com
```

**FU1 subject:** `"Re: Data Analytics Support — {organization}"`  
**FU2 subject:** `"Re: Data Analytics Support — {organization}"`

---

## Problems Found

### 1. AI Writing Tells in Templates
Every item on the "AI giveaway" checklist was present in v1:

| Tell | Where |
|------|-------|
| Em dash (—) | Initial body: "...data analysis — or have a project..." |
| "I came across..." | Initial body line 1 |
| No contractions | "I run", "I offer", "Would you be open" — 0 contractions in body |
| Overly formal sign-off | "Best, Joshua Forrest, Forrest Intelligence, forrestintelligence.com" — 4 lines for a cold email |
| "I'd love to learn more" | Second paragraph |
| Vague reference to org | "I came across {organization}" — not their research, not a specific paper |
| Generic close | "Would you be open to a quick conversation?" |
| Every email same length | Static template = every recipient gets identical word count |

### 2. Subject Line Is a Spam Flag
`"Data Analytics Support — Penn State"` — this reads like a marketing email subject. It names the service before earning any interest. A real peer-to-peer email from a researcher would say something like "question about your health disparities work."

FU1 and FU2 subjects are identical: `"Re: Data Analytics Support — {organization}"` — since the thread is continued, the subject should match what was sent in the initial. These were hardcoded independently, so they'd never match.

### 3. No University Diversity Logic
The query `SELECT ... WHERE status = 'pending' LIMIT 20` pulls strictly in insertion order. If your CSV lists 10 leads from the same university consecutively, that school gets 10 emails on the same day. This is the single highest-risk failure mode in the system.

### 4. No Send Delays
All emails send back-to-back in a tight loop. Gmail may throttle, and hitting 5 `.edu` addresses at the same university within 60 seconds will trigger their inbound spam filters.

### 5. Only 2 Follow-Ups, Tight Spacing
Day 3 / Day 7 is too compressed. Day 3 is barely time for someone to see and ignore an email. The third touch (Day 14 graceful close) is where a lot of "actually, let's talk" replies come from — it's missing.

### 6. No Personalization Fields
The DB schema had no `research_focus` or `recent_work` columns. The template could only use `name` and `organization`. "I came across {organization}" is as specific as it got — not a paper, not a grant, not a topic area.

### 7. No Opt-Out Language
No way for a recipient to say "please don't email me." Academics talk. One polite "please remove me" is much better than them flagging the email to their IT department.

### 8. Sending from SJU Address
The `.env.example` shows `GMAIL_ADDRESS=jf10747454@sju.edu`. Sending from a university student address introduces its own deliverability issues (recipients may dismiss it as a grad student fishing for clients) and doesn't build your professional brand. Should be `josh@forrestintelligence.com`.

### 9. Director Template (`.md` file) Has Same Problems
The manually-used director outreach template has all the same issues:
- Bullet points in the body
- "I'm reaching out because I believe there's an opportunity..."
- "My name is Josh Forrest" in the first paragraph
- 10-line signature block
- "I've channeled that expertise" — formal and slightly buzzwordy
This template wasn't changed by the script rewrite since it's manually used — see Remaining Recommendations.

---

## Changes Made

### 1. University Diversity — `select_leads_for_batch()`
**Before:** `SELECT ... LIMIT ?` with no diversity constraints.  
**After:** Two-pass selection:
- Pass 1: Fill batch from institutions NOT contacted in the last `INSTITUTION_COOLDOWN_DAYS` (default 3)
- Pass 2: Fill remaining slots from any institution, still respecting `MAX_PER_INSTITUTION=2` cap
- Prints batch composition (institutions + counts) before sending
- Warns if fewer than `MIN_INSTITUTIONS=8` unique institutions are in the batch

### 2. Email Templates — Complete Rewrite
All 6 templates (initial + 3 variants, 3 follow-ups) were rewritten from scratch.

**New rules enforced in code:**
- No em dashes anywhere
- No bullets
- Contractions throughout (I'm, I've, you'd, etc.)
- No "I came across," "I hope this finds you well," "leverage," "synergize," "cutting-edge"
- No intro sentence starting with name
- Opt-out line in 2 of 3 initial variants
- 3 variants with different word counts (~60w, ~80w, ~100w) selected deterministically by `lead_id`

**Subject line rotation:** 5+ patterns, always lowercase, specific where data is available:
- `"quick question about your {research_focus} research"` (if research_focus present)
- `"question about your {research_focus} work"` (if research_focus present)
- `"quick question re: {recent_work}"` (if recent_work present)
- `"saw your work on {recent_work}"` (if recent_work present)
- `"quick question"` (fallback)
- `"question from a fellow researcher"` (fallback)
- `"question about your research at {org_short}"` (fallback)

### 3. Follow-Up Sequence Restructured
**Before:** Day 3 bump, Day 7 angle  
**After:**
- FU1 Day 4: 15-20 word bump, 3 variants
- FU2 Day 8: ~40-50 words, references research_focus if available, 2 variants
- FU3 Day 14: ~25-30 word graceful close, 3 variants, marks lead `closed`

FU subjects now use `f"re: {initial_subject}"` so they thread correctly with the initial email.

### 4. New Database Columns
Added via `_migrate_db()` (safe for existing databases):
- `research_focus TEXT` — researcher's field/topic area
- `recent_work TEXT` — specific paper, grant, project to reference
- `initial_subject TEXT` — stored when initial email is sent, used by follow-ups for threading
- `follow_up_3_at TEXT` — timestamp for new Day-14 touch

### 5. Send Delays
`_delay()` function sleeps `random.randint(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)` seconds (default 30-90s) between each send. No delay in dry-run mode.

### 6. Added `--mark-unsubscribed` Command
Status `'unsubscribed'` already appeared in `show_status()` but there was no CLI command to set it. Added.

### 7. Updated `leads_template.csv` and `.env.example`
- CSV template now includes `research_focus` and `recent_work` headers
- `.env.example` documents all new variables with inline explanations
- `.env.example` notes that `josh@forrestintelligence.com` should be the sender

### 8. Dry-Run Shows Full Email Content
v1 dry-run only printed the recipient name and email. v2 prints subject + full body for every email in the batch.

---

## Sample Emails — v2 System

### Email 1: Dr. Sarah Chen, University of Michigan (variant 0, ~60 words)
**Subject:** `quick question about your health disparities research`
```
Hi Sarah,

Your work on Racial inequities in maternal mortality outcomes caught my attention, 
particularly the health disparities angle. I run Forrest Intelligence, a small 
consulting firm that does stats and methodology work for researchers. The clients I 
work with are usually faculty or grad students who need help getting through the 
analytical side of applied projects.

Would you have 15 minutes? If this isn't relevant to what you're working on, no worries.

Josh
```

### Email 2: Dr. Robert Kim, Duke University (variant 1, ~80 words)
**Subject:** `saw your work on Adaptive trial design for rare pediatric diseases`
```
Hi Robert,

I read your Adaptive trial design for rare pediatric diseases and had a question about 
the clinical trial design side.

I do analytics and methodology consulting through Forrest Intelligence. Mostly I 
work with researchers on stats, survey design, and data analysis when projects need it.

Curious whether there's any overlap with what you're running in clinical trial design 
right now.

Any chance you'd have 15 minutes to connect? Nothing heavy on my end, just curious if 
there's a fit. If you'd rather not hear from me again, just say the word.

Josh Forrest
```

### Email 3: Dr. Linda Johansson, Boston University (variant 2, ~100 words)
**Subject:** `question about your organizational behavior work`
```
Hi Linda,

I've been following the organizational behavior research at Boston University.

I'm a data analyst who does research methods consulting through Forrest Intelligence. 
I work with faculty and doctoral students on applied projects, mostly on the quantitative 
side (stats, methodology, data analysis).

Wondering if there's any overlap with what you're running in organizational behavior 
right now.

I'd be happy to do a quick call if any of this resonates with what you're working on. 
15 minutes is plenty. If it's not a fit, I'd honestly rather know that early.

Josh Forrest
forrestintelligence.com
```

### Email 4: Dr. Marcus Webb, Ohio State University (variant 1, no research_focus match in FU2)
**FU2 Subject:** `re: question about your behavioral economics work`
```
Hi Marcus,

I've been thinking more about the behavioral economics angle since I last wrote. If 
stats or methodology support is ever something on your radar, I'm easy to reach.

Josh Forrest
forrestintelligence.com
```

---

## University Distribution Example — Sample Batch of 20

Using the test dataset (`test_leads.csv`), a batch of 20 covers all 20 institutions (1 per school since there are 20 unique institutions for 20 leads):

| # | Institution | Department/Field | Lead |
|---|------------|-----------------|------|
| 1 | University of Michigan | Health disparities | Dr. Sarah Chen |
| 2 | Ohio State University | Behavioral economics | Dr. Marcus Webb |
| 3 | University of Washington | ML fairness | Dr. Priya Nair |
| 4 | Rutgers University | Public health surveillance | Dr. James Okonkwo |
| 5 | Georgetown University | Social network analysis | Dr. Elena Vasquez |
| 6 | Duke University | Clinical trial design | Dr. Robert Kim |
| 7 | Penn State University | Educational assessment | Dr. Amanda Pierce |
| 8 | Emory University | Cardiovascular epidemiology | Dr. Thomas Osei |
| 9 | Boston University | Organizational behavior | Dr. Linda Johansson |
| 10 | UT Austin | Environmental policy | Dr. Carlos Mendez |
| 11 | Northwestern University | Computational social science | Dr. Fatima Al-Rashid |
| 12 | Stanford University | Survey methodology | Dr. David Park |
| 13 | UC San Diego | Bioinformatics | Dr. Rebecca Torres |
| 14 | Yale University | Criminology | Dr. Michael Adeyemi |
| 15 | Temple University | Social work research | Dr. Susan Whitfield |
| 16 | Notre Dame | Political science | Dr. Kevin O'Brien |
| 17 | Johns Hopkins University | Injury epidemiology | Dr. Aisha Patel |
| 18 | Columbia University | Housing economics | Dr. Nathan Goldberg |
| 19 | Howard University | Health psychology | Dr. Monica Williams |
| 20 | Vanderbilt University | Predictive analytics | Dr. Patrick Shen |

**In a real-world scenario with multiple leads from some institutions,** the diversity logic would select at most 2 from any school, prioritize schools not contacted in 3 days, and warn if fewer than 8 unique institutions appear.

---

## Follow-Up Sequence Example — Dr. Sarah Chen, University of Michigan

**Initial (Day 0):**  
Subject: `quick question about your health disparities research`  
~60 words. References maternal mortality paper. Ends with "no worries."

**FU1 (Day 4):**  
Subject: `re: quick question about your health disparities research`  
```
Hi Sarah,

Just bumping this up in case it got buried.

Josh
```

**FU2 (Day 8):**  
Subject: `re: quick question about your health disparities research`  
```
Hi Sarah,

I've been thinking more about the health disparities angle since I last wrote. If stats 
or methodology support is ever something on your radar, I'm easy to reach.

Josh Forrest
forrestintelligence.com
```

**FU3 (Day 14):**  
Subject: `re: quick question about your health disparities research`  
```
Hi Sarah,

I'll leave it here. If the timing ever shifts, you can find me at forrestintelligence.com.

Josh
```

---

## Remaining Recommendations (Manual / Can't Automate)

### 1. Switch Sending Domain to `josh@forrestintelligence.com`
Update `.env` with your business Gmail credentials. The SJU address works but looks like a student freelancing, not a professional firm. Set up a Google Workspace account for the domain if you haven't already.

### 2. Populate `research_focus` and `recent_work` for Every Lead
The system has the fields. You need to fill them. Even one good specific reference ("your NIH R01 on maternal mortality" vs. "your research") meaningfully changes response rates. Use Google Scholar, ResearchGate, or the lab's website. 30 seconds per lead.

### 3. Rewrite the Director Template (`.md` file)
The `Director Outreach Template.md` is used manually for program directors and department chairs. It has the same AI tells as v1 (bullets, formal intro, 10-line signature). Rewrite it using the same principles: no bullets, contractions, 80-120 words max, specific reference to the program, one ask.

### 4. Schedule the Script to Run Tuesday-Thursday at 9 AM
Research shows Tuesday-Thursday 8-10 AM gets the highest open rates for academic email. Use Windows Task Scheduler or a cron job. The current script runs on-demand — set it to run automatically at the right time.  
Command: `python outreach.py --send`

### 5. Set Up Reply Monitoring
When a lead replies, mark them with `--mark-replied` immediately so they don't get follow-ups. Right now this is manual. Consider piping Gmail API or a webhook to auto-mark replied leads.

### 6. Add SPF/DKIM/DMARC Records for Your Domain
If sending from `josh@forrestintelligence.com`, verify your domain's email authentication records are set up. Missing SPF/DKIM causes deliverability drops especially to `.edu` domains. Check with MXToolbox.

### 7. Test with 5-Lead Batch First
Before your first real `--send` run, do a 5-lead test with people you know at different institutions. Verify the emails landed in inbox (not spam), look right in both mobile and desktop clients, and the threading works correctly on follow-ups.
