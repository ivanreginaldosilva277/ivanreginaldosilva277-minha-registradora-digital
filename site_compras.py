import streamlit as st
import requests
import re
import json
import os
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"

def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒")

# --- ESTADO E LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

if not st.session_state.logado:
    st.title("📟 PDV REGISTRADORA")
    u = st.text_input("CPF:")
    s = st.text_input("Senha:", type="password")
    if st.button("ABRIR CAIXA"):
        st.session_state.logado = True; st.rerun()
else:
    st.title("🛍️ BIPAR PRODUTO")
    
    # ESTA É A ÚNICA FORMA QUE FUNCIONA NO SAMSUNG A03 SEM TRAVAR
    # Ele abre a sua câmera traseira oficial do Android
    foto_camera = st.camera_input("APONTE PARA O CÓDIGO E TIRE UMA FOTO")

    if foto_camera:
        st.info("Buscando informações do produto...")
        # (O sistema vai processar a imagem aqui)
        # Por enquanto, como o leitor de vídeo travou, use este campo para confirmar o número:
        cod_manual = st.text_input("Se o número não apareceu, digite aqui:")
        
        if cod_manual:
            nome = buscar_nome(cod_manual)
            if nome:
                st.success(f"PRODUTO: {nome}")
                if st.button("ADCIONAR AO CARRINHO"):
                    st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, 0) + 1
                    st.toast("Adicionado!")
            else:
                st.warning("Produto não cadastrado.")

    st.write("---")
    st.subheader("🛒 Carrinho Atual")
    for item, qtd in st.session_state.carrinho.items():
        st.write(f"{qtd}x {item}")
