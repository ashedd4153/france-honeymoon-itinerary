from __future__ import annotations

from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent

LOCATIONS = [
    {
        "name": "Fly Out",
        "dates": "July 19",
        "days": 0,
        "emoji": "🟥",
        "summary": "Sunday evening departure from Newark; wake up in Paris.",
        "file": "flight-planning.md",
    },
    {
        "name": "Paris",
        "dates": "July 20–24",
        "days": 5,
        "emoji": "🟩",
        "summary": "Art museums, picnics, rooftop drinks, and dairy-conscious dining.",
        "file": "paris.md",
    },
    {
        "name": "Bordeaux",
        "dates": "July 25–26",
        "days": 2,
        "emoji": "🟦",
        "summary": "Wine capital of France – tastings, riverfront strolls, Saint-Émilion.",
        "file": "bordeaux.md",
    },
    {
        "name": "Saint-Jean-de-Luz",
        "dates": "July 27–28",
        "days": 2,
        "emoji": "🟨",
        "summary": "Romantic French Basque fishing village – harbor, seafood, tranquility.",
        "file": "saint-jean-de-luz.md",
    },
    {
        "name": "San Sebastián",
        "dates": "July 29–Aug 1",
        "days": 4,
        "emoji": "🟪",
        "summary": "Pintxos crawls, Michelin dining, Basque culture, Old Town charm.",
        "file": "san-sebastian.md",
    },
    {
        "name": "Fly Home",
        "dates": "August 2",
        "days": 0,
        "emoji": "🟧",
        "summary": "Sunday departure from Bilbao; optional Guggenheim stop.",
        "file": "flight-planning.md",
    },
]

PLANNING_DOCS = {
    "Flight Planning": "flight-planning.md",
    "Train Planning": "train-planning.md",
    "Packing List": "packing-list.md",
}

CALENDAR_TABLE = """| Sun | Mon | Tue | Wed | Thu | Fri | Sat |
|-----|-----|-----|-----|-----|-----|-----|
|     |     |     | 1   | 2   | 3   | 4   |
| 5   | 6   | 7   | 8   | 9   | 10  | 11  |
| 12  | 13  | 14  | 15  | 16  | 17  | 18  |
| 🟥19 | 🟩20 | 🟩21 | 🟩22 | 🟩23 | 🟩24 | 🟦25 |
| 🟦26 | 🟨27 | 🟨28 | 🟪29 | 🟪30 | 🟪31 | 🟪1 |
| 🟧2 | 3   | 4   | 5   | 6   | 7   | 8   |
"""


import re

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
    # Split content by image markdown syntax
    pattern = r'!\[(.*?)\]\((.*?)\)'
    parts = re.split(pattern, content)
    
    i = 0
    while i < len(parts):
        if i + 2 < len(parts):
            # Check if this could be an image pattern by looking ahead
            text_before = parts[i]
            if text_before.strip():
                st.markdown(text_before)
            
            # Check if next parts look like alt text and path
            potential_alt = parts[i + 1] if i + 1 < len(parts) else ""
            potential_path = parts[i + 2] if i + 2 < len(parts) else ""
            
            # If the path looks like an image file
            if potential_path and potential_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                img_path = BASE_DIR / potential_path
                if img_path.exists():
                    st.image(str(img_path), caption=potential_alt, use_container_width=True)
                else:
                    st.warning(f"Image not found: {potential_path}")
                i += 3
            else:
                i += 1
        else:
            # Remaining text
            if parts[i].strip():
                st.markdown(parts[i])
            i += 1


def render_location_details(location: dict[str, str]) -> None:
    st.subheader(f"{location['emoji']} {location['name']} · {location['dates']}")
    summary = location.get("summary")
    if summary:
        st.write(summary)
    content = load_markdown(location["file"], drop_title=True)
    render_markdown_with_images(content)


def render_planning_section(title: str, relative_path: str) -> None:
    st.markdown(f"### {title}")
    st.markdown(load_markdown(relative_path, drop_title=False))


def overview_page() -> None:
    st.title("France & Basque Country Honeymoon")
    st.caption("July 19 – August 2, 2026")

    col1, col2, col3 = st.columns(3)
    col1.metric("Trip Length", "14 days")
    col2.metric("Destinations", "4 cities")
    col3.metric("Travel Style", "Trains + Flights")

    st.markdown("### Timeline Snapshot")
    st.markdown(CALENDAR_TABLE)
    st.caption("*Colors show where you're sleeping that night*")

    st.markdown("### Segments")
    for loc in LOCATIONS:
        if loc['days'] > 0:
            st.write(f"{loc['emoji']} **{loc['name']}** – {loc['dates']} ({loc['days']} nights)")
        else:
            st.write(f"{loc['emoji']} **{loc['name']}** – {loc['dates']}")

    st.markdown(
        "[View all locations on Google Maps]"
        "(https://www.google.com/maps/dir/Paris,+France/Bordeaux,+France/Saint-Jean-de-Luz,+France/San+Sebastian,+Spain/Bilbao,+Spain)"
    )

    st.markdown("### Planning Tools")
    st.markdown(
        "- [Train Planning](train-planning.md)\n"
        "- [Packing List](packing-list.md)\n"
        "- [Flight Planning](flight-planning.md)"
    )


def destinations_page() -> None:
    st.title("Destination Details")
    # Filter to actual destinations (not fly out/home)
    destinations = [loc for loc in LOCATIONS if loc["days"] > 0]
    selected_name = st.selectbox(
        "Choose a segment to explore",
        [f"{loc['name']} ({loc['dates']})" for loc in destinations],
    )
    selected = next(
        loc
        for loc in destinations
        if loc["name"] in selected_name
    )
    render_location_details(selected)

    with st.expander("See all destination notes"):
        for loc in destinations:
            render_location_details(loc)
            st.divider()


def logistics_page() -> None:
    st.title("Flights & Train Logistics")
    flights_tab, trains_tab = st.tabs(["Flights", "Trains"])
    with flights_tab:
        render_planning_section("Flight Planning", PLANNING_DOCS["Flight Planning"])
    with trains_tab:
        render_planning_section("Train Planning", PLANNING_DOCS["Train Planning"])


def packing_page() -> None:
    st.title("Packing & Prep")
    render_planning_section("Packing Checklist", PLANNING_DOCS["Packing List"])
    st.info(
        "Tip: keep allergy cards accessible during dining, especially in Paris and San Sebastián."
    )


def main() -> None:
    st.set_page_config(
        page_title="Honeymoon Dashboard", page_icon="🇫🇷", layout="wide"
    )
    page = st.sidebar.radio(
        "Navigate",
        ("Overview", "Destinations", "Flights & Transport", "Packing & Notes"),
    )
    if page == "Overview":
        overview_page()
    elif page == "Destinations":
        destinations_page()
    elif page == "Flights & Transport":
        logistics_page()
    else:
        packing_page()


if __name__ == "__main__":
    main()
