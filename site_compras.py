import streamlit as st
from streamlit_barcode_scanner import st_barcode_scanner
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒")

def buscar_nome_internet(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == 1:
                return dados["product"].get("product_name", "Produto Desconhecido")
    except: return None
    return None

# (Mantendo suas funções de carregar/salvar dados e login...)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- DENTRO DA ABA DE COMPRA ---
st.subheader("📟 Scanner de Barras")
st.write("Aponte para o código e ele lerá sozinho:")

# Este é o comando que faz a mágica de ler sem bater foto
codigo_lido = st_barcode_scanner()

if codigo_lido:
    cod = str(codigo_lido).strip()
    with st.spinner(f"Lendo código {cod}..."):
        nome_p = buscar_nome_internet(cod)
        if nome_p:
            if nome_p not in st.session_state.carrinho:
                st.session_state.carrinho[nome_p] = {'preco': 0.0, 'qtd': 0}
            st.session_state.carrinho[nome_p]['qtd'] += 1
            st.success(f"✅ {nome_p} adicionado!")
            st.rerun()
