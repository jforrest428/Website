# DEMO.md — 5-Minute Walkthrough Script
**For recording a screen-capture demo video. Total runtime: ~5 min.**

---

## Setup (before you hit record)
1. Open four terminals, all at `keystone-case-study/`
2. Have VS Code open with this repo
3. Increase terminal font size to 18pt
4. Set terminal background to navy (`#102a43`)
5. Activate a screen recorder (Loom, OBS, or QuickTime)

---

## Segment 1: The Problem (0:00 – 0:45)
*Show the Forrest Analytics case study page in the browser*

**Narration:**
> "Keystone Plumbing & Drain — $2.1M in annual revenue, 8 licensed technicians, 850 customers.
> They're a real business with a real problem. 29% of their calls go unanswered. 42% of their customers
> haven't heard from them in over a year. Their average review response time is measured in days, not hours.
> We built four AI products on top of their real operational data to fix each one. Let me show you."

*Action: Scroll slowly down the case study page from hero to pain-point stats.*

---

## Segment 2: Daily Briefing (0:45 – 1:30)
*Terminal 1 active*

**Narration:**
> "Every morning at 6am, the owner gets this text."

**Action:**
```bash
cd keystone-case-study
python products/01_daily_briefing/generate_briefing.py --date 2026-04-07
```

*Wait for the Rich output to show the JSON context and the SMS panel.*

> "That's Claude reading yesterday's revenue, today's schedule, 126 overdue invoices,
> and one unanswered negative review — and turning it into a text message in under 3 seconds.
> No dashboard. No login. The owner opens their phone and knows what matters."

*Switch to Streamlit viewer:*
```bash
streamlit run products/01_daily_briefing/app.py
```
*Show the iMessage-style phone UI with 10 days of bubbles.*

---

## Segment 3: Review Reply Manager (1:30 – 2:30)
*Terminal 2 active*

**Narration:**
> "Keystone has 420 reviews. 55% of the negative ones go unanswered. This is what happens when you don't."

**Action:**
```bash
python products/02_review_reply/draft_replies.py --limit 10
```

*Show the Rich table of drafted replies.*

> "Now let me show the owner's side."
```bash
streamlit run products/02_review_reply/app.py
```

*In browser: click through 2-3 reviews. Show a 1-star review and its drafted reply. Click Approve.*

> "One tap. The owner stays in control. And here — the pattern analyzer."

*Switch to Pattern Analysis tab. Point out David Chen with 3 negative mentions.*

> "Three negative reviews in 90 days referencing the same tech. The system flagged it.
> The owner can have that coaching conversation before it becomes a fourth."

---

## Segment 4: Voice Receptionist (2:30 – 3:45)
*Terminal 3 active*

**Narration:**
> "This is the one. 29% of calls go unanswered. What does that actually cost?"

*Action: show call revenue chart from the case study page — $621K in missed-call revenue risk.*

> "Meet Dawn."
```bash
python products/04_voice_receptionist/scripted_demo.py --scenario 1
```

*Wait for Scenario 1 to play out — burst pipe emergency at 11:30pm.*

> "James called at 11:30pm. Dawn answered on the first ring, identified the emergency,
> and dispatched Mike Sullivan in under 60 seconds. James gets a text with Mike's ETA."

*Then run Scenario 2:*
```bash
python products/04_voice_receptionist/scripted_demo.py --scenario 2
```

> "Patricia called about a dead water heater. Dawn offered three slots, Patricia picked one,
> and the booking — with the tech's name, the time, and a confirmation text — was done
> before Patricia hung up."

*Show the call_log.jsonl with the bookings.*

---

## Segment 5: Re-Engagement Engine (3:45 – 4:30)
*Terminal 4 active / Browser*

```bash
streamlit run products/03_reengagement/app.py
```

**Narration:**
> "42% of Keystone's customers haven't been served in over a year.
> The data is sitting in the CRM, untouched. This is what we do with it."

*Show the KPI row: 221 dormant customers, $25K+ projected recovery.*

> "Five segments. Water heaters aging out, sump pumps before spring flooding season,
> drain cleaning lapsed, maintenance overdue, high-value customers who've gone quiet."

*Click into 'High-Value Dormant' segment. Open a customer.*

> "This is James Whitfield. $4,200 in lifetime spend. No job in 10 months.
> Claude writes him a personal SMS and a personal email referencing his specific service history.
> Not a blast. Not a template. His name, his service, his date."

*Show the SMS and email side by side.*

> "We project 12% of these people book. That's $25K in revenue that was already in the database —
> it just needed someone to go get it."

---

## Segment 6: The Close (4:30 – 5:00)
*Switch to Forrest Analytics case study page, scroll to CTA*

**Narration:**
> "Four products. One dataset. One Claude API.
> This is what I build for service businesses — plumbers, HVAC shops, lawn care companies.
> The economics are straightforward: if your shop misses 5 calls a week and the average job is $600,
> that's $150K a year walking out the door.
>
> I do a free 15-minute call audit — I'll pull your actual missed-call data and we'll know the number
> in the first conversation. No pitch. Just data.
>
> Link is in the description."

*Action: Click the "Book a Free 15-Min Audit" button.*

---

## Post-Production Notes
- Record in 1080p minimum
- Add captions during the briefing and receptionist segments (the text is fast)
- Cut the terminal spinner animations down to 0.5x speed if needed
- Background music: low-key lo-fi, fade out during narration
- End card: your face + logo + forrestanalyticsgroup.com + "Book a free audit"
