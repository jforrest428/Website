"""
Product 2 — Review Reply Manager Streamlit UI
==============================================
Three-pane interface: review | drafted reply | approve/edit/skip
Run from keystone-case-study/: streamlit run products/02_review_reply/app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from products.review_reply_helper import load_drafts, save_approval, update_status
from patterns import flagged_techs, response_rate_by_platform, review_velocity

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Keystone Review Manager — AI Demo",
    page_icon="⭐",
    layout="wide",
)

st.markdown("""
<style>
  .star-gold { color: #f5a623; font-size: 18px; }
  .review-card { background: #f8f9fa; border-radius: 10px; padding: 16px; margin-bottom: 8px; }
  .badge-red { background: #fee2e2; color: #b91c1c; border-radius: 4px; padding: 2px 8px; font-size: 12px; font-weight: 600; }
  .badge-green { background: #dcfce7; color: #15803d; border-radius: 4px; padding: 2px 8px; font-size: 12px; font-weight: 600; }
  .badge-blue { background: #dbeafe; color: #1d4ed8; border-radius: 4px; padding: 2px 8px; font-size: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────────
page = st.sidebar.radio(
    "View",
    ["📬 Review Queue", "📊 Pattern Analysis"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Review Reply Manager")
st.sidebar.markdown("""
**AI Product 2 — Keystone Plumbing**

Drafts personalized replies to every Google, Yelp, and Angi review.
Owner approves with one click. Flags techs with repeat complaints.

*Powered by Claude claude-sonnet-4-6.*
""")

if st.sidebar.button("🔄 Draft New Replies", use_container_width=True):
    with st.spinner("Calling Claude to draft replies…"):
        import subprocess, sys
        subprocess.run(
            [sys.executable, str(ROOT / "products" / "02_review_reply" / "draft_replies.py"), "--limit", "20"],
            cwd=str(ROOT),
        )
    st.sidebar.success("Done! Refresh to see new drafts.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: REVIEW QUEUE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📬 Review Queue":
    st.markdown("## ⭐ Review Reply Queue")

    drafts = load_drafts()

    if not drafts:
        st.info(
            "No drafts found. Run `python products/02_review_reply/draft_replies.py` first, "
            "or click **Draft New Replies** in the sidebar."
        )
        st.stop()

    # Filter controls
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        status_filter = st.selectbox("Status", ["pending", "approved", "skipped", "all"], index=0)
    with col_b:
        star_filter = st.selectbox("Stars", ["all", "1", "2", "3", "4", "5"], index=0)
    with col_c:
        platform_filter = st.selectbox(
            "Platform",
            ["all"] + sorted({d["platform"] for d in drafts if d.get("platform")}),
        )

    filtered = drafts
    if status_filter != "all":
        filtered = [d for d in filtered if d.get("status") == status_filter]
    if star_filter != "all":
        filtered = [d for d in filtered if d.get("stars") == int(star_filter)]
    if platform_filter != "all":
        filtered = [d for d in filtered if d.get("platform") == platform_filter]

    # Stats bar
    total = len(drafts)
    approved = sum(1 for d in drafts if d.get("status") == "approved")
    pending = sum(1 for d in drafts if d.get("status") == "pending")
    skipped = sum(1 for d in drafts if d.get("status") == "skipped")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Drafts", total)
    m2.metric("Pending", pending)
    m3.metric("Approved", approved)
    m4.metric("Skipped", skipped)

    st.markdown("---")

    if not filtered:
        st.info("No reviews match the current filters.")
        st.stop()

    # Review cards
    for i, draft in enumerate(filtered):
        stars = draft.get("stars", 5)
        star_str = "★" * stars + "☆" * (5 - stars)
        status = draft.get("status", "pending")

        status_badge = {
            "pending": '<span class="badge-blue">Pending</span>',
            "approved": '<span class="badge-green">Approved</span>',
            "skipped": '<span class="badge-red">Skipped</span>',
        }.get(status, "")

        with st.container():
            st.markdown(f"### {star_str} &nbsp; {draft.get('platform')} &nbsp; {status_badge} &nbsp; `{draft.get('review_date', '')}`", unsafe_allow_html=True)
            if draft.get("tech_mentioned"):
                st.caption(f"Tech mentioned: **{draft['tech_mentioned']}**")

            left, right = st.columns([1, 1])

            with left:
                st.markdown("**Customer review:**")
                st.markdown(f"> {draft.get('review_text', '')}")

            with right:
                st.markdown("**AI-drafted reply:**")
                edited = st.text_area(
                    "Edit reply",
                    value=draft.get("drafted_reply", ""),
                    height=180,
                    key=f"reply_{draft['review_id']}",
                    label_visibility="collapsed",
                )

                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("✅ Approve", key=f"approve_{draft['review_id']}", use_container_width=True):
                        save_approval(draft["review_id"], edited)
                        update_status(draft["review_id"], "approved")
                        st.toast(f"Reply approved for {draft['review_id']}", icon="✅")
                        st.rerun()
                with btn2:
                    if st.button("✏️ Edit & Approve", key=f"edit_{draft['review_id']}", use_container_width=True):
                        save_approval(draft["review_id"], edited)
                        update_status(draft["review_id"], "approved")
                        st.toast("Edited reply saved!", icon="✏️")
                        st.rerun()
                with btn3:
                    if st.button("⏭ Skip", key=f"skip_{draft['review_id']}", use_container_width=True):
                        update_status(draft["review_id"], "skipped")
                        st.rerun()

            st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PATTERN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Pattern Analysis":
    st.markdown("## 📊 Tech Coaching Report")
    st.caption("Surfaces technicians with repeat negative review mentions so the owner can coach proactively.")

    flagged = flagged_techs(min_mentions=2, window_days=90)

    if flagged:
        for tech in flagged:
            with st.expander(f"⚠️ {tech['tech_name']} — {tech['count']} negative mentions", expanded=True):
                for rev in sorted(tech["reviews"], key=lambda r: r["Date"], reverse=True):
                    stars_str = "★" * int(rev["Stars"]) + "☆" * (5 - int(rev["Stars"]))
                    st.markdown(f"**{rev['Date']} · {rev['Platform']} · {stars_str}**")
                    st.markdown(f"> {rev['Review Text']}")
                    st.markdown("---")
    else:
        st.success("No techs with 2+ negative mentions in the last 90 days. 🎉")

    st.markdown("### Review Velocity (last 30 days)")
    velocity = review_velocity(30)
    vel_cols = st.columns(5)
    for i, stars in enumerate([5, 4, 3, 2, 1]):
        count = velocity.get(stars, 0)
        vel_cols[i].metric(f"{'★' * stars}", count)

    st.markdown("### Response Rate by Platform")
    rates = response_rate_by_platform()
    rate_data = {
        "Platform": list(rates.keys()),
        "Response Rate %": [v["rate_pct"] for v in rates.values()],
        "Total Reviews": [v["total"] for v in rates.values()],
        "Responded": [v["responded"] for v in rates.values()],
    }
    st.bar_chart({"data": rate_data["Response Rate %"]}, height=200)
    import pandas as pd
    st.dataframe(pd.DataFrame(rate_data).set_index("Platform"))
