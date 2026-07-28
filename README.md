import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Granola Art Studio", layout="wide")

st.title("🎨 Granola Art - Upravljanje")

# Povezivanje sa Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Čitanje podataka iz tabele Magacin
df = conn.read(worksheet="Magacin")

# --- SIDEBAR ---
page = st.sidebar.radio("Meni", ["Magacin", "Recepti", "Prodaja"])

if page == "Magacin":
    st.header("📦 Stanje Sirovina")
    
    # Prikaz tabele
    st.dataframe(df, use_container_width=True)
    
    # Formular za unos
    with st.expander("Dodaj novu sirovinu"):
        with st.form("new_entry"):
            naziv = st.text_input("Naziv")
            kat = st.selectbox("Kategorija", ["Sastojak", "Ambalaža", "Dodatak"])
            cena = st.number_input("Cena (RSD)", min_value=0.0)
            grama = st.number_input("Gramaža/Komada", min_value=1.0)
            
            if st.form_submit_button("Sačuvaj"):
                jed_cena = cena / grama
                new_row = pd.DataFrame([{
                    "Sirovina": naziv,
                    "Kategorija": kat,
                    "Cena pakovanja": cena,
                    "Kolicina": grama,
                    "Cena po jedinici": jed_cena
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # Slanje podataka nazad na Google Sheets
                conn.update(worksheet="Magacin", data=updated_df)
                st.success("Uspešno sačuvano na Google Drive!")
                st.rerun()

elif page == "Recepti":
    st.header("🥣 Recepti i Kalkulacija (Kalo 0.9)")
    st.info("Ovde ćemo u sledećem koraku povezati Magacin sa receptima.")
