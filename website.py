import streamlit as st
import google.generativeai as genai
import PIL.Image
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="BonnetjeMaster Pro", layout="wide")
st.title("BonnetjeMaster Pro")

with st.sidebar:
    st.header("Activatie")
    api_key = st.text_input("Voer je Gemini API Key in", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)

        # We gebruiken hier de meest standaard naamgeving
        model = genai.GenerativeModel('gemini-1.5-flash')

        uploaded_files = st.file_uploader(
            "Upload je bonnetjes", accept_multiple_files=True)

        if uploaded_files and st.button("Start Analyse"):
            all_data = []
            for file in uploaded_files:
                st.write(f"Bezig met: {file.name}...")
                try:
                    img = PIL.Image.open(file)
                    prompt = "Geef alleen: Winkel | Datum | Totaalbedrag | BTW_Bedrag | Categorie"
                    response = model.generate_content([prompt, img])
                    res_text = response.text.strip()
                    parts = res_text.split(" | ")

                    if len(parts) >= 4:
                        all_data.append({
                            "Bestand": file.name,
                            "Winkel": parts[0],
                            "Datum": parts[1],
                            "Totaal": parts[2],
                            "BTW": parts[3],
                            "Categorie": parts[4] if len(parts) > 4 else "Diversen"
                        })
                except Exception as e:
                    st.error(f"Fout bij {file.name}: {e}")

            if all_data:
                df = pd.DataFrame(all_data)
                st.table(df)

                output = BytesIO()
                df.to_excel(output, index=False)
                st.download_button(
                    "Download Excel", data=output.getvalue(), file_name="export.xlsx")

    except Exception as e:
        st.error(f"Configuratiefout: {e}")
else:
    st.warning("Voer eerst je API-sleutel in de zijbalk in.")
