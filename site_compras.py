import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="📟", layout="centered")

# --- FUNÇÕES DE BUSCA ---
def buscar_produto(codigo):
    if not codigo: return None, 0.0
    memoria = {}
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r") as f: memoria = json.load(f)
    
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            nome = p.get("product_name_pt") or p.get("product_name")
            return nome.upper(), 0.0
    except: pass
    return None, 0.0

# --- ESTILO ---
st.markdown("<style>.visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; }</style>", unsafe_allow_html=True)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.markdown("<h1 style='text-align:center;'>📟 REGISTRADORA IVAN</h1>", unsafe_allow_html=True)

# --- SCANNER ---
st.subheader("📸 Escanear Produto")
foto = st.camera_input("Tire foto do código de barras")

if foto:
    # Processando a imagem com o motor de alta precisão
    bytes_data = foto.getvalue()
    img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Detector estilo "WeChat" (Mais potente que o comum)
    detector = cv2.wechat_qrcode_WeChatQRCode()
    codigos, pontos = detector.detectAndDecode(img)
    
    if codigos:
        cod = str(codigos[0]).strip()
        st.success(f"📟 Código detectado: {cod}")
        
        nome, preco_sug = buscar_produto(cod)
        if nome:
            st.info(f"📦 PRODUTO: {nome}")
            p = st.number_input("Preço R$:", value=float(preco_sug), step=0.01)
            if st.button("➕ ADICIONAR"):
                st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, {'preco': p, 'qtd': 0})
                st.session_state.carrinho[nome]['qtd'] += 1
                st.toast("Adicionado!")
        else:
            st.warning("NOME NÃO ENCONTRADO")
            n_m = st.text_input("Nome do Produto:")
            p_m = st.number_input("Preço Unitário:")
            if st.button("SALVAR MANUAL"):
                st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                st.rerun()
    else:
        st.error("Não consegui ler as barras. Tente aproximar um pouco mais o celular.")

# --- CARRINHO ---
st.write("---")
total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)

for n, i in list(st.session_state.carrinho.items()):
    st.write(f"• {i['qtd']}x {n} - R$ {i['preco']*i['qtd']:.2f}")
