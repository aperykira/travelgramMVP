from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.demo_engine import (
    extract_profile_demo,
    generate_itinerary_demo,
    recommend_destinations_demo,
    refine_itinerary_demo,
)
from src.llm_client import call_openai_text, call_openai_with_images
from src.prompt_templates import (
    build_destination_prompt,
    build_itinerary_prompt,
    build_profile_prompt,
    build_refinement_prompt,
    destination_context,
)

load_dotenv()

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"

MASTER_PROMPT = (DATA_DIR / "master_prompt.md").read_text(encoding="utf-8")
KNOWLEDGE_PACK = json.loads((DATA_DIR / "static_knowledge_pack.json").read_text(encoding="utf-8"))

st.set_page_config(
    page_title="Travelgram",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Travelgram")
st.caption("Turn Instagram-inspired or uploaded travel inspiration into a personalized Travel Taste Profile, destination recommendations, and itinerary.")

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Generation mode", ["Demo Mode", "OpenAI API"], index=0)
    api_key = st.text_input("OpenAI API Key (optional)", type="password")
    model = st.text_input("Model name", value="gpt-4o-mini")
    st.info("Demo Mode works without an API key. API mode supports stronger outputs and optional image understanding.")

    st.divider()
    st.subheader("Guardrails")
    st.write("The assistant should not invent prices, hours, availability, bookings, live events, or hidden gems.")
    st.write("Dynamic details should be marked as items to verify.")

if "profile" not in st.session_state:
    st.session_state.profile = ""
if "recommendations" not in st.session_state:
    st.session_state.recommendations = ""
if "itinerary" not in st.session_state:
    st.session_state.itinerary = ""

tab1, tab2, tab3, tab4 = st.tabs([
    "1. Inspiration",
    "2. Taste Profile + Destinations",
    "3. Itinerary",
    "4. Refine"
])


def read_text_uploads(files) -> str:
    chunks = []
    for f in files or []:
        if f.type.startswith("text") or f.name.endswith((".txt", ".md", ".csv", ".json")):
            try:
                chunks.append(f"--- Uploaded file: {f.name} ---\n{f.getvalue().decode('utf-8', errors='ignore')}")
            except Exception:
                chunks.append(f"--- Uploaded file: {f.name} could not be decoded as text. ---")
    return "\n\n".join(chunks)


def uploaded_file_notes(files) -> str:
    if not files:
        return "No files uploaded."
    notes = []
    for f in files:
        notes.append(f"- {f.name} ({f.type}, {f.size} bytes)")
    return "\n".join(notes)


def image_files(files):
    return [f for f in (files or []) if (f.type or "").startswith("image/")]


def run_llm(prompt: str, files=None) -> str:
    if mode == "Demo Mode":
        raise RuntimeError("Demo Mode route should not call LLM.")
    imgs = image_files(files)
    if imgs:
        return call_openai_with_images(prompt, imgs, model=model, api_key=api_key or None)
    return call_openai_text(prompt, model=model, api_key=api_key or None)


with tab1:
    st.subheader("Add travel inspiration")
    st.write("Paste Instagram captions, saved reel notes, links, or any travel inspiration. You can also upload screenshots, notes, or itinerary files.")

    sample = """Kyoto street food, matcha cafés, quiet temples, boutique ryokans, scenic walking streets.
I like cozy cafés, local food markets, calm cultural experiences, and slow-paced days."""
    inspiration_text = st.text_area("Travel inspiration", value=sample, height=180)

    files = st.file_uploader(
        "Upload screenshots, images, notes, or documents",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "txt", "md", "csv", "json"],
    )

    if files:
        st.write("Uploaded files:")
        for f in files:
            st.write(f"- {f.name} ({f.type})")

    text_from_files = read_text_uploads(files)
    combined_inspiration = f"{inspiration_text}\n\n{text_from_files}".strip()
    file_notes = uploaded_file_notes(files)

    st.session_state["combined_inspiration"] = combined_inspiration
    st.session_state["files"] = files
    st.session_state["file_notes"] = file_notes

with tab2:
    st.subheader("Generate Travel Taste Profile")

    if st.button("Create Travel Taste Profile", type="primary"):
        combined_inspiration = st.session_state.get("combined_inspiration", "")
        file_notes = st.session_state.get("file_notes", "")

        with st.spinner("Creating profile..."):
            try:
                if mode == "Demo Mode":
                    st.session_state.profile = extract_profile_demo(combined_inspiration, file_notes)
                else:
                    prompt = build_profile_prompt(MASTER_PROMPT, combined_inspiration, file_notes)
                    st.session_state.profile = run_llm(prompt, st.session_state.get("files"))
            except Exception as e:
                st.error(f"Could not generate profile: {e}")

    if st.session_state.profile:
        st.markdown(st.session_state.profile)

        st.divider()
        st.subheader("Recommend destinations")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            trip_length = st.number_input("Trip length (days)", min_value=1, max_value=14, value=4)
        with col_b:
            budget = st.selectbox("Budget", ["Budget", "Mid-range", "Luxury", "Prefer not to specify"])
        with col_c:
            companions = st.selectbox("Traveling with", ["Solo", "Partner", "Friends", "Family"])

        constraints = {
            "days": int(trip_length),
            "budget": budget,
            "companions": companions,
        }
        st.session_state["constraints"] = constraints

        if st.button("Recommend destinations"):
            with st.spinner("Finding destination matches..."):
                try:
                    if mode == "Demo Mode":
                        st.session_state.recommendations = recommend_destinations_demo(
                            st.session_state.profile,
                            KNOWLEDGE_PACK,
                            constraints,
                        )
                    else:
                        prompt = build_destination_prompt(
                            MASTER_PROMPT,
                            st.session_state.profile,
                            KNOWLEDGE_PACK,
                            constraints,
                        )
                        st.session_state.recommendations = run_llm(prompt)
                except Exception as e:
                    st.error(f"Could not recommend destinations: {e}")

    if st.session_state.recommendations:
        st.markdown(st.session_state.recommendations)

with tab3:
    st.subheader("Generate itinerary")

    destinations = KNOWLEDGE_PACK.get("destinations", [])
    dest_options = {f"{d['destination']}, {d['country']}": d["destination_id"] for d in destinations}

    selected_label = st.selectbox("Select destination", list(dest_options.keys()))
    selected_id = dest_options[selected_label]
    selected_destination = destination_context(selected_id, KNOWLEDGE_PACK)

    col1, col2, col3 = st.columns(3)
    with col1:
        days = st.number_input("Days", min_value=1, max_value=14, value=int(st.session_state.get("constraints", {}).get("days", 4)))
    with col2:
        budget2 = st.selectbox("Budget range", ["Budget", "Mid-range", "Luxury", "Prefer not to specify"], index=1)
    with col3:
        companions2 = st.selectbox("Companions", ["Solo", "Partner", "Friends", "Family"], index=1)

    constraints2 = {
        "days": int(days),
        "budget": budget2,
        "companions": companions2,
    }
    st.session_state["constraints"] = constraints2

    if st.button("Generate itinerary", type="primary"):
        if not st.session_state.profile:
            st.warning("Create a Travel Taste Profile first.")
        else:
            with st.spinner("Generating itinerary..."):
                try:
                    if mode == "Demo Mode":
                        st.session_state.itinerary = generate_itinerary_demo(
                            st.session_state.profile,
                            selected_destination,
                            constraints2,
                        )
                    else:
                        prompt = build_itinerary_prompt(
                            MASTER_PROMPT,
                            st.session_state.profile,
                            selected_destination,
                            constraints2,
                        )
                        st.session_state.itinerary = run_llm(prompt)
                except Exception as e:
                    st.error(f"Could not generate itinerary: {e}")

    if st.session_state.itinerary:
        st.markdown(st.session_state.itinerary)
        st.download_button(
            "Download itinerary as Markdown",
            st.session_state.itinerary,
            file_name="ai_travel_itinerary.md",
            mime="text/markdown",
        )

with tab4:
    st.subheader("Refine itinerary")
    st.write("Try: ‘Make this cheaper’, ‘Make it more relaxed’, ‘Add more food experiences’, or ‘Focus on nature.’")

    if not st.session_state.itinerary:
        st.warning("Generate an itinerary first.")
    else:
        refinement_request = st.text_input("Refinement request", value="Make this cheaper and more relaxed.")
        if st.button("Refine itinerary"):
            with st.spinner("Refining..."):
                try:
                    if mode == "Demo Mode":
                        refined = refine_itinerary_demo(
                            st.session_state.itinerary,
                            refinement_request,
                            st.session_state.profile,
                            st.session_state.get("constraints", {}),
                        )
                    else:
                        prompt = build_refinement_prompt(
                            MASTER_PROMPT,
                            st.session_state.itinerary,
                            refinement_request,
                            st.session_state.profile,
                            st.session_state.get("constraints", {}),
                        )
                        refined = run_llm(prompt)
                    st.session_state.itinerary = refined
                except Exception as e:
                    st.error(f"Could not refine itinerary: {e}")

        st.markdown(st.session_state.itinerary)
