"""
Product 1 — Daily Briefing Streamlit Viewer
============================================
Shows the last 30 days of briefings as an iMessage-style bubble thread.
Run from keystone-case-study/: streamlit run products/01_daily_briefing/app.py
"""

import sys
from datetime import timedelta
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from products.daily_briefing_helper import get_briefings_for_range
from shared import data_loader

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Keystone Daily Briefing — AI Demo",
    page_icon="📱",
    layout="centered",
)

# ── CSS: iMessage-style bubbles ────────────────────────────────────────────────
st.markdown("""
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif; }
  .phone-frame {
    max-width: 400px;
    margin: 0 auto;
    background: #f2f2f7;
    border-radius: 40px;
    padding: 30px 18px 24px 18px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.20);
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  }
  .phone-header {
    text-align: center;
    font-size: 15px;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 3px;
  }
  .phone-sub {
    text-align: center;
    font-size: 12px;
    color: #8e8e93;
    margin-bottom: 18px;
  }
  .bubble-date {
    text-align: right;
    font-size: 11px;
    color: #8e8e93;
    margin-bottom: 4px;
    padding-right: 4px;
  }
  .bubble-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 4px;
  }
  .bubble {
    background: #007aff;
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px;
    max-width: 84%;
    font-size: 14px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .delivered {
    text-align: right;
    font-size: 11px;
    color: #8e8e93;
    margin-top: 2px;
    margin-bottom: 14px;
    padding-right: 4px;
  }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📱 Owner's Daily Briefing")
    st.markdown("**AI Product 1 — Keystone Plumbing**")
    st.markdown("""
Every morning at **6 AM**, this SMS lands on the owner's phone:
a plain-English snapshot of yesterday's revenue, today's schedule,
open invoices, and any reputation issues — in under 180 words.

*Powered by Claude claude-sonnet-4-6 + live dataset.*
""")
    st.divider()

    end_date = data_loader.latest_job_date().date()
    start_date = end_date - timedelta(days=29)
    st.caption(f"Dataset range: {start_date} → {end_date}")

    num_days = st.slider("Days to show", min_value=5, max_value=30, value=10)

    if st.button("🔄 Regenerate All Briefings", use_container_width=True):
        with st.spinner("Calling Claude for 30 days of briefings…"):
            get_briefings_for_range(start_date, end_date)
        st.success("All briefings generated!")

    st.divider()
    st.caption("Built by [Forrest Analytics Group](https://forrestanalyticsgroup.com)")

# ── Main ────────────────────────────────────────────────────────────────────────
st.markdown("## 📱 Daily Briefing — iMessage View")
st.caption("Each bubble is an AI-generated SMS delivered to the owner at 6am.")

end_date = data_loader.latest_job_date().date()
start_date = end_date - timedelta(days=num_days - 1)

with st.spinner("Loading briefings…"):
    briefings = get_briefings_for_range(start_date, end_date)

if not briefings:
    st.info("No briefings found. Click **Regenerate All Briefings** in the sidebar.")
    st.stop()

sorted_dates = sorted(briefings.keys(), reverse=True)

# Phone frame
phone_html = '<div class="phone-frame">'
phone_html += '<div class="phone-header">AI Ops Assistant</div>'
phone_html += '<div class="phone-sub">Keystone Plumbing &amp; Drain</div>'

for d in sorted_dates[:num_days]:
    text = briefings[d].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    phone_html += f'<div class="bubble-date">{d} · 6:00 AM</div>'
    phone_html += f'<div class="bubble-row"><div class="bubble">{text}</div></div>'
    phone_html += '<div class="delivered">Delivered</div>'

phone_html += "</div>"

st.markdown(phone_html, unsafe_allow_html=True)

st.markdown("---")
with st.expander("📋 All briefings as plain text"):
    for d in sorted_dates:
        st.markdown(f"**{d}**")
        st.text(briefings[d])
        st.markdown("---")
