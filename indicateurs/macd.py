import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

def app():
    st.title("📉 MACD (Moving Average Convergence Divergence)")

    # --- Récupération et préparation des données (mutualisable)
    api_key = '89VPC1UGYMZL10S4'
    url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=EUR&to_symbol=USD&outputsize=full&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    time_series = data.get('Time Series FX (Daily)', {})
    df = pd.DataFrame.from_dict(time_series, orient='index')
    df.columns = ['open', 'high', 'low', 'close']
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    df['close'] = df['close'].astype(float)

    # --- Calcul MACD
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal_Line']

    # --- Création du graphique Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['MACD'],
        mode='lines', name='MACD',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['Signal_Line'],
        mode='lines', name='Signal Line',
        line=dict(color='orange', width=2)
    ))
    fig.add_trace(go.Bar(
        x=df['date'], y=df['Histogram'],
        name='Histogram',
        marker_color='gray', opacity=0.5
    ))
    fig.update_layout(
        title='MACD (Moving Average Convergence Divergence)',
        xaxis_title='Date',
        yaxis_title='Valeur',
        legend_title='Légende',
        template='plotly_dark',
        xaxis=dict(rangeslider=dict(visible=True)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Explications et interprétation
    st.markdown("""
## 🔍 **Pourquoi ces valeurs ?**

Ces chiffres proviennent de la méthode d’origine développée par Gerald Appel dans les années 1970 :

- **12** : moyenne mobile exponentielle (EMA) courte (rapide), sur 12 jours.
- **26** : EMA longue (lente), sur 26 jours.
- **9** : EMA de la ligne MACD pour générer la ligne de signal (signal line).

## 📉 **Interprétation du MACD**

**Définition :**  
Le MACD est un indicateur de momentum qui mesure la différence entre deux moyennes mobiles exponentielles (EMA) des prix : généralement EMA 12 jours et EMA 26 jours.  
Il est composé de deux courbes principales :

- **Ligne MACD** : EMA 12 – EMA 26
- **Ligne de signal** : EMA 9 de la ligne MACD

**Interprétation des signaux principaux :**

- Si la **MACD > 0** → tendance haussière.
- Si la **MACD < 0** → tendance baissière.
- Si la **MACD croise au-dessus** de la ligne de signal → **signal d’achat**.
- Si la **MACD croise en dessous** → **signal de vente**.

L’histogramme (barres grises) montre la force de la divergence entre la MACD et la ligne de signal :  
- Plus il est haut (positif), plus l’élan haussier est fort.
- Plus il est bas (négatif), plus la pression vendeuse est importante.

**Comme pour tous les indicateurs, il est conseillé de croiser l’analyse du MACD avec d’autres outils pour plus de fiabilité.**
""")
