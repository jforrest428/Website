"""
Forrest Analytics Group — Email Outreach Script

Commands:
  python outreach.py --import-leads leads.csv   import leads from CSV
  python outreach.py --send                      send pending emails + follow-ups
  python outreach.py --dry-run                   preview without sending
  python outreach.py --mark-replied email        mark a lead as replied
  python outreach.py --status                    show pipeline summary
"""

import smtplib
import sqlite3
import csv
import os
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
GMAIL_ADDRESS    = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASS   = os.getenv("GMAIL_APP_PASSWORD")
FOLLOW_UP_1_DAYS = int(os.getenv("FOLLOW_UP_1_DAYS", 3))
FOLLOW_UP_2_DAYS = int(os.getenv("FOLLOW_UP_2_DAYS", 7))
DAILY_LIMIT      = int(os.getenv("DAILY_LIMIT", 20))
DB_PATH          = os.path.join(os.path.dirname(__file__), "outreach.db")


# ── Email Templates ─────────────────────────────────────────────────────────────
def template_initial(name, organization):
    subject = f"Data Analytics Support — {organization}"
    body = f"""\
Hi {name},

I came across {organization} and wanted to reach out. I run Forrest Analytics Group, \
a boutique analytics consulting firm that helps graduate researchers and organizations \
with statistical analysis, survey design, and applied data work.

If you're working on research that involves data analysis — or have a project where \
cleaner data or clearer results would make a difference — I'd love to learn more. \
I offer a free 15-minute call to see if there's a fit.

Would you be open to a quick conversation?

Best,
Joshua Forrest
Forrest Analytics Group
forrestanalyticsgroup.com
"""
    return subject, body


def template_follow_up_1(name, organization):
    subject = f"Re: Data Analytics Support — {organization}"
    body = f"""\
Hi {name},

Just following up on my previous note. I know things get busy — happy to keep this short.

If data analysis, methodology support, or research interpretation is something on \
your radar, I'm here. Free 15-minute call, no obligation.

Best,
Joshua Forrest
Forrest Analytics Group
forrestanalyticsgroup.com
"""
    return subject, body


def template_follow_up_2(name, organization):
    subject = f"Re: Data Analytics Support — {organization}"
    body = f"""\
Hi {name},

Last follow-up — I promise. If the timing isn't right, no worries at all.

If you ever need statistical support, research methodology help, or applied analytics, \
feel free to reach out at jf10747454@sju.edu or book a free call at forrestanalyticsgroup.com.

Best,
Joshua Forrest
Forrest Analytics Group
"""
    return subject, body


# ── Database ────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            organization     TEXT NOT NULL,
            email            TEXT UNIQUE NOT NULL,
            status           TEXT DEFAULT 'pending',
            initial_sent_at  TEXT,
            follow_up_1_at   TEXT,
            follow_up_2_at   TEXT,
            created_at       TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def import_leads(conn, csv_path):
    added = 0
    skipped = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                conn.execute(
                    "INSERT INTO leads (name, organization, email) VALUES (?, ?, ?)",
                    (row['name'].strip(), row['organization'].strip(), row['email'].strip().lower())
                )
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1
    conn.commit()
    print(f"Imported {added} lead(s). {skipped} already existed.")


# ── Sending ─────────────────────────────────────────────────────────────────────
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From']    = GMAIL_ADDRESS
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())


def run_outreach(conn, dry_run=False):
    now = datetime.now()
    sent_today = 0

    # ── Initial emails ──────────────────────────────────────────────────────────
    rows = conn.execute(
        "SELECT id, name, organization, email FROM leads WHERE status = 'pending' LIMIT ?",
        (DAILY_LIMIT,)
    ).fetchall()

    for lead_id, name, org, email in rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_initial(name, org)
        if dry_run:
            print(f"[DRY RUN] INITIAL     → {name} <{email}>")
            continue
        try:
            send_email(email, subject, body)
            conn.execute(
                "UPDATE leads SET status='sent', initial_sent_at=? WHERE id=?",
                (now.isoformat(), lead_id)
            )
            conn.commit()
            print(f"[SENT]    INITIAL     → {name} <{email}>")
            sent_today += 1
        except Exception as e:
            print(f"[ERROR]   {email}: {e}")

    # ── Follow-up 1 ─────────────────────────────────────────────────────────────
    cutoff_1 = (now - timedelta(days=FOLLOW_UP_1_DAYS)).isoformat()
    rows = conn.execute("""
        SELECT id, name, organization, email FROM leads
        WHERE status = 'sent'
          AND initial_sent_at < ?
          AND follow_up_1_at IS NULL
    """, (cutoff_1,)).fetchall()

    for lead_id, name, org, email in rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_follow_up_1(name, org)
        if dry_run:
            print(f"[DRY RUN] FOLLOW-UP 1 → {name} <{email}>")
            continue
        try:
            send_email(email, subject, body)
            conn.execute(
                "UPDATE leads SET follow_up_1_at=? WHERE id=?",
                (now.isoformat(), lead_id)
            )
            conn.commit()
            print(f"[SENT]    FOLLOW-UP 1 → {name} <{email}>")
            sent_today += 1
        except Exception as e:
            print(f"[ERROR]   {email}: {e}")

    # ── Follow-up 2 ─────────────────────────────────────────────────────────────
    cutoff_2 = (now - timedelta(days=FOLLOW_UP_2_DAYS)).isoformat()
    rows = conn.execute("""
        SELECT id, name, organization, email FROM leads
        WHERE status = 'sent'
          AND follow_up_1_at IS NOT NULL
          AND follow_up_1_at < ?
          AND follow_up_2_at IS NULL
    """, (cutoff_2,)).fetchall()

    for lead_id, name, org, email in rows:
        if sent_today >= DAILY_LIMIT:
            break
        subject, body = template_follow_up_2(name, org)
        if dry_run:
            print(f"[DRY RUN] FOLLOW-UP 2 → {name} <{email}>")
            continue
        try:
            send_email(email, subject, body)
            conn.execute(
                "UPDATE leads SET follow_up_2_at=? WHERE id=?",
                (now.isoformat(), lead_id)
            )
            conn.commit()
            print(f"[SENT]    FOLLOW-UP 2 → {name} <{email}>")
            sent_today += 1
        except Exception as e:
            print(f"[ERROR]   {email}: {e}")

    print(f"\nDone. {sent_today} email(s) {'would be ' if dry_run else ''}sent.")


def mark_replied(conn, email):
    conn.execute("UPDATE leads SET status='replied' WHERE email=?", (email.lower(),))
    conn.commit()
    print(f"Marked {email} as replied.")


def show_status(conn):
    print("\nLead Pipeline:")
    print("-" * 25)
    for status in ('pending', 'sent', 'replied', 'unsubscribed'):
        count = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status=?", (status,)
        ).fetchone()[0]
        print(f"  {status:<15} {count}")
    total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    print(f"  {'TOTAL':<15} {total}")


# ── CLI ──────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Forrest Analytics Group — Outreach Tool')
    parser.add_argument('--import-leads',  metavar='CSV',   help='Import leads from a CSV file')
    parser.add_argument('--send',          action='store_true', help='Send pending emails and follow-ups')
    parser.add_argument('--dry-run',       action='store_true', help='Preview emails without sending')
    parser.add_argument('--mark-replied',  metavar='EMAIL', help='Mark a lead as replied')
    parser.add_argument('--status',        action='store_true', help='Show pipeline summary')
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
    elif args.status:
        show_status(conn)
    else:
        parser.print_help()
