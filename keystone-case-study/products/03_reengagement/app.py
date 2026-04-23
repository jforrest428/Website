"""
Product 3 — Re-Engagement Engine Streamlit Dashboard
=====================================================
Shows segment sizes, projected revenue, and sample messages.
Run from keystone-case-study/: streamlit run products/03_reengagement/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from segment import (
    REACTIVATION_RATES,
    AVG_JOB_REVENUE,
    SEGMENTS,
    projected_revenue,
    as_of_date,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Keystone Re-Engagement — AI Demo",
    page_icon="💬",
    layout="wide",
)

SEGMENT_LABELS = {
    "water_heater_aging":    "🔥 Water Heater Aging (5+ years)",
    "sump_pump_seasonal":    "💧 Sump Pump Seasonal Check",
    "drain_cleaning_lapsed": "🚿 Drain Cleaning Lapsed (18+ mo)",
    "maintenance_lapsed":    "🔧 Annual Maintenance Lapsed (13+ mo)",
    "high_ltv_dormant":      "⭐ High-LTV Dormant Customers",
}

OUTPUT_DIR = Path(__file__).parent / "output"

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💬 Re-Engagement Engine")
    st.markdown("**AI Product 3 — Keystone Plumbing**")
    st.markdown("""
Segments the customer list weekly into 5 re-engagement buckets
and writes personalized SMS + email outreach for each customer.

*Powered by Claude claude-sonnet-4-6 + live dataset.*
""")
    st.divider()
    st.caption(f"Dataset as of: {as_of_date()}")

    if st.button("▶ Run Segmentation & Draft Messages", use_container_width=True):
        with st.spinner("Running segmentation and calling Claude…"):
            import subprocess, sys as sys2
            subprocess.run(
                [sys2.executable, str(ROOT / "products" / "03_reengagement" / "segment.py"), "--limit", "5"],
                cwd=str(ROOT),
            )
        st.sidebar.success("Done!")
        st.rerun()

    st.divider()
    st.caption("Built by [Forrest Intelligence](https://forrestintelligence.com)")

# ── Load segment data ──────────────────────────────────────────────────────────
segment_dfs: dict[str, pd.DataFrame] = {}
for seg_name in SEGMENTS:
    csv_path = OUTPUT_DIR / f"{seg_name}.csv"
    if csv_path.exists():
        segment_dfs[seg_name] = pd.read_csv(csv_path)
    else:
        # Run segmentation (size only) to show counts
        try:
            df = SEGMENTS[seg_name]()
            segment_dfs[seg_name] = df
        except Exception:
            segment_dfs[seg_name] = pd.DataFrame()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 💬 Customer Re-Engagement Dashboard")
st.caption("Weekly segmentation of lapsed customers with AI-drafted personalized outreach.")

# ── KPI Row ────────────────────────────────────────────────────────────────────
total_customers = sum(len(df) for df in segment_dfs.values())
total_projected = sum(projected_revenue(seg, len(df))["projected_revenue"] for seg, df in segment_dfs.items())
has_drafts = any("SMS Draft" in df.columns for df in segment_dfs.values())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Dormant Customers", f"{total_customers:,}")
k2.metric("Projected Recovery", f"${total_projected:,.0f}")
k3.metric("Avg Reactivation Rate", "12%")
k4.metric("Avg Job Value", "$980")

st.markdown("---")

# ── Segment Cards ──────────────────────────────────────────────────────────────
st.markdown("### Segment Breakdown")

seg_cols = st.columns(len(SEGMENTS))
for i, (seg_name, label) in enumerate(SEGMENT_LABELS.items()):
    df = segment_dfs.get(seg_name, pd.DataFrame())
    proj = projected_revenue(seg_name, len(df))
    with seg_cols[i]:
        st.markdown(f"**{label}**")
        st.metric("Customers", proj["size"])
        st.metric("Projected Revenue", f"${proj['projected_revenue']:,.0f}")
        st.caption(f"{proj['reactivation_rate_pct']:.0f}% reactivation × ${proj['avg_job_revenue']:,.0f} avg job")

st.markdown("---")

# ── Revenue Projection Chart ───────────────────────────────────────────────────
st.markdown("### Projected Recovered Revenue by Segment")
chart_data = pd.DataFrame({
    "Segment": [SEGMENT_LABELS[s].split(" ", 1)[1] for s in SEGMENTS],
    "Projected Revenue ($)": [projected_revenue(s, len(segment_dfs.get(s, pd.DataFrame())))["projected_revenue"] for s in SEGMENTS],
})
st.bar_chart(chart_data.set_index("Segment"))

st.markdown("---")

# ── Drill-down by segment ──────────────────────────────────────────────────────
st.markdown("### Sample Outreach Messages")

selected_seg = st.selectbox(
    "Select segment to preview",
    options=list(SEGMENTS.keys()),
    format_func=lambda s: SEGMENT_LABELS[s],
)

df = segment_dfs.get(selected_seg, pd.DataFrame())

if df.empty:
    st.info("No data for this segment. Click **Run Segmentation** in the sidebar.")
elif "SMS Draft" not in df.columns:
    st.info(f"{len(df)} customers in this segment. Click **Run Segmentation** to generate outreach messages.")
    st.dataframe(df.head(10))
else:
    st.caption(f"{len(df)} customers · {SEGMENT_LABELS[selected_seg]}")

    for i, row in df.head(5).iterrows():
        with st.expander(
            f"**{row.get('Customer Name', 'Customer')}** — {row.get('Job Type', '')} — "
            f"{str(row.get('Last Service', ''))[:10]} ({row.get('Months Since', 0):.0f} mo ago)"
        ):
            sms_col, email_col = st.columns([1, 2])
            with sms_col:
                st.markdown("**📱 SMS Draft**")
                sms = str(row.get("SMS Draft", ""))
                char_count = len(sms)
                st.text_area("SMS", value=sms, height=100, key=f"sms_{i}", label_visibility="collapsed")
                color = "red" if char_count > 160 else "green"
                st.caption(f":{color}[{char_count}/160 characters]")
            with email_col:
                st.markdown("**📧 Email Draft**")
                st.markdown(f"**Subject:** {row.get('Email Subject', '')}")
                st.text_area("Body", value=str(row.get("Email Body", "")), height=160, key=f"email_{i}", label_visibility="collapsed")
