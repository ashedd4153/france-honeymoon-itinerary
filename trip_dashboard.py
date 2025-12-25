from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import streamlit as st

BASE_DIR = Path(__file__).parent

# --- Data Loading ---

def load_itinerary() -> dict[str, Any]:
    itinerary_path = BASE_DIR / "itinerary.json"
    if not itinerary_path.exists():
        st.error(f"Error: {itinerary_path} not found.")
        return {}
    with open(itinerary_path, "r", encoding="utf-8") as f:
        return json.load(f)

ITINERARY = load_itinerary()
LOCATIONS = ITINERARY.get("destinations", [])
PLANNING_DOCS = ITINERARY.get("planning_docs", {})
TRIP_TITLE = ITINERARY.get("trip_title", "Honeymoon Dashboard")
DATES_SUMMARY = ITINERARY.get("dates_summary", "")

# --- Helpers ---

def load_markdown(relative_path: str, drop_title: bool = False) -> str:
    """Load markdown content and remove back-links to the README."""
    path = BASE_DIR / relative_path
    if not path.exists():
        return f"*{relative_path} not found*"
    text = path.read_text(encoding="utf-8").strip()
    lines = [
        line for line in text.splitlines() if "[← Back to Itinerary]" not in line
    ]
    if drop_title and lines and lines[0].startswith("#"):
        lines = lines[1:]
    return "\n".join(lines).strip()

def render_markdown_with_images(content: str) -> None:
    """Render markdown content with proper image handling for Streamlit."""
    pattern = r'!\[(.*?)\]\((.*?)\)'
    parts = re.split(pattern, content)
    
    i = 0
    while i < len(parts):
        if i + 2 < len(parts):
            text_before = parts[i]
            if text_before.strip():
                st.markdown(text_before)
            
            potential_alt = parts[i + 1]
            potential_path = parts[i + 2]
            
            if potential_path and potential_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                img_path = BASE_DIR / potential_path
                if img_path.exists():
                    st.image(str(img_path), caption=potential_alt, use_container_width=True)
                else:
                    st.warning(f"Image not found: {potential_path}")
                i += 3
            else:
                i += 1
        else:
            if parts[i].strip():
                st.markdown(parts[i])
            i += 1

def render_location_details(location: dict[str, Any]) -> None:
    st.subheader(f"{location['emoji']} {location['name']} · {location['dates']}")
    summary = location.get("summary")
    if summary:
        st.info(summary)
    content = load_markdown(location["file"], drop_title=True)
    render_markdown_with_images(content)

def render_planning_section(title: str, relative_path: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(load_markdown(relative_path, drop_title=False))

# --- Pages ---

def overview_page() -> None:
    st.title(TRIP_TITLE)
    st.caption(DATES_SUMMARY)

    # Metrics
    metrics = ITINERARY.get("metrics", [])
    if metrics:
        cols = st.columns(len(metrics))
        for col, metric in zip(cols, metrics):
            col.metric(metric["label"], metric["value"])

    st.divider()

    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("### 📅 Timeline Snapshot")
        # Generate calendar table dynamically or use from itinerary.json if added
        # For now, let's keep it simple as a list or a static table if available
        # I'll use a simplified version for now
        CALENDAR_TABLE = """| Sun | Mon | Tue | Wed | Thu | Fri | Sat |
|-----|-----|-----|-----|-----|-----|-----|
| ✈️19 | 🗼20 | 🗼21 | 🗼22 | 🗼23 | 👑24 | 🏰25 |
| 🏰26 | 🍷27 | 🌊28 | 🌊29 | 🥘30 | 🥘31 | 🥘1  |
| ✈️2  |     |     |     |     |     |     |
"""
        st.markdown(CALENDAR_TABLE)
        st.caption("*Colors show where you're sleeping that night*")

    with col2:
        st.markdown("### 📍 Segments")
        for loc in LOCATIONS:
            if loc['days'] > 0:
                st.write(f"{loc['emoji']} **{loc['name']}** – {loc['dates']} ({loc['days']} nights)")
            else:
                st.write(f"{loc['emoji']} **{loc['name']}** – {loc['dates']}")
        
        google_maps_link = ITINERARY.get("google_maps_link")
        if google_maps_link:
            st.link_button("🗺️ View Route on Google Maps", google_maps_link)

    st.divider()
    
    st.markdown("### 🗂 Quick Access Planning")
    cols = st.columns(len(PLANNING_DOCS))
    for col, (title, path) in zip(cols, PLANNING_DOCS.items()):
        with col:
            st.markdown(f"**{title}**")
            st.caption(f"Browse {path}")

def destinations_page() -> None:
    st.title("Destination Details")
    
    # Filter to actual destinations (not fly out/home)
    destinations = [loc for loc in LOCATIONS if loc["days"] > 0]
    
    # Use tabs for destinations if there aren't too many, otherwise a selectbox
    if len(destinations) <= 10:
        tabs = st.tabs([f"{loc['emoji']} {loc['name']}" for loc in destinations])
        for tab, loc in zip(tabs, destinations):
            with tab:
                render_location_details(loc)
    else:
        selected_name = st.selectbox(
            "Choose a segment to explore",
            [f"{loc['name']} ({loc['dates']})" for loc in destinations],
        )
        selected = next(loc for loc in destinations if loc["name"] in selected_name)
        render_location_details(selected)

def logistics_page() -> None:
    st.title("Flights & Transport Logistics")
    
    tab_names = list(PLANNING_DOCS.keys())
    # Filter logistics specific docs if needed, for now just show them
    logistics_docs = {k: v for k, v in PLANNING_DOCS.items() if "Packing" not in k}
    
    if logistics_docs:
        tabs = st.tabs(list(logistics_docs.keys()))
        for tab, (title, path) in zip(tabs, logistics_docs.items()):
            with tab:
                render_planning_section(title, path)
    else:
        st.write("No logistics docs found.")

def packing_page() -> None:
    st.title("Packing & Prep")
    packing_path = PLANNING_DOCS.get("Packing List")
    if packing_path:
        render_planning_section("Packing Checklist", packing_path)
    else:
        st.warning("Packing List not found in itinerary.json")
    
    st.info("Tip: keep allergy cards accessible during dining, especially in Paris and San Sebastián.")

# --- Main ---

def main() -> None:
    st.set_page_config(
        page_title=TRIP_TITLE,
        page_icon="🇫🇷",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar Navigation with custom branding
    st.sidebar.title("✈️ Honeymoon 2026")
    st.sidebar.divider()
    
    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Destinations", "Logistics", "Packing & Prep"],
        index=0
    )
    
    st.sidebar.divider()
    st.sidebar.info("Dates: July 19 – August 2")
    
    if page == "Overview":
        overview_page()
    elif page == "Destinations":
        destinations_page()
    elif page == "Logistics":
        logistics_page()
    elif page == "Packing & Prep":
        packing_page()

if __name__ == "__main__":
    main()
