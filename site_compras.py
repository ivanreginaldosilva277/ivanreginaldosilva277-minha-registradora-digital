import streamlit as st
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_MEMORIA = "banco_zona_leste.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="🎙️")

# --- FUNÇÕES DE MEMÓRIA (O APRENDIZADO DO APP) ---
def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_na_memoria(codigo, nome):
    memoria = carregar_memoria()
    memoria[codigo] = nome.strip().upper()
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False)

def buscar_nome(codigo):
    # 1. Tenta buscar na memória local (Produtos que você já ensinou)
    memoria = carregar_memoria()
    if codigo in memoria:
        return memoria[codigo]

    # 2. Se não tem na memória, tenta na internet
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name")
                if nome:
                    salvar_na_memoria(codigo, nome) # Já aprende para a próxima
                    return nome.strip().upper()
    except: pass
    return None

# --- ESTILO VISUAL CAIXA ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; height: 3.5em; background-color: #2e7d32; color: white; }
    </style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

total_compra = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>TOTAL</small><h1>R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA DE DADOS ---
st.subheader("🎙️ Bipar ou Ditar Código")
codigo_input = st.text_input("Fale ou digite o código:", key="input_bip")

if codigo_input:
    cod_limpo = re.sub(r'\D', '', codigo_input)
    
    if cod_limpo:
        nome_p = buscar_nome(cod_limpo)
        
        if nome_p:
            st.success(f"✅ PRODUTO: {nome_p}")
            preco = st.number_input(f"Preço de {nome_p}:", min_value=0.0, step=0.01)
            if st.button("➕ ADICIONAR"):
                st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                st.rerun()
        else:
            st.warning(f"Código {cod_limpo} ainda não cadastrado.")
            n_man = st.text_input("Qual o nome deste produto?")
            p_man = st.number_input("Preço R$:", min_value=0.0)
            if st.button("Salvar e Aprender"):
                salvar_na_memoria(cod_limpo, n_man) # App aprende o nome para sempre
                st.session_state.carrinho[n_man.upper()] = {'preco': p_man, 'qtd': 1}
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
