import streamlit as st
import cv2
import numpy as np
import requests
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Registradora Digital", page_icon="🛒", layout="centered")

# --- FUNÇÃO DE BUSCA NA INTERNET ---
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

# --- ESTILO VISUAL REGISTRADORA ---
st.markdown("""
    <style>
    .visor-caixa { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .item-linha { background:#1e1e1e; padding:15px; border-radius:12px; margin-bottom:10px; border-left: 5px solid #00ff88; color: white; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; }
    </style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("📟 Registradora Inteligente")

# 1. VISOR DE TOTAL
total_compra = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor-caixa'><small>TOTAL DA COMPRA</small><h1>R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

# 2. SCANNER DE CÓDIGO DE BARRAS
st.subheader("🛍️ Bipar Mercadoria")
foto = st.camera_input("Tire foto do código de barras para registrar")

if foto:
    # Processa a foto
    bytes_data = foto.getvalue()
    img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.barcode.BarcodeDetector()
    ok, pontos, codigos, tipos = detector.detectAndDecode(img)
    
    if ok:
        cod = str(codigos).strip()
        nome_p = buscar_nome(cod)
        
        if nome_p:
            st.success(f"✅ Identificado: {nome_p}")
            preco_p = st.number_input(f"Preço de {nome_p}:", min_value=0.0, step=0.01, key=f"p_{cod}")
            if st.button("➕ ADICIONAR AO CARRINHO"):
                st.session_state.carrinho[nome_p] = {'preco': preco_p, 'qtd': 1}
                st.rerun()
        else:
            st.warning(f"Código {cod} não achado na internet.")
            n_man = st.text_input("Nome do produto:")
            p_man = st.number_input("Preço R$:", key="p_man")
            if st.button("Salvar Manual"):
                st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                st.rerun()
    else:
        st.error("Não consegui ler as barras. Tente focar melhor ou limpar a lente!")

# 3. LISTA DE COMPRAS COM AJUSTE DE QUANTIDADE
st.write("---")
st.subheader("🛒 Itens Registrados")

if not st.session_state.carrinho:
    st.info("Nenhum item bipado ainda.")
else:
    for nome in list(st.session_state.carrinho.keys()):
        item = st.session_state.carrinho[nome]
        with st.container():
            st.markdown(f"<div class='item-linha'><b>{nome}</b> - R$ {item['preco']:.2f}</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1,1,1,1])
            
            if c1.button("➖", key=f"min_{nome}"):
                if item['qtd'] > 1: st.session_state.carrinho[nome]['qtd'] -= 1
                else: del st.session_state.carrinho[nome]
                st.rerun()
            
            c2.markdown(f"<h4 style='text-align:center;'>{item['qtd']}</h4>", unsafe_allow_html=True)
            
            if c3.button("➕", key=f"plus_{nome}"):
                st.session_state.carrinho[nome]['qtd'] += 1
                st.rerun()
                
            if c4.button("❌", key=f"del_{nome}"):
                del st.session_state.carrinho[nome]
                st.rerun()

if st.button("🗑️ LIMPAR TODA A COMPRA"):
    st.session_state.carrinho = {}
    st.rerun()
