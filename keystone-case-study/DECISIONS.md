# DECISIONS.md — Keystone Plumbing AI Case Study

Significant architectural and product decisions made during the build.
Each entry documents what was chosen, why, and where it matters.

---

## 1. Pre-generated demo data vs. live API calls in the browser

**Decision:** Pre-generated static JSON embedded in the Next.js apps.

**Why:** The Keystone site is a demo/portfolio piece. Live Claude API calls from the browser would require a proxy server (CORS, API key exposure), add latency visible to the prospect, and cost money on every page view. Pre-generating the best 4–10 outputs per product and embedding them as TypeScript constants achieves the same "wow" effect at zero cost and zero latency. The Python backends can always be run live for a hands-on walkthrough.

---

## 2. Two separate Next.js apps vs. monorepo

**Decision:** Two separate `create-next-app` projects (`keystone_site/`, `forrest_case_study/`).

**Why:** The prompt specified distinct directories. More importantly, these serve different audiences and deployment contexts: `keystone_site/` is a demo plumbing company site (standalone), while `forrest_case_study/` is a page to be dropped into `forrestintelligence.com`. Keeping them separate means each can be deployed independently to Vercel or any static host with no coupling.

---

## 3. Python script path resolution (sys.path injection)

**Decision:** Each product script uses `sys.path.insert(0, ROOT)` where `ROOT = Path(__file__).parent.parent.parent`.

**Why:** Avoids requiring the user to install the shared package or configure PYTHONPATH manually. Every script is runnable with `python products/XX/script.py` from any directory. The trade-off (non-standard imports) is acceptable for a demo project; a production deployment would use a proper package structure with `pyproject.toml`.

---

## 4. Water heater segment threshold (5 years → 12 months)

**Decision:** The water heater aging segment uses a 12-month threshold instead of the spec's 5 years.

**Why:** The synthetic dataset only spans April 2024 – April 2026 (2 years). No water heater replacements in the dataset are 5+ years old. Using a 12-month threshold produces a meaningful segment from the available data while the UI and messaging still reference the "aging water heater" narrative correctly. In production against a real CRM with 8+ years of history, the threshold reverts to 60 months and no code change is needed.

---

## 5. Caching strategy: two-layer cache

**Decision:** Disk-based SHA-256 cache in `.cache/` (Claude API responses) + file-based output cache in `products/XX/output/` (final formatted outputs).

**Why:** The Claude cache prevents duplicate API costs when demoing or testing. The output cache prevents re-running the full pipeline if an output already exists (e.g., `--date 2026-04-07` only calls Claude once). The two layers are independent: clearing `.cache/` forces a fresh API call; clearing `output/` forces a fresh pipeline run but hits the API cache.

---

## 6. Streamlit for approval UIs, not FastAPI + React

**Decision:** Streamlit for owner-approval UIs (Review Reply, Re-Engagement, Briefing viewer).

**Why:** The spec calls for Streamlit explicitly for these. It's the right tool: these are internal tools, not public-facing UX. Streamlit lets us ship a functional, screen-recordable demo in a fraction of the time a full React app would take. The Next.js modals serve the public-facing demo role.

---

## 7. Temperature settings

- Briefings and review replies: **0.3** — precise, consistent, stays on brand
- Re-engagement outreach: **0.7** — needs to feel human and personalized, slight variation is desirable
- Voice receptionist: **0.3** — tool-use accuracy is more important than creative variation

---

## 8. Voice receptionist: tool-use implementation approach

**Decision:** Implement tool handlers against the live dataset but as "fake" integrations (no real calendar, no real SMS).

**Why:** Real telephony (Twilio), real SMS, and real calendar integrations are out of scope and would require live credentials. The tool handlers instead log to `call_log.jsonl`, return realistic values (actual tech names, real availability windows derived from the jobs sheet), and print confirmations to the console. This produces a demo that is functionally indistinguishable from a live integration during a screen recording.

---

## 9. Emergency detection: keyword-based vs. model-based

**Decision:** Let the Claude model handle emergency classification — no keyword pre-filter.

**Why:** The `RECEPTIONIST_SYSTEM_PROMPT` defines the emergency categories and instructs the model to call `escalate_to_oncall` when they're detected. This is more robust than a pre-filter (handles paraphrasing, context) and keeps the logic in one place. The model is very reliable at this classification.

---

## 10. Dataset note: `patterns.py` `include_groups=False`

**Decision:** Added `include_groups=False` to the `groupby().apply()` call in `patterns.py`.

**Why:** Pandas 2.x raises a `FutureWarning` when the grouping column is included in the `apply` result. Explicitly passing `include_groups=False` silences the warning and future-proofs the code against Pandas 3.x where this behavior will be the default.

---

## 11. Keystone site: no dark mode

**Decision:** Single light-mode theme only.

**Why:** The site is a demo tool, not a consumer app. Navy + orange on white is a deliberate brand choice. Adding dark mode doubles CSS complexity with no demo value.

---

## 12. Case study page: server component (no "use client")

**Decision:** The Forrest Intelligence case study page is a pure server component (static render).

**Why:** It contains no interactivity. No useState, no event handlers. This makes it statically renderable, perfectly SEO-optimized, and trivially droppable into any Next.js app as a route. The `"use client"` directive is intentionally absent.
