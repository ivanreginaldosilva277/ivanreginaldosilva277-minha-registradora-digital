import streamlit as st
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_MEMORIA = "banco_zona_leste.json"

st.set_page_config(page_title="Registradora Ultra Rápida", page_icon="⚡")

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def buscar_nome_ninja(codigo):
    memoria = carregar_memoria()
    if codigo in memoria: return memoria[codigo]

    # Tenta a base de dados oficial do Brasil (mais completa)
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome:
                    # Salva na memória para ser instantâneo na próxima vez
                    memoria[codigo] = nome.strip().upper()
                    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
                        json.dump(memoria, f, ensure_ascii=False)
                    return nome.strip().upper()
    except: pass
    return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; height: 3.5em; background-color: #2e7d32; color: white; }
    </style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

total = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>VALOR ACUMULADO</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA DE DADOS ---
st.write("### 🛍️ Bipar ou Ditar")
codigo_input = st.text_input("Use o microfone ou digite o código:", key="input_bip")

if codigo_input:
    cod = re.sub(r'\D', '', codigo_input)
    if cod:
        with st.spinner("Localizando..."):
            nome_p = buscar_nome_ninja(cod)
            
            # Se não achou, coloca um nome automático para não perder tempo
            if not nome_p:
                nome_p = f"PRODUTO {cod[-4:]}" # Pega os últimos 4 números do código
            
            st.success(f"📦 {nome_p}")
            preco = st.number_input(f"Preço do item (R$):", min_value=0.0, step=0.01, key=f"p_{cod}")
            
            if st.button("➕ ADICIONAR AGORA"):
                st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                st.session_state.input_bip = "" # Limpa para o próximo
                st.rerun()

# --- LISTA NO CARRINHO ---
st.write("---")
for nome in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[nome]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{nome}**")
    item['qtd'] = c2.number_input("Qtd", value=item['qtd'], key=f"q_{nome}", min_value=1)
    if c3.button("X", key=f"d_{nome}"):
        del st.session_state.carrinho[nome]
        st.rerun()
