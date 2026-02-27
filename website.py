import streamlit as st
import google.generativeai as genai
import PIL.Image
import pandas as pd
from io import BytesIO

# --- CONFIGURATIE ---
st.set_page_config(page_title="BonnetjeMaster Pro",
                   layout="wide", page_icon="💰")

# --- JOUW API KEY (HIER PLAKKEN) ---
MY_SECRET_KEY = "AIzaSy..."  # <--- VERVANG DIT DOOR JOUW SLEUTEL
# ----------------------------------

# Initialiseer Gemini
if MY_SECRET_KEY != "AIzaSy...":
    genai.configure(api_key=MY_SECRET_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- UI DESIGN ---
st.title("🏆 BonnetjeMaster Pro")
st.markdown("""
    *Scan meerdere bonnetjes tegelijk, bereken BTW en exporteer direct naar Excel.*
    ---
""")

# Zijbalk voor instellingen
with st.sidebar:
    st.header("⚙️ Instellingen")
    st.info("De API-key is geladen uit de beveiligde instellingen.")
    export_format = st.selectbox(
        "Export formaat", ["Excel (.xlsx)", "CSV (.csv)"])
    st.write("---")
    st.write("© 2026 BonnetjeMaster Business")

# Bestanden uploaden
uploaded_files = st.file_uploader(
    "Selecteer je bonnetjes (meerdere tegelijk mogelijk)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} bestanden klaar voor analyse.")

    if st.button("🚀 Start Analyse & Bereken BTW"):
        all_data = []
        progress_bar = st.progress(0)

        for index, file in enumerate(uploaded_files):
            # Status update
            st.write(f"Bezig met analyseren: **{file.name}**...")

            # Afbeelding inladen
            img = PIL.Image.open(file)

            # Prompt voor de AI (Geld verdienen = details weten!)
            prompt = """
            Analyseer dit bonnetje en geef de volgende gegevens terug in dit exacte formaat:
            Winkel | Datum | Totaalbedrag | BTW_Bedrag | Categorie
            
            Voorbeeld: 
            Albert Heijn | 24-02-2024 | 15.50 | 1.28 | Boodschappen
            
            Geef alleen de tekst terug, geen extra uitleg.
            """

            try:
                response = model.generate_content([prompt, img])
                data_line = response.text.strip().split(" | ")

                if len(data_line) == 5:
                    all_data.append({
                        "Bestand": file.name,
                        "Winkel": data_line[0],
                        "Datum": data_line[1],
                        "Totaal": data_line[2],
                        "BTW": data_line[3],
                        "Categorie": data_line[4]
                    })
            except Exception as e:
                st.error(f"Foutje bij {file.name}: {e}")

            # Update voortgang
            progress_bar.progress((index + 1) / len(uploaded_files))

        # Resultaten tonen
        if all_data:
            st.write("---")
            st.subheader("📊 Overzicht resultaten")
            df = pd.DataFrame(all_data)
            st.table(df)

            # Excel export knop
            towrite = BytesIO()
            df.to_excel(towrite, index=False, header=True)
            towrite.seek(0)
            st.download_button(
                label="📥 Download Excel Export voor Boekhouder",
                data=towrite,
                file_name="bonnetjes_export.xlsx",
                mime="application/vnd.ms-excel"
            )
            st.balloons()
