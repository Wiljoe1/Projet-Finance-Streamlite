import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


def app():
    st.title("📊 SMA (Simple Moving Average) & EMA (Exponential Moving Average)")
    # Ton code ici pour charger les données et afficher le graphique...
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
    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["EMA_20"] = df["close"].ewm(span=20, adjust=False).mean()

    fig_ma = go.Figure()
    fig_ma.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["close"],
            mode="lines",
            name="Close",
            line=dict(color="red", width=2),
        )
    )
    fig_ma.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["SMA_20"],
            mode="lines",
            name="SMA 20",
            line=dict(color="cyan", width=2),
        )
    )
    fig_ma.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["EMA_20"],
            mode="lines",
            name="EMA 20",
            line=dict(color="orange", width=2),
        )
    )
    fig_ma.update_layout(
        title="Cours de clôture, SMA 20 et EMA 20",
        xaxis_title="Date",
        yaxis_title="Prix",
        legend_title="Légende",
        template="plotly_dark",
        xaxis=dict(rangeslider=dict(visible=True)),
    )
    st.plotly_chart(fig_ma, use_container_width=True)

    st.markdown(
        """
    ## 📊  **Interprétations**

    ### 1. ***SMA 20 (Simple Moving Average 20 jours)***
    
    **Définition :**

    La SMA 20 est la moyenne arithmétique des 20 derniers cours de clôture. Elle lisse les variations de prix pour aider à repérer la tendance générale.

    **Interprétation :**

    - Si le prix dépasse la SMA 20 par le haut, cela peut indiquer une tendance haussière ou un signal d’achat.
    - Si le prix casse la SMA 20 par le bas, cela peut signaler une tendance baissière ou un signal de vente.
    - La SMA 20 réagit lentement aux changements rapides, ce qui limite les faux signaux mais peut réagir avec un peu de retard.

    ### 2. ***EMA 20 (Exponential Moving Average 20 jours)***

    **Définition :**
    L’EMA 20 donne plus de poids aux prix récents, ce qui la rend plus réactive aux mouvements de marché que la SMA.

    **Interprétation :**

    - Si le prix passe au-dessus de l’EMA 20, cela peut être interprété comme un signal haussier (tendance à l’achat).
    - Si le prix passe sous l’EMA 20, cela peut signaler une tendance baissière (tendance à la vente).
    - L’EMA 20 permet de détecter plus rapidement les retournements de tendance, mais elle peut générer plus de faux signaux que la SMA 20.
    """
    )
