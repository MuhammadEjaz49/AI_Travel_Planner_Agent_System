import os
import streamlit as st
from datetime import datetime
from io import BytesIO

from langchain_core.messages import HumanMessage
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from main import app   # your LangGraph / agent system

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

# ─────────────────────────────
# SIDEBAR
# ─────────────────────────────
st.sidebar.title("🌍 AI Travel Planner")

thread_id = st.sidebar.text_input(
    "User ID",
    value="Asif_user",
    help="Session ID for memory"
)

st.sidebar.subheader("Powered by")
st.sidebar.write([
    "LangGraph",
    "Groq (LLaMA 3)",
    "PostgreSQL",
    "Tavily Search",
    "AviationStack"
])

st.sidebar.subheader("Agent Pipeline")
st.sidebar.write([
    "Flight Agent",
    "Hotel Agent",
    "Itinerary Agent",
    "Final Agent"
])

# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("✈️ AI Travel Booking System")
st.write("Multi-agent system for flights, hotels, itinerary, and final travel plan.")

# ─────────────────────────────
# INPUT
# ─────────────────────────────
quick_options = [
    "7-day Japan trip",
    "Paris trip for 5 days",
    "Dubai weekend trip",
    "Bali backpacking 10 days"
]

selected = st.radio("Quick Trip Ideas", quick_options)

user_query = st.text_area(
    "Describe your trip",
    value=selected,
    placeholder="Example: Plan a 7-day trip to Japan including flights, hotels and itinerary"
)

generate = st.button("🚀 Generate Travel Plan")

# ─────────────────────────────
# PDF GENERATOR
# ─────────────────────────────
def generate_pdf(text: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    story = []

    for line in text.split("\n"):
        story.append(Paragraph(line.replace("<", "&lt;").replace(">", "&gt;"), style))
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ─────────────────────────────
# AGENT RUN
# ─────────────────────────────
if generate:
    if not user_query.strip():
        st.warning("Please enter a trip description.")
        st.stop()

    config = {"configurable": {"thread_id": thread_id}}

    collected = {
        "flight_results": "",
        "hotel_results": "",
        "itinerary": "",
        "final_response": "",
        "llm_calls": 0
    }

    st.subheader("🤖 Agent Execution")

    for chunk in app.stream(
        {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
        stream_mode="updates",
    ):
        for node_name, state_update in chunk.items():

            st.write(f"### {node_name}")

            if node_name == "flight_agent":
                collected["flight_results"] = state_update.get("flight_results", "")
                st.write(collected["flight_results"])

            elif node_name == "hotel_agent":
                collected["hotel_results"] = state_update.get("hotel_results", "")
                st.write(collected["hotel_results"])

            elif node_name == "itinerary_agent":
                collected["itinerary"] = state_update.get("itinerary", "")
                st.write(collected["itinerary"])

            elif node_name == "final_agent":
                msgs = state_update.get("messages", [])
                collected["final_response"] = msgs[-1].content if msgs else ""
                st.write(collected["final_response"])

            collected["llm_calls"] = state_update.get(
                "llm_calls",
                collected["llm_calls"]
            )

    # ─────────────────────────────
    # STATS
    # ─────────────────────────────
    st.subheader("📊 Stats")
    st.write({
        "Agents Run": 4,
        "LLM Calls": collected["llm_calls"],
        "Status": "Completed"
    })

    # ─────────────────────────────
    # FINAL OUTPUT
    # ─────────────────────────────
    if collected["final_response"]:
        st.subheader("🧠 Final Travel Plan")
        st.write(collected["final_response"])

    # ─────────────────────────────
    # SAVE CONTENT
    # ─────────────────────────────
    file_content = f"""
Travel Plan

Query: {user_query}
Generated: {datetime.now()}
User ID: {thread_id}

--------------------------------

Flight Info:
{collected['flight_results']}

--------------------------------

Hotel Info:
{collected['hotel_results']}

--------------------------------

Itinerary:
{collected['itinerary']}

--------------------------------

Final Plan:
{collected['final_response']}

--------------------------------
LLM Calls: {collected['llm_calls']}
"""

    # ─────────────────────────────
    # PDF DOWNLOAD
    # ─────────────────────────────
    pdf_buffer = generate_pdf(file_content)

    st.download_button(
        label="⬇️ Download PDF Travel Plan",
        data=pdf_buffer,
        file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )