import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def laske_kaukolampo_kustannukset(kustannus, inflaatio):
    nykyinen = kustannus
    tulos = []
    for _ in range(50):
        tulos.append(nykyinen)
        nykyinen *= (1 + inflaatio / 100)
    return tulos

def laske_kustannukset_50v(investointi, omaisuuden_myynti, investointi_laina_aika, korko,
                            sahkon_hinta, sahkon_kulutus_kwh,
                            korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio,
                            maksavat_neliot):
    vuodet = 50
    lainan_maara = investointi - omaisuuden_myynti
    lyhennys = lainan_maara / investointi_laina_aika
    jaljella_oleva_laina = lainan_maara
    sahkon_hinta_vuosi = sahkon_hinta

    kokonais_kustannukset = []
    korjaus_kustannukset = []
    korjauslainat = []

    for vuosi in range(1, vuodet + 1):
        if vuosi <= investointi_laina_aika:
            lyh = lyhennys
            korko_investointi = jaljella_oleva_laina * (korko / 100)
            jaljella_oleva_laina -= lyh
        else:
            lyh = 0
            korko_investointi = 0

        sahkolasku = sahkon_hinta_vuosi * sahkon_kulutus_kwh

        if vuosi > 1 and (vuosi - 1) % korjaus_vali == 0:
            uusi_korjaus = {
                "jaljella": korjaus_hinta,
                "lyhennys": korjaus_hinta / korjaus_laina_aika,
                "vuosia_jaljella": korjaus_laina_aika
            }
            korjauslainat.append(uusi_korjaus)

        korjaus_korko_yht = 0
        korjaus_lyhennys_yht = 0
        for laina in korjauslainat:
            if laina["vuosia_jaljella"] > 0:
                korko_tama = laina["jaljella"] * (korko / 100)
                korjaus_korko_yht += korko_tama
                korjaus_lyhennys_yht += laina["lyhennys"]
                laina["jaljella"] -= laina["lyhennys"]
                laina["vuosia_jaljella"] -= 1

        korjauslainat = [l for l in korjauslainat if l["vuosia_jaljella"] > 0]

        kokonais = lyh + korko_investointi + sahkolasku + korjaus_lyhennys_yht + korjaus_korko_yht
        kokonais_kustannukset.append(kokonais)
        korjaus_kustannukset.append(korjaus_lyhennys_yht + korjaus_korko_yht)

        sahkon_hinta_vuosi *= (1 + sahkon_inflaatio / 100)

    return kokonais_kustannukset, korjaus_kustannukset

def main():
    st.title("Maalämpö vs Kaukolämpö – 50 vuoden vertailu")

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
        korjaus_hinta = st.number_input("Korjauksen hinta (€)", value=20000.0)
        korjaus_laina_aika = st.slider("Korjauslainan maksuaika (vuotta)", 1, 30, value=10)

    vuodet = list(range(1, 51))

    kaukolampo = laske_kaukolampo_kustannukset(kaukolampo_kustannus, kaukolampo_inflaatio)

    ml_ilman, korjaukset_ilman = laske_kustannukset_50v(
        investointi, 0, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio,
        maksavat_neliot
    )

    ml_myynnilla, korjaukset_myynnilla = laske_kustannukset_50v(
        investointi, omaisuuden_myynti, investointi_laina_aika, korko,
        sahkon_hinta, sahkon_kulutus,
        korjaus_vali, korjaus_hinta, korjaus_laina_aika, sahkon_inflaatio,
        maksavat_neliot
    )

    kassavirta_vuosi = menetetty_kassavirta_kk * 12
    ml_myynnilla = [m + kassavirta_vuosi for m in ml_myynnilla]

    # KUSTANNUSKÄYRÄ
    fig1, ax1 = plt.subplots()
    ax1.plot(vuodet, kaukolampo, label="Kaukolämpö", linestyle="--")
    ax1.plot(vuodet, ml_ilman, label="Maalämpö ilman myyntiä")
    ax1.plot(vuodet, ml_myynnilla, label="Maalämpö myynnillä + kassavirta")
    ax1.set_title("Kokonaiskustannukset 50 vuoden ajalla")
    ax1.set_xlabel("Vuosi")
    ax1.set_ylabel("Kustannus (€)")
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    # VASTIKEKÄYRÄ
    vastike_ilman = [v / maksavat_neliot / 12 for v in ml_ilman]
    vastike_myynnilla = [v / maksavat_neliot / 12 for v in ml_myynnilla]
    korjausvastike = [v / maksavat_neliot / 12 for v in korjaukset_ilman]

    fig2, ax2 = plt.subplots()
    ax2.plot(vuodet, vastike_ilman, label="Maalämpö ilman myyntiä")
    ax2.plot(vuodet, vastike_myynnilla, label="Maalämpö myynnillä")
    ax2.plot(vuodet, korjausvastike, label="Minimivastike korjauksille", linestyle="--")
    ax2.set_title("Vastikkeet 50 vuoden ajalla (€ / m² / kk)")
    ax2.set_xlabel("Vuosi")
    ax2.set_ylabel("Vastike (€ / m² / kk)")
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

if __name__ == "__main__":
    main()
