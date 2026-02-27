import streamlit as st
import google.generativeai as genai
import PIL.Image
import pandas as pd
from io import BytesIO

# --- CONFIGURATIE ---
st.set_page_config(page_title="BonnetjeMaster Pro", layout="wide", page_icon="💰")

# --- UI DESIGN ---
st.title("🏆 BonnetjeMaster Pro")
st.markdown("""
    *Scan meerdere bonnetjes tegelijk, bereken BTW en exporteer naar Excel.*
    ---
""")

# --- ZIJBALK: HET VERDIENMODEL ---
with st.sidebar:
    st.header("🔑 Activatie")
    api_key = st.text_input("Voer je Gemini API Key in", type="password", help="Je kunt een gratis sleutel aanmaken bij Google AI Studio.")
    
    st.write("---")
    if not api_key:
        st.warning("⚠️ Voer een API-sleutel in om de scanner te activeren.")
        st.markdown("[Hoe kom ik aan een sleutel?](https://aistudio.google.com/app/apikey)")
    else:
        st.success("✅ Scanner is klaar voor gebruik!")
    
    st.write("---")
    st.header("⚙️ Export Instellingen")
    export_format = st.selectbox("Formaat", ["Excel (.xlsx)", "CSV (.csv)"])
    st.write("© 2026 BonnetjeMaster Business")

# --- HOOFDPROGRAMMA ---
# Controleer of er een sleutel is
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Bestanden uploaden
        uploaded_files = st.file_uploader(
            "Selecteer je bonnetjes (meerdere tegelijk mogelijk)", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            st.info(f"📍 {len(uploaded_files)} bestanden geselecteerd.")
            
            if st.button("🚀 Start Analyse & Bereken BTW"):
                all_data = []
                progress_bar = st.progress(0)
                
                for index, file in enumerate(uploaded_files):
                    st.write(f"Bezig met analyseren: **{file.name}**...")
                    img = PIL.Image.open(file)
                    
                    prompt = """
                    Analyseer dit bonnetje en geef de volgende gegevens terug in dit exacte formaat:
                    Winkel | Datum | Totaalbedrag | BTW_Bedrag | Categorie
                    
                    Geef alleen deze regel tekst terug, niets anders.
                    """
                    
                    try:
                        response = model.generate_content([prompt, img])
                        data_line = response.text.strip().split(" | ")
                        
                        if len(data_line) >= 4:
                            all_data.append({
                                "Bestand": file.name,
                                "Winkel": data_line[0],
                                "Datum": data_line[1],
                                "Totaal": data_line[2],
                                "BTW": data_line[3],
                                "Categorie": data_line[4] if len(data_line) > 4 else "Onbekend"
                            })
                    except Exception as e:
                        st.error(f"Fout bij {file.name}: {e}")
                    
                    progress_bar.progress((index + 1) / len(uploaded_files))

                if all_data:
                    st.write("---")
                    st.subheader("📊 Je Overzicht")
                    df = pd.DataFrame(all_data)
                    st.table(df)
                    
                    # Excel export
                    towrite = BytesIO()
                    df.to_excel(towrite, index=False, header=True)
                    towrite.seek(0)
                    st.download_button(
                        label="📥 Download Excel voor Boekhouding",
                        data=towrite,
                        file_name="mijn_bonnetjes.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                    st.balloons()
    except Exception as e:
        st.error("Er is iets mis met de API-sleutel. Controleer of deze correct is.")
else:
    st.info("👋 Welkom! Voer links je API-sleutel in om te beginnen met het scannen van je bonnetjes.")
