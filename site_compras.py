import streamlit as st
import cv2
import numpy as np
import requests
import re

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒")

# Função para buscar nome na internet
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: return None
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("📟 Registradora do Ivan")

# --- ÁREA DO SCANNER ---
st.subheader("📸 Ler Código de Barras")

# ESTE É O BOTÃO OFICIAL QUE ABRE A CÂMERA NO SAMSUNG
foto = st.camera_input("Clique abaixo para abrir a câmera e ler o código")

if foto:
    # 1. Converte a foto para o leitor entender
    bytes_data = foto.getvalue()
    img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # 2. Motor de leitura de barras
    detector = cv2.barcode.BarcodeDetector()
    ok, pontos, codigos, tipos = detector.detectAndDecode(img)
    
    if ok:
        cod = str(codigos[0]).strip()
        st.success(f"✅ Código identificado: {cod}")
        nome = buscar_nome(cod)
        if nome:
            st.write(f"**Produto:** {nome}")
            if st.button(f"Somar {nome} no Carrinho"):
                st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, 0) + 1
                st.rerun()
        else:
            st.warning("Produto não achado na internet. Digite o nome abaixo:")
            n_m = st.text_input("Nome do produto:")
            if st.button("Salvar manual"):
                st.session_state.carrinho[n_m] = st.session_state.carrinho.get(n_m, 0) + 1
                st.rerun()
    else:
        st.error("Não consegui ler as barras. Tente deixar o código bem reto e nítido na foto.")

st.write("---")
st.subheader("🛒 Sua Sacola")
for item, qtd in st.session_state.carrinho.items():
    st.write(f"• {qtd}x **{item}**")
