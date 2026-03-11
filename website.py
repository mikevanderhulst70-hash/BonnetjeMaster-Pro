import streamlit as st
import google.generativeai as genai
import PIL.Image
import pandas as pd
from io import BytesIO

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="BonnetjeMaster Pro",
                   layout="wide", page_icon="💰")

# --- 2. INTERFACE ---
st.title("🏆 BonnetjeMaster Pro")
st.markdown("Zet je bonnetjes om in een professioneel Excel-overzicht.")

# Zijbalk voor de API-sleutel (Jouw verdienmodel: de klant gebruikt zijn eigen sleutel)
with st.sidebar:
    st.header("🔑 Activatie")
    api_key = st.text_input("Voer je Gemini API Key in", type="password")
    st.info("Geen sleutel? Haal hem gratis op bij: aistudio.google.com")
    st.write("---")
    st.write("© 2026 BonnetjeMaster Business")

# --- 3. LOGICA ---
if api_key:
    try:
        # Initialiseer de AI met de ingevulde sleutel
        genai.configure(api_key=api_key)

        # Gebruik de meest stabiele modelnaam om 404-fouten te voorkomen
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Bestanden uploaden
        uploaded_files = st.file_uploader(
            "Upload je bonnetjes (JPG of PNG)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} bestanden geladen.")

            if st.button(" Start de Analyse"):
                all_data = []
                progress_bar = st.progress(0)

                for index, file in enumerate(uploaded_files):
                    st.write(f"Bezig met scannen: **{file.name}**...")

                    try:
                        img = PIL.Image.open(file)

                        # De prompt die de AI vertelt wat hij moet doen
                        prompt = "Extraheer de volgende info van dit bonnetje: Winkel | Datum | Totaalbedrag | BTW_Bedrag | Categorie. Geef alleen deze regel terug, gescheiden door verticale streepjes."

                        # AI aanroepen
                        response = model.generate_content([prompt, img])
                        res_text = response.text.strip()

                        # Gegevens splitsen naar kolommen
                        parts = res_text.split(" | ")
                        if len(parts) >= 4:
                            all_data.append({
                                "Bestand": file.name,
                                "Winkel": parts[0],
                                "Datum": parts[1],
                                "Totaal": parts[2],
                                "BTW": parts[3],
                                "Categorie": parts[4] if len(parts) > 4 else "Algemeen"
                            })
                    except Exception as e:
                        st.error(f"Fout bij {file.name}: {str(e)}")

                    # Voortgang bijwerken
                    progress_bar.progress((index + 1) / len(uploaded_files))

                # Resultaten tonen als er data is
                if all_data:
                    st.write("---")
                    st.subheader(" Resultaten")
                    df = pd.DataFrame(all_data)
                    st.dataframe(df, use_container_width=True)

                    # Excel export maken
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False,
                                    sheet_name='Bonnetjes')

                    st.download_button(
                        label=" Download Excel Bestand",
                        data=output.getvalue(),
                        file_name="bonnetjes_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.balloons()

    except Exception as e:
        st.error(f"Er is een probleem met de verbinding: {e}")
else:
    # Dit ziet de gebruiker als hij nog geen sleutel heeft ingevuld
    st.warning(
        " Voer eerst je API-sleutel in de zijbalk in om de scanner te activeren.")
