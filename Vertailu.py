import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd  # Uusi import taulukkoa varten

# ... [tässä kaikki aikaisemmat funktiot: laske_kustannukset_50v, laske_kaukolampo_kustannukset]

# [main() alkaa]
def main():
    st.title("Maalämpö vs Kaukolämpö – 50 vuoden vertailu (kaikki vaihtoehdot)")

    with st.sidebar:
        st.header("Perustiedot")
        investointi = st.number_input("Investoinnin suuruus (€)", value=650000.0)
        omaisuuden_myynti = st.number_input("Omaisuuden myyntitulo (€)", value=100000.0)
        investointi_laina_aika = st.slider("Investointilainan maksuaika (vuotta)", 5, 40, value=20)
        korko = st.number_input("Lainan korko (% / vuosi)", value=3.0)
        sahkon_hinta = st.number_input("Sähkön hinta (€/kWh)", value=0.12)
        sahkon_inflaatio = st.number_input("Sähkön hinnan nousu (% / vuosi)", value=2.0)
        sahkon_kulutus = st.number_input("Maalämmön sähkönkulutus (kWh/v)", value=180000.0)
        kaukolampo_kustannus = st.number_input("Kaukolämmön vuosikustannus (€)", value=85000.0)
        kaukolampo_inflaatio = st.number_input("Kaukolämmön hinnan nousu (% / vuosi)", value=2.0)
        menetetty_kassavirta_kk = st.number_input("Menetetyn omaisuuden kassavirta (€ / kk)", value=0.0)
        maksavat_neliot = st.number_input("Maksavat neliöt (m²)", value=1000.0)

        st.header("Korjaukset")
        korjaus_vali = st.slider("Korjausväli (vuotta)", 5, 30, value=15)
        korjaus_hinta = st.number_input("Yksittäisen korjauksen hinta (€)", value=20000.0)
        korjaus_laina_aika = st.slider("Korjauslainan maksuaika (vuotta)", 1, 30, value=10)

    vuodet = list(range(1, 51))

    kaukolampo = laske_kaukolampo_kustannukset(kaukolampo_kustannus, kaukolampo_inflaatio)

    maalampo_ilman = laske_kustannukset_50v(
        investointi, 0, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio
    )

    maalampo_myynnilla = laske_kustannukset_50v(
        investointi, omaisuuden_myynti, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio
    )

    # Menetetty kassavirta
    kassavirta_vuosi = menetetty_kassavirta_kk * 12
    kassavirrat = [kassavirta_vuosi] * 50
    maalampo_myynnilla = [m + k for m, k in zip(maalampo_myynnilla, kassavirrat)]

    # Kaavio
    fig, ax = plt.subplots()
    ax.plot(vuodet, kaukolampo, label="Kaukolämpö", linestyle="--")
    ax.plot(vuodet, maalampo_ilman, label="Maalämpö (ilman myyntiä)")
    ax.plot(vuodet, maalampo_myynnilla, label="Maalämpö (myynnillä + kassavirta)")
    ax.set_title("Lämmityskustannukset 50 vuoden ajalla")
    ax.set_xlabel("Vuosi")
    ax.set_ylabel("Kustannus (€)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Ensimmäisen vuoden vastikevertailu
    st.markdown("### Ensimmäisen vuoden vastikevertailu per m²")

    def laske_vastike(kustannus_lista, neliot):
        vuosikustannus = kustannus_lista[0]
        per_m2_vuosi = vuosikustannus / neliot
        per_m2_kk = per_m2_vuosi / 12
        return per_m2_vuosi, per_m2_kk

    kaukolampo_vuosi, kaukolampo_kk = laske_vastike(kaukolampo, maksavat_neliot)
    maalampo_ilman_vuosi, maalampo_ilman_kk = laske_vastike(maalampo_ilman, maksavat_neliot)
    maalampo_myynnilla_vuosi, maalampo_myynnilla_kk = laske_vastike(maalampo_myynnilla, maksavat_neliot)

    st.markdown(f"**Kaukolämpö:** {kaukolampo_vuosi:.2f} €/m²/v | {kaukolampo_kk:.2f} €/m²/kk")
    st.markdown(f"**Maalämpö ilman omaisuuden myyntiä:** {maalampo_ilman_vuosi:.2f} €/m²/v | {maalampo_ilman_kk:.2f} €/m²/kk")
    st.markdown(f"**Maalämpö omaisuuden myynnillä:** {maalampo_myynnilla_vuosi:.2f} €/m²/v | {maalampo_myynnilla_kk:.2f} €/m²/kk")

    st.markdown("---")
    st.markdown(f"**Erotus (kaukolämpö vs ilman myyntiä): {kaukolampo_vuosi - maalampo_ilman_vuosi:.2f} €/m²/v**")
    st.markdown(f"**Erotus (kaukolämpö vs myynnillä): {kaukolampo_vuosi - maalampo_myynnilla_vuosi:.2f} €/m²/v**")

    # Vastiketaulukko 5 vuoden välein
    st.markdown("### Vastikkeet 5 vuoden välein (€ / m² / kk)")

    data = {
        "Vuosi": [],
        "Kaukolämpö": [],
        "Maalämpö ilman myyntiä": [],
        "Maalämpö myynnillä": []
    }

    for vuosi in range(5, 51, 5):
        idx = vuosi - 1
        k = kaukolampo[idx] / maksavat_neliot / 12
        m1 = maalampo_ilman[idx] / maksavat_neliot / 12
        m2 = maalampo_myynnilla[idx] / maksavat_neliot / 12

        data["Vuosi"].append(vuosi)
        data["Kaukolämpö"].append(f"{k:.2f}")
        data["Maalämpö ilman myyntiä"].append(f"{m1:.2f}")
        data["Maalämpö myynnillä"].append(f"{m2:.2f}")

    df = pd.DataFrame(data)
    st.table(df)

if __name__ == "__main__":
    main()
