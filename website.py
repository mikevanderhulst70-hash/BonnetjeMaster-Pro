import streamlit as st
import google.generativeai as genai
import PIL.Image
import pandas as pd
from io import BytesIO

# --- CONFIGURATIE ---
st.set_page_config(page_title="BonnetjeMaster Pro", layout="wide")

st.title("🏆 BonnetjeMaster Pro")

# --- ZIJBALK ---
with st.sidebar:
    st.header("🔑 Activatie")
    api_key = st.text_input("Voer je Gemini API Key in", type="password")
    st.info("Haal je sleutel op via: aistudio.google.com")

# --- HIER GEBEURT HET ---
if api_key:
    try:
        # Initialiseer de AI DIRECT nadat de sleutel is ingevoerd
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        uploaded_files = st.file_uploader("Upload je bonnetjes", type=[
                                          "jpg", "jpeg", "png"], accept_multiple_files=True)

        if uploaded_files and st.button("🚀 Start Analyse"):
            all_data = []
            progress_bar = st.progress(0)

            for index, file in enumerate(uploaded_files):
                st.write(f"Bezig met: {file.name}...")
                img = PIL.Image.open(file)

                # De opdracht aan de AI
                prompt = "Winkel | Datum | Totaalbedrag | BTW_Bedrag | Categorie. Geef alleen deze regel."

                try:
                    # Hier gebruiken we 'model' die hierboven is gedefinieerd
                    response = model.generate_content([prompt, img])
                    data_line = response.text.strip().split(" | ")

                    if len(data_line) >= 4:
                        all_data.append({
                            "Bestand": file.name,
                            "Winkel": data_line[0],
                            "Datum": data_line[1],
                            "Totaal": data_line[2],
                            "BTW": data_line[3],
                            "Categorie": data_line[4] if len(data_line) > 4 else "Diversen"
                        })
                except Exception as e:
                    st.error(f"Fout bij {file.name}: {e}")

                progress_bar.progress((index + 1) / len(uploaded_files))

            if all_data:
                df = pd.DataFrame(all_data)
                st.table(df)

                # Excel knop
                towrite = BytesIO()
                df.to_excel(towrite, index=False)
                towrite.seek(0)
                st.download_button("📥 Download Excel",
                                   data=towrite, file_name="export.xlsx")
                st.balloons()

    except Exception as e:
        st.error(f"Sleutel fout: {e}")
else:
    st.warning("👈 Vul eerst je API-sleutel in de zijbalk in om te beginnen.")
