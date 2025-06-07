import streamlit as st
from PIL import Image
import os
import importlib

# Les titres et icônes de chaque "app"
PAGES = {
    "📊 SMA & EMA": "sma_ema",
    "📈 RSI": "rsi",
    "📉 MACD": "macd",
}

st.set_page_config(page_title="Analyse Financière EUR/USD",
                   page_icon="images/logo_app.png",
                   layout="wide")

# Sidebar menu
#st.sidebar.title("Analyse EUR/USD")

st.sidebar.image("images/logo_app.png", width=50, use_container_width=True)# 
selection = st.sidebar.selectbox("Choisissez un indicateur", list(PAGES.keys()))

# Onglet spécial AUTOMATISATION en dessous
st.sidebar.markdown("---")
trading_auto = st.sidebar.button("⚡ Automatisation & Trading")

if trading_auto:
    page_module = importlib.import_module("indicateurs.automatisation")
    page_module.app()
else:
    page_module = importlib.import_module(f"indicateurs.{PAGES[selection]}")
    page_module.app()