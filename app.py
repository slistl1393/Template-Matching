import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")
st.title("📐 Symbolerkennung auf Bauplänen")

uploaded_json = st.file_uploader("Lade deine JSON-Erkennungsergebnisse hoch:", type=["json"])

if uploaded_json:
    data = json.load(uploaded_json)
    summary = data.get("summary", {})
    matches = data.get("matches", [])

    st.header("📊 Trefferanzahl pro Template")
    st.json(summary)

    df = pd.DataFrame(matches)
    st.header("📋 Alle erkannten Bauteile")
    st.dataframe(df)

    templates = list(summary.keys())
    selected_template = st.selectbox("🔍 Nur Treffer von:", options=templates)
    filtered_df = df[df["template"] == selected_template]
    st.write(f"{len(filtered_df)} Treffer für {selected_template}")
    st.dataframe(filtered_df)

    st.header("🖼 Planbild anzeigen")
    uploaded_img = st.file_uploader("Lade das Planbild hoch (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_img:
        file_bytes = np.asarray(bytearray(uploaded_img.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        for match in matches:
            if match["template"] != selected_template:
                continue
            x, y, w, h = match["bounding_box"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, match["template"], (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="Plan mit markierten Treffern", use_column_width=True)
