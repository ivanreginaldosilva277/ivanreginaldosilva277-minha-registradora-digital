import streamlit as st
from streamlit_camera_desktop_web_rtc import camera_desktop_web_rtc
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Calculadora Inteligente", page_icon="🛒")

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

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("🛒 Calculadora de Mercado")

# --- O LEITOR AUTOMÁTICO ---
st.subheader("📟 Leitor de Código de Barras")
st.write("Clique no botão abaixo para ativar o scanner automático:")

# Este componente abre a câmera e fica procurando o código sozinho
codigo_lido = camera_desktop_web_rtc()

if codigo_lido:
    cod = str(codigo_lido).strip()
    if "ultimo_codigo" not in st.session_state or st.session_state.ultimo_codigo != cod:
        st.session_state.ultimo_codigo = cod
        with st.spinner(f"Lendo código {cod}..."):
            nome_p = buscar_nome_internet(cod)
            if nome_p:
                if nome_p not in st.session_state.carrinho:
                    st.session_state.carrinho[nome_p] = {'preco': 0.0, 'qtd': 0}
                st.session_state.carrinho[nome_p]['qtd'] += 1
                st.success(f"✅ {nome_p} adicionado!")
                st.rerun()

st.write("---")
# --- EXIBIÇÃO DO CARRINHO ---
total = 0
for n, i in st.session_state.carrinho.items():
    c1, c2, c3 = st.columns([2,1,1])
    c1.write(f"**{n}**")
    with c2:
        p = st.number_input("R$", value=float(i['preco']), key=f"p_{n}")
        st.session_state.carrinho[n]['preco'] = p
    with c3:
        st.write(f"Qtd: {i['qtd']}")
    total += (st.session_state.carrinho[n]['preco'] * i['qtd'])

st.metric("VALOR TOTAL", f"R$ {total:.2f}")
