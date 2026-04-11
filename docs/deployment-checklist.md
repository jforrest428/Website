# Deployment Checklist
**Generated:** April 10, 2026 | Audit implementation commit: `c874916`

---

## Files Modified

| File | What Changed |
|------|-------------|
| `small-business/index.html` | OG tags, canonical, meta desc, hero copy, Why Us headline, headshot, CTA rename, case study copy, pricing grid fix, FAQ section, footer nav, schema markup |
| `style.css` | `.pricing-grid-2col` class, headshot styles, FAQ section styles, mobile overflow fix |
| `small-business/missed-call-sms/index.html` | "Claude Writes the Text" → "AI Writes the Text" (×2); email; Book a Call |
| `small-business/estimate-followup/index.html` | "Claude writes" → passive AI voice (×4); email; Book a Call |
| `index.html` | Email only |
| `research/index.html` | Email (×2) |
| `small-business/ai-website-chatbot/index.html` | Email; Book a Call |
| `small-business/customer-reengagement/index.html` | Email; Book a Call |
| `small-business/review-reputation-manager/index.html` | Email; Book a Call |
| `small-business/owners-daily-briefing/index.html` | Email; Book a Call |
| `small-business/ai-voice-receptionist/index.html` | Email; Book a Call |
| `small-business/keystone-plumbing/index.html` | Email only (Book a Call was already correct on this page) |

---

## Pre-Deployment Steps

### 1. Set up professional email (before deploying)
The code now references `josh@forrestanalytics.com`. This email must exist before users see it.

**Option A — Google Workspace (recommended):** $6/mo
1. Go to workspace.google.com
2. Add forrestanalyticsgroup.com as your domain
3. Create `josh@forrestanalytics.com`
4. Verify domain ownership (add a TXT record in your DNS)

**Option B — Zoho Mail (free tier):** zoho.com/mail
1. Create a free account
2. Add your domain
3. Create `josh@forrestanalytics.com`
4. Add MX records to your DNS

> ⚠️ Do NOT skip this step. If users click `mailto:josh@forrestanalytics.com` before the email exists, it will bounce.

### 2. Create OG image (recommended before deploying)
The OG tags reference `/assets/og-small-business.png`. This image doesn't exist yet — without it, the OG tags will load but social previews won't show an image.

**Create a 1200×630px image:**
- Use Canva or Figma
- Use your dark navy background with gold text
- Text: "AI Tools for Local Service Businesses" + your logo
- Save as `assets/og-small-business.png`
- Add it to the repo and commit

Until this file is created, the OG tags will still work (title and description will show on social), just without an image thumbnail. Low urgency but worth doing.

### 3. Verify local changes look correct (optional)
Open the HTML files in a browser locally before pushing:
```bash
# Windows — open in default browser
start small-business/index.html
```
Check:
- [ ] Hero sub-headline says "Stop losing jobs to missed calls, dead estimates..."
- [ ] "Book a Call" nav links to `#sb-contact` (not `/research/#contact`)
- [ ] Footer email shows `josh@forrestanalytics.com`
- [ ] Josh's headshot appears in the "Why Work With Us" section
- [ ] FAQ section appears above the contact form
- [ ] Pricing grid collapses to single column (resize browser to 375px to verify)

---

## Deployment Steps

This site deploys via **GitHub Pages** (confirmed by `CNAME` file and domain setup).

### Push to deploy:
```bash
git push origin main
```

GitHub Pages automatically redeploys on every push to `main`. No build step required — it's plain HTML/CSS/JS.

### Expected deploy time:
1–3 minutes for GitHub Pages to process and propagate.

---

## Verify Changes Are Live

After pushing, wait 2–3 minutes then check:

### Quick checks (browser):
1. **https://forrestanalyticsgroup.com/small-business/**
   - [ ] Hero sub-headline is updated
   - [ ] "Book a Call" in nav goes to the Free Audit form (not the research contact)
   - [ ] Footer email shows `josh@forrestanalytics.com`
   - [ ] Headshot photo visible in "Why Work With Us" section
   - [ ] FAQ section visible between Pricing and the contact form
   - [ ] Resize to 375px wide — pricing section should NOT have a horizontal scrollbar

2. **https://forrestanalyticsgroup.com/small-business/missed-call-sms/**
   - [ ] Step 2 says "AI Writes the Text" (not "Claude Writes the Text")

3. **https://forrestanalyticsgroup.com/small-business/estimate-followup/**
   - [ ] Body copy no longer references "Claude" by name

### OG/meta tag check:
Paste the URL into https://www.opengraph.xyz to verify OG tags are reading correctly.

### Schema markup check:
Paste the URL into https://validator.schema.org to verify LocalBusiness + FAQPage schema.

### Email check:
Send a test email to `josh@forrestanalytics.com` and confirm it arrives (only relevant after Step 1 above is completed).

---

## Rollback Instructions

If something breaks after deploying:

```bash
# Roll back to the save-point commit (pre-changes)
git revert HEAD
git push origin main
```

Or to go all the way back to before the audit work:
```bash
# Find the commit hash
git log --oneline | head -5

# Hard reset to save point (the commit labeled "Save point before website audit improvements")
git reset --hard f2c1567
git push origin main --force
```

> ⚠️ `--force` push is destructive. Only use if you need to fully undo everything. The revert approach above is safer.

---

## What Was NOT Implemented (Requires External Setup)

These items from the audit require action outside the codebase:

| Item | What's Needed | Effort |
|------|--------------|--------|
| **Calendly self-scheduling** | Sign up at calendly.com, create a 15-min booking type, then update the "Book a Call" nav link from `#sb-contact` to your Calendly URL | Half day |
| **Real client testimonials** | Gather quotes from beta users or audit call participants, then add a testimonials section (suggest adding above the FAQ section) | Ongoing |
| **Phone number** | Add a Google Voice number or business line, then add it to the footer and contact section in the HTML | Quick once you have the number |
| **OG image** | Create `assets/og-small-business.png` (1200×630px) and commit | 30 min |
| **Satisfaction/cancellation guarantee copy** | Write it, add to pricing section or FAQ | Quick |

---

## Commits Reference

```
c874916  Apply website audit improvements — 12 files, 15 changes  ← all changes
f2c1567  Save point before website audit improvements               ← rollback target
df83f6d  Write chatbot leads to lead-crm-output/leads.csv CRM tracker
```
