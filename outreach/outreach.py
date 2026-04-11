"""
Forrest Analytics Group -- Email Outreach Script (v2)

Commands:
  python outreach.py --import-leads leads.csv     import leads from CSV
  python outreach.py --send                        send pending emails + follow-ups
  python outreach.py --dry-run                     preview without sending (shows full emails)
  python outreach.py --mark-replied email          mark a lead as replied
  python outreach.py --mark-unsubscribed email     mark a lead as opted out
  python outreach.py --status                      show pipeline summary

CSV columns: name, organization, email, research_focus (optional), recent_work (optional)
"""

import imaplib
import sqlite3
import csv
import os
import argparse
import random
import time
from email.mime.text import MIMEText
from email.utils import formatdate
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────────
GMAIL_ADDRESS        = os.getenv("EMAIL_ADDRESS")
GMAIL_APP_PASS       = os.getenv("EMAIL_APP_PASSWORD")
IMAP_HOST            = os.getenv("IMAP_HOST", "imap.zoho.com")
IMAP_PORT            = int(os.getenv("IMAP_PORT", 993))
DRAFTS_FOLDER        = os.getenv("DRAFTS_FOLDER", "Drafts")
FOLLOW_UP_1_DAYS     = int(os.getenv("FOLLOW_UP_1_DAYS", 4))   # Day 4: short bump
FOLLOW_UP_2_DAYS     = int(os.getenv("FOLLOW_UP_2_DAYS", 8))   # Day 8: new angle
FOLLOW_UP_3_DAYS     = int(os.getenv("FOLLOW_UP_3_DAYS", 14))  # Day 14: graceful close
DAILY_LIMIT          = int(os.getenv("DAILY_LIMIT", 20))
EMAIL_DELAY_MIN      = int(os.getenv("EMAIL_DELAY_MIN", 30))   # seconds between sends
EMAIL_DELAY_MAX      = int(os.getenv("EMAIL_DELAY_MAX", 90))   # seconds between sends
# University diversity settings
MAX_PER_INSTITUTION  = 2    # hard cap: leads per institution per daily batch
MIN_INSTITUTIONS     = 8    # target: unique institutions per batch (warns if below)
INSTITUTION_COOLDOWN = int(os.getenv("INSTITUTION_COOLDOWN_DAYS", 3))  # days before same school recurs
DB_PATH = os.path.join(os.path.dirname(__file__), "outreach.db")


# ── Helpers ──────────────────────────────────────────────────────────────────────
def first_name(full_name):
    """Extract usable first name, stripping honorifics (Dr., Prof., etc.)."""
    HONORIFICS = {'dr', 'prof', 'professor', 'mr', 'mrs', 'ms', 'miss'}
    parts = full_name.strip().split()
    if not parts:
        return full_name
    if parts[0].lower().rstrip('.') in HONORIFICS:
        return parts[1] if len(parts) > 1 else full_name
    return parts[0]


def _rng(lead_id, suffix=0):
    """
    Deterministic RNG seeded by lead_id so the same lead always generates
    the same template/subject on every run. suffix distinguishes call sites.
    """
    return random.Random(lead_id * 1000 + suffix)


# ── Subject Lines ────────────────────────────────────────────────────────────────
def pick_subject(lead_id, organization, research_focus="", recent_work=""):
    """
    Pick a subject line. Deterministic per lead (same lead = same subject every run).
    Always lowercase, 3-7 words, specific where possible.
    5+ patterns so consecutive emails in a batch don't look templated.
    No marketing language ("Collaboration Opportunity", "Support for Your Research", etc.)
    """
    rng = _rng(lead_id, suffix=1)
    candidates = []

    if research_focus:
        candidates += [
            f"quick question about your {research_focus} research",
            f"question about your {research_focus} work",
            f"your {research_focus} research, a question",
        ]
    if recent_work:
        candidates += [
            f"quick question re: {recent_work}",
            f"saw your work on {recent_work}",
        ]
    # Generic fallbacks -- always in the pool
    org_short = organization.split()[0].lower()  # "Penn" from "Penn State", etc.
    candidates += [
        "quick question",
        "question from a fellow researcher",
        "question about your work",
    ]
    # Only include the org-specific fallback if org_short is a recognizable word,
    # not a 2-letter acronym ("uc", "ut") that looks like a typo.
    if len(org_short) > 3:
        candidates.append(f"question about your research at {org_short}")
    return rng.choice(candidates)


# ── Research Reference Lines ──────────────────────────────────────────────────────
def _research_ref(lead_id, organization, research_focus, recent_work):
    """
    Build the opening line that references their specific work.
    Varies by available data. Avoids "I came across your research on..." pattern.
    """
    rng = _rng(lead_id, suffix=2)

    if recent_work and research_focus:
        opts = [
            f"Your work on {recent_work} caught my attention, particularly the {research_focus} angle.",
            f"I read your {recent_work} and had a question about the {research_focus} side.",
        ]
    elif recent_work:
        opts = [
            f"I read your {recent_work} and wanted to reach out.",
            f"Your {recent_work} came up in some reading I was doing.",
            f"I've been looking at your work on {recent_work}.",
        ]
    elif research_focus:
        opts = [
            f"I've been following the {research_focus} research at {organization}.",
            f"Your work on {research_focus} at {organization} caught my attention.",
            f"I noticed your {research_focus} work at {organization} and had a question.",
        ]
    else:
        opts = [
            f"I noticed your work at {organization} and wanted to reach out.",
            f"I had a question about the research you're doing at {organization}.",
        ]
    return rng.choice(opts)


def _connection_line(lead_id, research_focus):
    """One-line bridge between the intro and the ask."""
    rng = _rng(lead_id, suffix=3)
    if research_focus:
        opts = [
            f"Given your work in {research_focus}, I figured it was worth asking.",
            f"Curious whether there's any overlap with what you're running in {research_focus} right now.",
            f"Wondering if any of this maps to what you have going on the {research_focus} side.",
        ]
    else:
        opts = [
            "Wondering if there's any overlap with what you're working on.",
            "Curious whether this maps to any projects you have going.",
            "Figured it was worth asking.",
        ]
    return rng.choice(opts)


# ── Email Templates ──────────────────────────────────────────────────────────────
def template_initial(lead_id, name, organization, research_focus="", recent_work=""):
    """
    Pick one of 3 initial email variants. Deterministic per lead_id.
    Word counts: variant 0 ~60w, variant 1 ~80w, variant 2 ~100w.
    Rules enforced:
      - No em dashes
      - No bullets
      - Contractions throughout
      - No "My name is Josh...", no "I hope this email finds you well"
      - No "leverage", "synergize", "cutting-edge", "groundbreaking"
      - No "I'd love to schedule a call to discuss potential synergies"
      - Plain text only
      - Opt-out line in variants 1 and 2
    """
    research_focus = research_focus or ""
    recent_work = recent_work or ""
    fname = first_name(name)
    ref = _research_ref(lead_id, organization, research_focus, recent_work)
    conn_line = _connection_line(lead_id, research_focus)
    subject = pick_subject(lead_id, organization, research_focus, recent_work)
    variant = _rng(lead_id, suffix=0).randint(0, 2)

    if variant == 0:
        # Shortest (~60 words). Direct ask, no opt-out, signed "Josh".
        body = (
            f"Hi {fname},\n\n"
            f"{ref} I run Forrest Analytics Group, a small consulting firm that does stats and methodology work for researchers. "
            f"The clients I work with are usually faculty or grad students who need help getting through the analytical side of applied projects.\n\n"
            f"Would you have 15 minutes? If this isn't relevant to what you're working on, no worries.\n\n"
            f"Josh"
        )

    elif variant == 1:
        # Medium (~80 words). Connection line, opt-out, signed "Josh Forrest".
        body = (
            f"Hi {fname},\n\n"
            f"{ref}\n\n"
            f"I do analytics and methodology consulting through Forrest Analytics Group. "
            f"Mostly I work with researchers on stats, survey design, and data analysis when projects need it.\n\n"
            f"{conn_line}\n\n"
            f"Any chance you'd have 15 minutes to connect? Nothing heavy on my end, just curious if there's a fit. "
            f"If you'd rather not hear from me again, just say the word.\n\n"
            f"Josh Forrest"
        )

    else:
        # Longer (~100 words). More context, URL, opt-out in closing.
        body = (
            f"Hi {fname},\n\n"
            f"{ref}\n\n"
            f"I'm a data analyst who does research methods consulting through Forrest Analytics Group. "
            f"I work with faculty and doctoral students on applied projects, mostly on the quantitative side "
            f"(stats, methodology, data analysis).\n\n"
            f"{conn_line}\n\n"
            f"I'd be happy to do a quick call if any of this resonates with what you're working on. "
            f"15 minutes is plenty. If it's not a fit, I'd honestly rather know that early.\n\n"
            f"Josh Forrest\n"
            f"forrestanalyticsgroup.com"
        )

    return subject, body


def template_follow_up_1(lead_id, name, organization, initial_subject=""):
    """
    Day 4. Very short bump (~15-20 words). Just resurfaces the thread.
    No new pitch, no new info.
    """
    fname = first_name(name)
    subject = f"re: {initial_subject}" if initial_subject else "re: my last note"
    rng = _rng(lead_id, suffix=10)
    variants = [
        f"Hi {fname},\n\nJust bumping this up in case it got buried.\n\nJosh",
        f"Hi {fname},\n\nFloating this back up. Figured it was worth one more try.\n\nJosh",
        f"Hi {fname},\n\nJust checking in on this. Happy to keep it short if you have a few minutes.\n\nJosh",
    ]
    return subject, rng.choice(variants)


def template_follow_up_2(lead_id, name, organization, research_focus="", initial_subject=""):
    """
    Day 8. New angle, ~40-50 words. Small value add or reference to their field.
    Shorter than the initial, longer than FU1.
    """
    fname = first_name(name)
    research_focus = research_focus or ""
    subject = f"re: {initial_subject}" if initial_subject else "re: analytics consulting"
    rng = _rng(lead_id, suffix=11)

    if research_focus:
        angle_opts = [
            f"I've been thinking more about the {research_focus} angle since I last wrote.",
            f"Something related to {research_focus} came up that made me think of your work again.",
        ]
        angle = rng.choice(angle_opts)
    else:
        angle = "One more note on this."

    variants = [
        (
            f"Hi {fname},\n\n"
            f"{angle} If stats or methodology support is ever something on your radar, I'm easy to reach.\n\n"
            f"Josh Forrest\n"
            f"forrestanalyticsgroup.com"
        ),
        (
            f"Hi {fname},\n\n"
            f"{angle} Still happy to connect briefly if the timing works. No pressure.\n\n"
            f"Josh"
        ),
    ]
    return subject, rng.choice(variants)


def template_follow_up_3(lead_id, name, organization, initial_subject=""):
    """
    Day 14. Graceful close (~25-30 words). Last touch, no ask, leaves door open.
    """
    fname = first_name(name)
    subject = f"re: {initial_subject}" if initial_subject else "re: analytics consulting"
    rng = _rng(lead_id, suffix=12)
    variants = [
        f"Hi {fname},\n\nI'll leave it here. If the timing ever shifts, you can find me at forrestanalyticsgroup.com.\n\nJosh",
        f"Hi {fname},\n\nI'll assume the timing isn't right. If it ever is, I'm at forrestanalyticsgroup.com.\n\nJosh",
        f"Hi {fname},\n\nLast note, I promise. If you ever need analytics or methodology help, forrestanalyticsgroup.com.\n\nJosh",
    ]
    return subject, rng.choice(variants)


# ── Database ─────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            organization     TEXT NOT NULL,
            email            TEXT UNIQUE NOT NULL,
            research_focus   TEXT DEFAULT '',
            recent_work      TEXT DEFAULT '',
            status           TEXT DEFAULT 'pending',
            initial_sent_at  TEXT,
            initial_subject  TEXT DEFAULT '',
            follow_up_1_at   TEXT,
            follow_up_2_at   TEXT,
            follow_up_3_at   TEXT,
            created_at       TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    _migrate_db(conn)
    return conn


def _migrate_db(conn):
    """
    Add new v2 columns to existing databases without breaking anything.
    Safe to run on a fresh DB (ALTER TABLE errors are caught and ignored).
    """
    new_cols = [
        ("research_focus",  "TEXT DEFAULT ''"),
        ("recent_work",     "TEXT DEFAULT ''"),
        ("initial_subject", "TEXT DEFAULT ''"),
        ("follow_up_3_at",  "TEXT"),
    ]
    for col, col_def in new_cols:
        try:
            conn.execute(f"ALTER TABLE leads ADD COLUMN {col} {col_def}")
        except sqlite3.OperationalError:
            pass  # column already exists -- normal on v2 databases
    conn.commit()


def import_leads(conn, csv_path):
    """
    Import leads from CSV. Required columns: name, organization, email.
    Optional columns: research_focus, recent_work (for personalization).
    Deduplicates on email (case-insensitive).
    """
    added = skipped = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                conn.execute(
                    """INSERT INTO leads (name, organization, email, research_focus, recent_work)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        row['name'].strip(),
                        row['organization'].strip(),
                        row['email'].strip().lower(),
                        row.get('research_focus', '').strip(),
                        row.get('recent_work', '').strip(),
                    )
                )
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1  # email already in DB
    conn.commit()
    print(f"Imported {added} lead(s). {skipped} already existed.")


# ── Institution Diversity Selection ──────────────────────────────────────────────
def select_leads_for_batch(conn, limit):
    """
    Select pending leads for today's batch with institution diversity enforcement:
      - Hard cap: MAX_PER_INSTITUTION leads per institution per batch
      - Deprioritize institutions contacted within INSTITUTION_COOLDOWN days
      - Warns if fewer than MIN_INSTITUTIONS unique institutions are in the batch
      - Two-pass selection: pass 1 fills from cool institutions, pass 2 fills
        remaining slots from recently-contacted institutions if needed
    Returns list of (id, name, organization, email, research_focus, recent_work).
    """
    all_pending = conn.execute(
        """SELECT id, name, organization, email, research_focus, recent_work
           FROM leads WHERE status = 'pending' ORDER BY created_at"""
    ).fetchall()

    if not all_pending:
        return []

    # Institutions emailed in the last INSTITUTION_COOLDOWN days
    cooldown_cutoff = (datetime.now() - timedelta(days=INSTITUTION_COOLDOWN)).isoformat()
    recently_contacted = {
        row[0] for row in conn.execute(
            "SELECT DISTINCT organization FROM leads WHERE initial_sent_at > ?",
            (cooldown_cutoff,)
        ).fetchall()
    }

    batch = []
    inst_count = {}  # organization -> count already in this batch

    # Pass 1: leads from institutions NOT recently contacted (preferred)
    for lead in all_pending:
        if len(batch) >= limit:
            break
        lead_id, name, org, email, rf, rw = lead
        if org not in recently_contacted and inst_count.get(org, 0) < MAX_PER_INSTITUTION:
            batch.append(lead)
            inst_count[org] = inst_count.get(org, 0) + 1

    # Pass 2: fill remaining slots from recently-contacted institutions if needed
    # (ensures we always fill the batch even when many institutions are on cooldown)
    if len(batch) < limit:
        batch_ids = {lead[0] for lead in batch}
        for lead in all_pending:
            if len(batch) >= limit:
                break
            lead_id, name, org, email, rf, rw = lead
            if lead_id not in batch_ids and inst_count.get(org, 0) < MAX_PER_INSTITUTION:
                batch.append(lead)
                inst_count[org] = inst_count.get(org, 0) + 1

    unique_count = len(inst_count)
    if unique_count < MIN_INSTITUTIONS:
        print(
            f"[WARN] Only {unique_count} unique institutions in batch "
            f"(target: {MIN_INSTITUTIONS}+). Import more leads from diverse institutions."
        )

    return batch


# ── Sending ──────────────────────────────────────────────────────────────────────
def create_draft(to_email, subject, body):
    """
    Save email as a draft in Zoho Mail via IMAP APPEND.
    Drafts appear in your Zoho Drafts folder for review before sending.
    Plain text only -- HTML avoided for .edu deliverability.

    Requires IMAP access enabled in Zoho:
      mail.zoho.com > Settings > Mail Accounts > IMAP Access > Enable
    """
    msg = MIMEText(body, 'plain')
    msg['From']    = GMAIL_ADDRESS
    msg['To']      = to_email
    msg['Subject'] = subject
    msg['Date']    = formatdate(localtime=True)

    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as mail:
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        mail.append(
            DRAFTS_FOLDER,
            '\\Draft',
            imaplib.Time2Internaldate(time.time()),
            msg.as_bytes()
        )


def _delay(dry_run):
    """
    Random delay between emails (30-90s by default).
    Prevents rate-limit blocks and avoids the blast-pattern that triggers
    university spam filters when 15+ emails hit the same domain in minutes.
    No delay in dry-run mode.
    """
    if not dry_run:
        delay = random.randint(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
        time.sleep(delay)


def run_outreach(conn, dry_run=False):
    now = datetime.now()
    sent_today = 0

    # ── Initial emails ────────────────────────────────────────────────────────────
    batch = select_leads_for_batch(conn, DAILY_LIMIT)

    if batch:
        inst_list = {}
        for lead in batch:
            org = lead[2]
            inst_list[org] = inst_list.get(org, 0) + 1
        print(f"\nBatch: {len(batch)} initial email(s) across {len(inst_list)} institution(s)")
        for org, cnt in sorted(inst_list.items()):
            print(f"  {org}: {cnt}")
        print()

    for lead in batch:
        if sent_today >= DAILY_LIMIT:
            break
        lead_id, name, org, email, research_focus, recent_work = lead
        subject, body = template_initial(lead_id, name, org, research_focus, recent_work)

        if dry_run:
            print(f"\n{'='*65}")
            print(f"[DRY RUN] INITIAL  to: {name} <{email}>")
            print(f"Institution: {org}")
            print(f"Subject: {subject}")
            print(f"\n{body}\n")
            sent_today += 1
            continue
        try:
            create_draft(email, subject, body)
            conn.execute(
                "UPDATE leads SET status='sent', initial_sent_at=?, initial_subject=? WHERE id=?",
                (now.isoformat(), subject, lead_id)
            )
            conn.commit()
            print(f"[DRAFT] INITIAL  -> {name} <{email}>  [{org}]")
            sent_today += 1
            _delay(dry_run)
        except Exception as e:
            print(f"[ERROR] {email}: {e}")

    # ── Follow-up 1 ──────────────────────────────────────────────────────────────
    cutoff_1 = (now - timedelta(days=FOLLOW_UP_1_DAYS)).isoformat()
    fu1_rows = conn.execute(
        """SELECT id, name, organization, email, research_focus, initial_subject
           FROM leads
           WHERE status = 'sent'
             AND initial_sent_at < ?
             AND follow_up_1_at IS NULL""",
        (cutoff_1,)
    ).fetchall()

    for lead_id, name, org, email, research_focus, initial_subj in fu1_rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_follow_up_1(lead_id, name, org, initial_subj)
        if dry_run:
            print(f"\n{'='*65}")
            print(f"[DRY RUN] FOLLOW-UP 1  to: {name} <{email}>")
            print(f"Subject: {subject}")
            print(f"\n{body}\n")
            sent_today += 1
            continue
        try:
            create_draft(email, subject, body)
            conn.execute("UPDATE leads SET follow_up_1_at=? WHERE id=?", (now.isoformat(), lead_id))
            conn.commit()
            print(f"[DRAFT] FU-1  -> {name} <{email}>")
            sent_today += 1
            _delay(dry_run)
        except Exception as e:
            print(f"[ERROR] {email}: {e}")

    # ── Follow-up 2 ──────────────────────────────────────────────────────────────
    cutoff_2 = (now - timedelta(days=FOLLOW_UP_2_DAYS)).isoformat()
    fu2_rows = conn.execute(
        """SELECT id, name, organization, email, research_focus, initial_subject
           FROM leads
           WHERE status = 'sent'
             AND follow_up_1_at IS NOT NULL
             AND follow_up_1_at < ?
             AND follow_up_2_at IS NULL""",
        (cutoff_2,)
    ).fetchall()

    for lead_id, name, org, email, research_focus, initial_subj in fu2_rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_follow_up_2(lead_id, name, org, research_focus, initial_subj)
        if dry_run:
            print(f"\n{'='*65}")
            print(f"[DRY RUN] FOLLOW-UP 2  to: {name} <{email}>")
            print(f"Subject: {subject}")
            print(f"\n{body}\n")
            sent_today += 1
            continue
        try:
            create_draft(email, subject, body)
            conn.execute("UPDATE leads SET follow_up_2_at=? WHERE id=?", (now.isoformat(), lead_id))
            conn.commit()
            print(f"[DRAFT] FU-2  -> {name} <{email}>")
            sent_today += 1
            _delay(dry_run)
        except Exception as e:
            print(f"[ERROR] {email}: {e}")

    # ── Follow-up 3 (graceful close) ──────────────────────────────────────────────
    cutoff_3 = (now - timedelta(days=FOLLOW_UP_3_DAYS)).isoformat()
    fu3_rows = conn.execute(
        """SELECT id, name, organization, email, initial_subject
           FROM leads
           WHERE status = 'sent'
             AND follow_up_2_at IS NOT NULL
             AND follow_up_2_at < ?
             AND follow_up_3_at IS NULL""",
        (cutoff_3,)
    ).fetchall()

    for lead_id, name, org, email, initial_subj in fu3_rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_follow_up_3(lead_id, name, org, initial_subj)
        if dry_run:
            print(f"\n{'='*65}")
            print(f"[DRY RUN] FOLLOW-UP 3 (close)  to: {name} <{email}>")
            print(f"Subject: {subject}")
            print(f"\n{body}\n")
            sent_today += 1
            continue
        try:
            create_draft(email, subject, body)
            conn.execute(
                "UPDATE leads SET follow_up_3_at=?, status='closed' WHERE id=?",
                (now.isoformat(), lead_id)
            )
            conn.commit()
            print(f"[DRAFT] FU-3 (close)  -> {name} <{email}>")
            sent_today += 1
            _delay(dry_run)
        except Exception as e:
            print(f"[ERROR] {email}: {e}")

    if dry_run:
        print(f"\nDone. {sent_today} email(s) previewed (nothing drafted or sent).")
    else:
        print(f"\nDone. {sent_today} draft(s) saved to your Zoho Drafts folder.")


# ── Status / Reporting ────────────────────────────────────────────────────────────
def mark_replied(conn, email):
    conn.execute("UPDATE leads SET status='replied' WHERE email=?", (email.lower(),))
    conn.commit()
    print(f"Marked {email} as replied.")


def mark_unsubscribed(conn, email):
    conn.execute("UPDATE leads SET status='unsubscribed' WHERE email=?", (email.lower(),))
    conn.commit()
    print(f"Marked {email} as unsubscribed.")


def show_status(conn):
    print("\nLead Pipeline:")
    print("-" * 30)
    for status in ('pending', 'sent', 'replied', 'closed', 'unsubscribed'):
        count = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status=?", (status,)
        ).fetchone()[0]
        print(f"  {status:<15} {count}")
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    print(f"  {'TOTAL':<15} {total}")

    print("\nTop Institutions (pending leads):")
    print("-" * 45)
    rows = conn.execute(
        """SELECT organization, COUNT(*) as cnt FROM leads
           WHERE status = 'pending'
           GROUP BY organization ORDER BY cnt DESC LIMIT 20"""
    ).fetchall()
    for org, cnt in rows:
        print(f"  {org:<40} {cnt}")


# ── CLI ────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Forrest Analytics Group -- Outreach Tool v2')
    parser.add_argument('--import-leads',      metavar='CSV',   help='Import leads from CSV')
    parser.add_argument('--send',              action='store_true', help='Send pending emails and follow-ups')
    parser.add_argument('--dry-run',           action='store_true', help='Preview emails without sending')
    parser.add_argument('--mark-replied',      metavar='EMAIL', help='Mark a lead as replied')
    parser.add_argument('--mark-unsubscribed', metavar='EMAIL', help='Mark a lead as opted out')
    parser.add_argument('--status',            action='store_true', help='Show pipeline summary')
    args = parser.parse_args()

    conn = init_db()

    if args.import_leads:
        import_leads(conn, args.import_leads)
    elif args.send:
        run_outreach(conn, dry_run=False)
    elif args.dry_run:
        run_outreach(conn, dry_run=True)
    elif args.mark_replied:
        mark_replied(conn, args.mark_replied)
    elif args.mark_unsubscribed:
        mark_unsubscribed(conn, args.mark_unsubscribed)
    elif args.status:
        show_status(conn)
    else:
        parser.print_help()
