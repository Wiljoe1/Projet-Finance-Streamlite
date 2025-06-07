import streamlit as st
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText


def generate_signals(df):
    signals = []
    for i in range(1, len(df)):
        buy = (
            (df["MACD"].iloc[i - 1] < df["Signal_Line"].iloc[i - 1])
            and (df["MACD"].iloc[i] > df["Signal_Line"].iloc[i])
            and (df["RSI_14"].iloc[i] < 70)
            and (df["close"].iloc[i] > df["SMA_20"].iloc[i])
        )
        sell = (
            (df["MACD"].iloc[i - 1] > df["Signal_Line"].iloc[i - 1])
            and (df["MACD"].iloc[i] < df["Signal_Line"].iloc[i])
            and (df["RSI_14"].iloc[i] > 30)
            and (df["close"].iloc[i] < df["SMA_20"].iloc[i])
        )
        if buy:
            signals.append("Buy")
        elif sell:
            signals.append("Sell")
        else:
            signals.append("")
    signals = [""] + signals
    df["Signal"] = signals
    return df


def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, password):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)


def app():
    st.title("⚡ Automatisation & Trading")
    st.markdown(
        """
***Définir les règles de signaux***

**Achat (Buy) :**

MACD croise au-dessus de la ligne signal ET RSI < 70 ET cours au-dessus de SMA 20

**Vente (Sell) :**

MACD croise sous la ligne signal ET RSI > 30 ET cours sous SMA 20
"""
    )

    # -- Charger les données
    api_key = "89VPC1UGYMZL10S4"
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&outputsize=full&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    time_series = data.get("Time Series FX (Daily)", {})
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.columns = ["open", "high", "low", "close"]
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.reset_index(inplace=True)
    df.rename(columns={"index": "date"}, inplace=True)
    df["close"] = df["close"].astype(float)

    # -- Calcul des indicateurs
    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["EMA_20"] = df["close"].ewm(span=20, adjust=False).mean()

    # RSI
    def calculate_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    df["RSI_14"] = calculate_rsi(df["close"])
    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # -- Générer les signaux
    df = generate_signals(df)
    dernier_signal = df.iloc[-1]["Signal"]

    if dernier_signal in ["Buy", "Sell"]:
        st.success(f"**Dernier signal détecté : {dernier_signal}**")
        st.write(
            f"""
- **Date :** {df.iloc[-1]['date']}
- **Prix de clôture :** {df.iloc[-1]['close']}
- **RSI 14 :** {df.iloc[-1]['RSI_14']:.2f}
- **SMA 20 :** {df.iloc[-1]['SMA_20']:.5f}
- **MACD :** {df.iloc[-1]['MACD']:.5f}
- **Signal Line :** {df.iloc[-1]['Signal_Line']:.5f}
"""
        )

        # -- Option d'envoi d'alerte email 

        # ------- Paramètres de l'expéditeur -------
        expediteur = "wiljoe125@gmail.com"
        mot_de_passe = "Wilson.12345@"  # <-- MOT DE PASSE DE L'EXPEDITEUR EN DUR

        # ------- Saisie de l'email du destinataire -------
        destinataire = st.text_input("Entrez l'adresse email du destinataire :")

        sujet = f"ALERTE TRADING EUR/USD : Signal {dernier_signal}"
        corps = (
            f"Un signal {dernier_signal} a été détecté sur EUR/USD.\n"
            f"Date : {df.iloc[-1]['date']}\n"
            f"Prix de clôture : {df.iloc[-1]['close']}\n"
            f"RSI 14 : {df.iloc[-1]['RSI_14']:.2f}\n"
            f"SMA 20 : {df.iloc[-1]['SMA_20']:.5f}\n"
            f"MACD : {df.iloc[-1]['MACD']:.5f}\n"
            f"Signal Line : {df.iloc[-1]['Signal_Line']:.5f}\n"
        )

        if st.button("Envoyer l'alerte par email"):
            if destinataire:
                send_email(
                    sujet,
                    corps,
                    destinataire,
                    expediteur,
                    "smtp.gmail.com",
                    587,
                    mot_de_passe,
                )
                st.success(f"Email envoyé à {destinataire} !")
            else:
                st.warning("Veuillez saisir l'adresse email du destinataire.")

    else:
        st.info("Aucun signal d’achat ou de vente n’a été détecté pour la journée la plus récente.")
