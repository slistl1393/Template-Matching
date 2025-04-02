import streamlit as st
import json
import os
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import plotly.express as px

# --- GitHub-Daten laden ---
@st.cache_data
def load_all_matches_from_github(repo="slistl1393/Template-Matching", folder="json_output", branch="main"):
    url = f"https://api.github.com/repos/{repo}/contents/{folder}?ref={branch}"
    files = requests.get(url).json()

    all_data = []
    for file in files:
        if file["name"].endswith(".json"):
            content = requests.get(file["download_url"]).json()
            all_data.append(content)
    return all_data

@st.cache_data
def load_bauteil_infos(info_file_url="https://raw.githubusercontent.com/slistl1393/Template-Matching/main/bauteil_info.json"):
    try:
        response = requests.get(info_file_url)
        return response.json()
    except:
        return {}

@st.cache_data
def load_plan_image_from_github(url="https://raw.githubusercontent.com/slistl1393/Template-Matching/main/plan_image.png"):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# --- Visualisierung der Treffer auf dem Plan ---
def visualize_matches_on_plan(matches):
    if not matches:
        st.info("Keine Treffer gefunden.")
        return

    df = pd.DataFrame([
        {
            "x": m["position"]["x"],
            "y": m["position"]["y"],
            "bauteil": m.get("bauteil", "Unbekannt"),
            "template": m["template"]
        } for m in matches
    ])

    fig = px.scatter(
        df, x="x", y="y", color="bauteil", hover_data=["template"],
        title="📍 Treffer auf dem Gesamtplan", width=1200, height=800
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

# --- Streamlit App ---
st.set_page_config(page_title="Bauteilerkennung", layout="wide")
st.title("🔍 Bauteilerkennung und Auswertung")

bauteil_infos = load_bauteil_infos()
all_templates = load_all_matches_from_github()

st.header("📦 Übersicht erkannter Bauteile")

if not all_templates:
    st.warning("⚠️ Keine JSON-Daten gefunden. Stelle sicher, dass GitHub-Repo korrekt befüllt ist.")
else:
    for template in all_templates:
        bauteil = template.get("bauteil", "Unbekannt")
        count = template.get("count", len(template.get("matches", [])))

        with st.expander(f"{bauteil} ({count}x erkannt)"):
            info = bauteil_infos.get(bauteil, {})
            st.write(f"**🔹 Preis:** {info.get('preis', 'Keine Angabe')}")
            st.write(f"**🔹 Maße:** {info.get('maße', 'Keine Angabe')}")
            st.write(f"**🔹 Alternativen:** {', '.join(info.get('alternativen', [])) or 'Keine'}")
            st.write(f"**🔹 Info:** {info.get('info', '')}")

            st.markdown("---")
            st.subheader("📍 Trefferpositionen:")
            st.json(template.get("matches", []))

# --- Bildanzeige und Treffer ---
st.header("🗺️ Treffer auf Gesamtplan")
image = load_plan_image_from_github()
st.image(image, caption="Gesamtplan (Ausschnitt)", use_column_width=True)

# --- Zoombare Plotly-Karte ---
all_matches = [m for t in all_templates for m in t.get("matches", [])]
visualize_matches_on_plan(all_matches)

st.success("✅ Daten erfolgreich geladen und visualisiert.")
