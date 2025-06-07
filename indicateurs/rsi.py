import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def app():
    st.title("📈 RSI (Relative Strength Index)")

    # -- Requête API + préparation des données (à mutualiser selon projet)
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

    # -- Calcul RSI
    df["RSI_14"] = calculate_rsi(df["close"])

    # -- Création du graphique Plotly
    fig_rsi = go.Figure()
    fig_rsi.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["RSI_14"],
            mode="lines",
            name="RSI (14)",
            line=dict(color="purple", width=2),
        )
    )
    fig_rsi.add_trace(
        go.Scatter(
            x=df["date"],
            y=[70] * len(df),
            mode="lines",
            name="Surachat (70)",
            line=dict(color="red", dash="dash"),
        )
    )
    fig_rsi.add_trace(
        go.Scatter(
            x=df["date"],
            y=[30] * len(df),
            mode="lines",
            name="Survente (30)",
            line=dict(color="green", dash="dash"),
        )
    )
    fig_rsi.update_layout(
        title="RSI (Relative Strength Index)",
        xaxis_title="Date",
        yaxis_title="RSI",
        legend_title="Légende",
        template="plotly_dark",
        xaxis=dict(rangeslider=dict(visible=True)),
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(fig_rsi, use_container_width=True)

    # -- Interprétation en Markdown
    st.markdown(
        """
## 📈 **Interprétation du RSI**

### ***RSI 14 (Relative Strength Index 14 jours)***

**Définition :**

Le RSI 14 mesure la force et la vitesse des mouvements de prix sur les 14 dernières périodes, avec une échelle de 0 à 100.

**Interprétation classique :**

- RSI > 70 : Zone de surachat (potentiel retournement baissier ou correction à venir).

- RSI < 30 : Zone de survente (potentiel retournement haussier ou rebond).

- RSI entre 30 et 70 : Marché neutre ou sans tendance forte.

**Utilisation :**

- Peut être utilisé pour repérer les excès du marché (achat/vendue).

- Peut également signaler la continuité d’une tendance forte si le RSI reste élevé ou bas pendant longtemps.
    """
    )
