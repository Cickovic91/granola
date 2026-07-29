import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Postavke stranice
st.set_page_config(page_title="Granola Art Studio", layout="wide")


# --- SIGURNOST (BRAVA) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input(
            "Unesite pristupnu šifru studija",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    return st.session_state["password_correct"]


def password_entered():
    if st.session_state["password"] == "granola2024":  # OVDE PROMENI ŠIFRU U SVOJU
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.error("Pogrešna šifra!")


if not check_password():
    st.stop()

# --- POVEZIVANJE SA BAZOM ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Čitamo oba lista
df_magacin = conn.read(worksheet="Magacin")
df_recepti = conn.read(worksheet="Recepti")

# Čišćenje kolona (uklanja skrivene razmake ako postoje)
df_magacin.columns = df_magacin.columns.str.strip()
if not df_recepti.empty:
    df_recepti.columns = df_recepti.columns.str.strip()

st.title("🎨 Granola Art - Upravljanje")

# --- SIDEBAR NAVIGACIJA ---
page = st.sidebar.radio(
    "Meni", ["Magacin", "Recepti", "Kalkulator Proizvodnje", "Statistika"]
)

if page == "Magacin":
    st.header("📦 Stanje Sirovina i Ambalaže")
    st.dataframe(df_magacin, use_container_width=True)

    with st.expander("Dodaj novu stavku"):
        with st.form("new_item"):
            naziv = st.text_input("Naziv")
            kat = st.selectbox("Kategorija", ["Sastojak", "Ambalaža", "Dodatak"])
            cena = st.number_input("Cena pakovanja (RSD)", min_value=0.0)
            grama = st.number_input("Gramaža/Komada u pakovanju", min_value=1.0)
            if st.form_submit_button("Sačuvaj"):
                jed_cena = cena / grama
                new_row = pd.DataFrame(
                    [
                        {
                            "Sirovina": naziv,
                            "Kategorija": kat,
                            "Cena pakovanja": cena,
                            "Kolicina": grama,
                            "Cena po jedinici": jed_cena,
                        }
                    ]
                )
                updated_df = pd.concat([df_magacin, new_row], ignore_index=True)
                conn.update(worksheet="Magacin", data=updated_df)
                st.success("Sačuvano!")
                st.rerun()

elif page == "Recepti":
    st.header("🥣 Knjiga Recepata")

    # Prikaz postojećih recepata
    if not df_recepti.empty:
        st.subheader("Vaši recepti")
        st.dataframe(df_recepti, use_container_width=True)

    with st.expander("➕ Kreiraj novi recept"):
        recept_ime = st.text_input("Naziv novog recepta (npr. Granola Badem-Med)")

        # Biranje sastojaka iz Magacina
        sastojci_opcije = df_magacin[df_magacin["Kategorija"] == "Sastojak"][
            "Sirovina"
        ].tolist()
        izabrani_sastojci = st.multiselect(
            "Izaberi sastojke iz magacina", sastojci_opcije
        )

        if izabrani_sastojci:
            temp_list = []
            ukupni_trosak_sirovina = 0

            for s in izabrani_sastojci:
                col1, col2 = st.columns(2)
                with col1:
                    grami = st.number_input(f"Gramaža za {s}", min_value=0.0, key=s)

                # Matematika: Uzimamo cenu iz Magacina
                cena_po_g = df_magacin[df_magacin["Sirovina"] == s][
                    "Cena po jedinici"
                ].values[0]
                trosak_stavke = grami * cena_po_g
                ukupni_trosak_sirovina += trosak_stavke
                temp_list.append(
                    {"Naziv Recepta": recept_ime, "Sastojak": s, "Kolicina_g": grami}
                )

            # --- KALO FAKTOR (0.9) ---
            ukupna_gramaza = sum([item["Kolicina_g"] for item in temp_list])
            pecena_gramaza = ukupna_gramaza * 0.9

            st.divider()
            st.write(f"⚖️ Ukupna sirova težina: **{ukupna_gramaza:.0f}g**")
            st.write(
                f"🔥 Očekivana težina nakon pečenja (Kalo 0.9): **{pecena_gramaza:.0f}g**"
            )
            st.write(
                f"💰 Ukupan trošak sirovina: **USD {ukupni_trosak_sirovina:.2f}**"
            )  # Koristim USD po instrukcijama

            if st.button("Sačuvaj Recept"):
                new_recept_df = pd.concat(
                    [df_recepti, pd.DataFrame(temp_list)], ignore_index=True
                )
                conn.update(worksheet="Recepti", data=new_recept_df)
                st.success(f"Recept '{recept_ime}' je uspešno sačuvan!")
                st.rerun()

elif page == "Kalkulator Proizvodnje":
    st.header("🚜 Kalkulator Ture")
    st.write(
        "Ovde ćemo sutra dodati opciju da izabereš recept i kažeš 'Treba mi 10 tegli', a on ti izbaci šoping listu."
    )
