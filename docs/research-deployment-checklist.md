# Research Page Deployment Checklist
**Audit date:** April 10, 2026  
**Deploy to:** GitHub Pages (auto-deploys on push to `main`)  
**Branch:** `main`

---

## Files Modified

| File | Changes |
|---|---|
| `research/index.html` | Full audit implementation — see change log below |
| `docs/research-page-audit.md` | New file — audit findings and recommendations |
| `docs/research-deployment-checklist.md` | This file |

### research/index.html — Detailed Change Log

| Section | What Changed |
|---|---|
| `<head>` meta title | Rewrote for SEO: "Statistical Consulting for PhD Students & Researchers \| Forrest Intelligence" |
| `<head>` meta description | Rewrote to target researcher search queries; includes key terms: dissertation, PhD, Wharton, M.S. Analytics |
| `<head>` `<style>` block | Added page-specific CSS for 3 new sections: methods belt, testimonials, pricing |
| Hero eyebrow | "Data Analytics & Research Consulting" → "Statistical Consulting for Academic Researchers" |
| Hero H1 | "Statistical Support for Researchers & Organizations" → "I Help Researchers Get Through the Analysis" |
| Hero sub-copy | Rewritten to name PhD students, postdocs, and faculty; removed generic consulting language |
| Hero CTA | "Request a Free 15-Minute Consultation" → "Get a Free 15-Minute Consultation" |
| Hero stats row | "University Engagements" → "Research Institutions"; "PhD Level Methodology Support" → "Dissertation-Level Methodology"; "R · Python · Excel" → "R · SPSS · Python" |
| Affiliations — Wharton card | Added Aramco, T-Mobile, Apple client names; removed "part-time" |
| Affiliations — SJU card | Removed "incoming"; now reads "Instructor of AI for Business; M.S. Business Intelligence & Analytics (Data Science specialization)" |
| **NEW: Methods section** | New section after affiliations — lists 10 statistical methods (SEM, HLM, EFA/CFA, mediation, power analysis, etc.) and 6 software tools |
| Problem card 2 | "messy data / defense date" → "deadline is real and the analysis isn't done" (broader: applies to defenses, manuscripts, grant reports) |
| Problem card 3 | "don't know how to write up results" → "not sure it's telling the right story" (broader: applies to faculty/reviewers/leadership) |
| Services eyebrow | "What We Do" → "How I Help" |
| Services H2 | "Services" → "What You'll Get" |
| Service card 1 — title | "Doctoral Research Design & Methodology Support" → "Dissertation & Thesis Statistics" |
| Service card 1 — description | Rewritten to emphasize committee-readiness and researcher confidence |
| Service card 1 — bullets | Added "Power analysis and sample size planning" |
| Service card 2 — title | "Statistical Analysis & Results Interpretation" → "Statistical Analysis & Results" |
| Service card 2 — for label | Added "Manuscripts & Grant Reports" |
| Service card 2 — bullets | Added explicit method list (regression, ANOVA, SEM, HLM) |
| Service card 3 — title | "Applied Analytics & Decision Support" → "Faculty & Lab Analytics Support" |
| Service card 3 — for label | "Small Organizations & Research Teams" → "Postdocs, Faculty PIs & Research Teams" |
| Service card 3 — description | Rewritten for faculty/postdoc audience; added "Grant-fundable, scope-defined" |
| Service card 3 — bullets | Added "Documented for grant reporting and reimbursement" |
| Services note | Updated to reference pricing section with anchor link |
| Services CTA | "Request a Consultation" → "Get a Free Consultation" |
| **NEW: Testimonials section** | New section (dark navy) after services — 3 anonymized placeholder testimonials covering PhD student, postdoc, and faculty perspectives. **Replace with real quotes before deploying.** |
| Process step 1 | Minor copy edit — added "whether I'm the right fit" |
| Process step 2 | "Scope & Flat-Rate Proposal" → "Written Scope & Flat-Rate Quote" (clearer wording) |
| Process step 4 | Minor edit — added "in front of your committee or anyone else" |
| **NEW: Pricing section** | New section (off-white) after process — 3 tiers: Methodology Session ($150/session), Project Support (from $450/project), Research Retainer (from $800/month). Includes academic discount note. |
| About — headshot alt text | "Forrest Intelligence consultant" → "Josh Forrest, statistical consultant for academic researchers" |
| About — paragraph 1 | Minor edit — added em dash for rhythm |
| About — paragraph 2 | Full rewrite: leads with M.S. credential, current SJU role, Wharton exec ed client names (Aramco, T-Mobile, Apple), Duquesne dissertation work |
| About — paragraph 3 | Minor edit — expanded outcomes list |
| FAQ — item 3 (process) | Updated to include specific methods: SEM, HLM, factor analysis, power analysis |
| **NEW: FAQ — postdocs/faculty** | New item: "Do you work with postdocs, faculty, or research labs?" — covers retainer, grant reimbursement |
| **NEW: FAQ — student budget** | New item: "I'm a grad student on a limited budget. Can I still work with you?" — references Methodology Session and academic discount |
| FAQ — "How long does a project take?" | Added: "If you have a hard deadline, tell me at the start" |
| FAQ — "What do you charge?" | Updated to reference pricing section with anchor link |
| **NEW: FAQ CTA** | Added gold CTA button after FAQ section |
| Contact form label | "Tell us about your project" → "Tell me about your project" |
| Contact form dropdown | Added "Postdoc / Early-Career Researcher" and "Faculty / Principal Investigator" options; renamed "Small Business / Organization" → "Research Team / Lab" |
| Form success message | "We'll be in touch" → "I'll be in touch" |
| Footer nav | Added "Pricing" link |

---

## Steps to Deploy

1. **Review testimonials** — the 3 testimonials in the `#testimonials` section are placeholder text. Before deploying to production, replace each with a real quote from an actual client. Keep them anonymized (Role, Field — no names). If you don't have real quotes yet, you can deploy the placeholders temporarily but plan to replace them within 30 days.

2. **Verify pricing** — confirm that $150/session, $450/project minimum, and $800/month retainer minimum match your actual pricing. These numbers are in the `#pricing` section and in the FAQ answer for "I'm a grad student on a limited budget."

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```
   GitHub Pages auto-deploys from `main`. Deployment typically takes 1–3 minutes.

4. **Verify live site** — navigate to `forrestintelligence.com/research/` and check:
   - [ ] Page title in browser tab reads "Statistical Consulting for PhD Students & Researchers | Forrest Intelligence"
   - [ ] Hero headline reads "I Help Researchers Get Through the Analysis"
   - [ ] Wharton card mentions Aramco, T-Mobile, and Apple
   - [ ] SJU card reads "Instructor of AI for Business; M.S. Business Intelligence & Analytics"
   - [ ] "What I Work With" methods section is visible after affiliations
   - [ ] Three testimonial cards are visible (dark navy section)
   - [ ] Pricing section shows three tiers with dollar amounts
   - [ ] FAQ has 7 items (not 5)
   - [ ] Footer nav includes "Pricing" link
   - [ ] Contact form dropdown includes "Postdoc / Early-Career Researcher" and "Faculty / Principal Investigator"

5. **Test on mobile** — visit on an iPhone/Android or use browser dev tools at 375px:
   - [ ] Hero text fits without overflow
   - [ ] Methods tags wrap cleanly
   - [ ] Pricing cards stack to single column
   - [ ] Testimonial cards stack to single column
   - [ ] CTA buttons are thumb-friendly

6. **Test the form** — submit a test inquiry and verify:
   - [ ] Form submits to Formspree without error
   - [ ] Success message appears: "Message Received / I'll be in touch within one business day"
   - [ ] You receive the email at josh@forrestintelligence.com

---

## How to Verify Changes

```bash
# Check current git status
git status

# See what changed vs the save point
git diff HEAD~1 research/index.html

# View commit log
git log --oneline -5
```

---

## Rollback Instructions

The pre-audit state was committed with message:  
`"Save point before research page audit improvements"`

To roll back:
```bash
# Find the save point commit hash
git log --oneline | grep "Save point before research page audit"

# Roll back research/index.html only (keeps other changes)
git checkout <commit-hash> -- research/index.html
git commit -m "Rollback research/index.html to pre-audit state"
git push origin main
```

To roll back everything (nuclear option):
```bash
git revert HEAD --no-commit
git commit -m "Revert: roll back research page audit changes"
git push origin main
```

---

## Post-Deploy Priorities

1. **Replace placeholder testimonials** with real quotes — this is the highest-leverage trust signal missing from the page
2. **Add Calendly or scheduling link** — "Book a Call" currently links to the contact form; a direct calendar link would remove friction for faculty and postdocs who prefer self-scheduling
3. **Confirm pricing accuracy** — the numbers are placeholders based on market rates; update to match your actual rates before driving paid traffic
4. **Consider adding a blog/resources section** — long-term SEO for queries like "how to choose a statistical test for dissertation" would drive consistent organic traffic from the exact audience you're targeting
