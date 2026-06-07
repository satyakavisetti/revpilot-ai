import streamlit as st
import time
from datetime import datetime

from crm import deals
from agents import (
    coordinator_agent,
    get_memory,
    prospecting_agent,
    metrics_agent,
    impact_agent
)
from actions import get_email_events


st.set_page_config(page_title="RevPilot AI", layout="wide")


# Clean UI Styling
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}

.card {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-box {
    text-align: center;
}

.log {
    background:#111827;
    padding:12px;
    border-radius:10px;
    margin-bottom:8px;
    border-left: 4px solid #6366f1;
}
</style>
""", unsafe_allow_html=True)


# Header
st.markdown("""
<h1 style='text-align:center;'>RevPilot AI</h1>
<p style='text-align:center;color:gray;'>
Autonomous Revenue Intelligence System
</p>
""", unsafe_allow_html=True)


# Metrics
total = len(deals)
recovered = len([d for d in deals if d["status"] == "Recovery Initiated"])
revenue = sum(d["value"] for d in deals if d["status"] == "Recovery Initiated")

metrics = metrics_agent(deals)
impact = impact_agent(deals)

st.markdown("## Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Deals", total)
c2.metric("Recovered Deals", recovered)
c3.metric("Revenue Impact", f"₹{revenue}")
c4.metric("Conversion Rate", f"{metrics['conversion']}%")

st.caption(f"Cycle Time Reduction: {metrics['cycle_reduction']}%")


# AI Control
st.markdown("## System Control")

auto_mode = st.toggle("Autonomous Mode")

if auto_mode:
    st.success("System running in autonomous mode")
else:
    st.info("Manual mode active")


# Pipeline Overview
st.markdown("## Pipeline Overview")

left, right = st.columns([1, 3])

with left:
    st.markdown("<div class='card'><div class='section-title'>Risk Distribution</div>", unsafe_allow_html=True)

    high = len([d for d in deals if d["days_no_reply"] > 10])
    medium = len([d for d in deals if 5 < d["days_no_reply"] <= 10])
    low = total - high - medium

    def bar(label, value, color):
        percent = int((value / max(total, 1)) * 100)
        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <b>{label}</b> ({value})
            <div style="background:#1f2937;border-radius:6px;">
                <div style="
                    width:{percent}%;
                    background:{color};
                    padding:6px;
                    border-radius:6px;
                    text-align:right;
                    color:white;">
                    {percent}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    bar("High Risk", high, "#ef4444")
    bar("Medium Risk", medium, "#f59e0b")
    bar("Low Risk", low, "#22c55e")

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    colA, colB = st.columns(2)

    with colA:
        st.markdown("<div class='card'><div class='section-title'>System Status</div>", unsafe_allow_html=True)

        st.write("Intelligence Engine: Active")
        st.write("Strategy Engine: Running")
        st.write("Execution Engine: Active")
        st.write("Learning Engine: Updating")

        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown("<div class='card'><div class='section-title'>Live Performance</div>", unsafe_allow_html=True)

        st.metric("Decisions Processed", total)
        st.metric("Actions Executed", recovered)
        st.metric("Success Rate", f"{int((recovered/max(total,1))*100)}%")
        st.metric("Avg Response Time", "0.3s")

        st.markdown("</div>", unsafe_allow_html=True)


# Intelligence Layer
st.markdown("## Intelligence Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'><div class='section-title'>Risk Evaluation</div>", unsafe_allow_html=True)

    sample = deals[0]
    result = coordinator_agent(sample)

    st.write(f"Inactivity: {sample['days_no_reply']} days")
    st.write(f"Engagement Score: {sample['engagement_score']}")
    st.write(f"Churn Prediction: {result.get('prediction', 0)}%")

    st.progress(result.get('prediction', 0) / 100)

    st.markdown("</div>", unsafe_allow_html=True)


with col2:
    st.markdown("<div class='card'><div class='section-title'>Strategy Summary</div>", unsafe_allow_html=True)

    st.write(f"Recovered: {recovered}")
    st.write(f"Pending: {total - recovered}")

    st.markdown("</div>", unsafe_allow_html=True)


with col3:
    st.markdown("<div class='card'><div class='section-title'>Key Insights</div>", unsafe_allow_html=True)

    st.write("Deal inactivity strongly impacts conversion")
    st.write("Competitive signals influence decision making")
    st.write("Faster follow-ups improve recovery rate")

    st.markdown("</div>", unsafe_allow_html=True)


# Autonomous Execution
st.markdown("## Autonomous Execution")

log_box = st.empty()
logs = []

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    logs.insert(0, f"<div class='log'><b>[{t}]</b><br>{msg}</div>")
    log_box.markdown("".join(logs[:10]), unsafe_allow_html=True)


if st.button("Run Execution Cycle") or auto_mode:

    progress = st.progress(0)

    for i, deal in enumerate(deals):

        result = coordinator_agent(deal)

        if result.get("risk") and result["risk"] != "LOW":

            log(f"Risk detected for {deal['company']}")
            log(f"Prediction: {result.get('prediction', 0)}%")

            if "strategy" in result:
                log(f"Strategy: {result['strategy']['name']}")

            if "email" in result:
                log("Generating outreach")
                log(result["email"])

            if "email_event" in result:
                event = result["email_event"]
                log(f"Email sent to {deal['email']}")
                log(f"Opened: {event['opened']} | Replied: {event['replied']}")

            if "adaptation" in result:
                log(f"Adaptation: {result['adaptation']}")
            if "trace" in result:
                log(f"Trace: {result['trace']}")

            log("Cycle complete")

        progress.progress((i + 1) / len(deals))
        time.sleep(0.2)

    st.success("Execution cycle completed")


# Learning
st.markdown("## Learning Engine")

memory = get_memory()

if memory:
    st.metric("Learned Strategies", len(memory))
    for m in memory:
        st.write(f"{m['company']} -> {m['strategy']}")
else:
    st.info("Learning in progress")


# Prospecting
st.markdown("## Prospecting")

for lead in prospecting_agent():
    st.markdown(f"""
    <div class='card'>
    <b>{lead['company']}</b> ({lead['industry']})<br>
    Score: {lead['score']}<br>
    {lead['outreach']}
    </div>
    """, unsafe_allow_html=True)


# Email Tracking
st.markdown("## Email Activity")

events = get_email_events()

if events:
    for e in events:
        status = "Replied" if e["replied"] else ("Opened" if e["opened"] else "Not Opened")

        st.markdown(f"""
        <div class='card'>
        {e['email']}<br>
        Status: {status}<br>
        Time: {e['time']}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No activity recorded yet")