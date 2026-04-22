import streamlit as st
import requests
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Registradora Ivan", page_icon="🎙️")

# --- FUNÇÃO DE BUSCA TURBINADA (Busca em Duas Bases) ---
def buscar_nome(codigo):
    # Base 1: OpenFoodFacts (Mundial)
    try:
        url1 = f"https://openfoodfacts.org{codigo}.json"
        r1 = requests.get(url1, timeout=3)
        if r1.status_code == 200:
            d1 = r1.json()
            if d1.get("status") == 1:
                p = d1["product"]
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome: return nome.strip().upper()
    except: pass

    # Base 2: API de Apoio (Alternativa para Brasil)
    try:
        url2 = f"https://upcitemdb.com{codigo}"
        r2 = requests.get(url2, timeout=3)
        if r2.status_code == 200:
            d2 = r2.json()
            if d2.get("items"):
                return d2["items"][0].get("title").upper()
    except: pass
    
    return None

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; height: 3em; }
    </style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# Visor de Total
total_compra = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>TOTAL</small><h1>R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA POR VOZ OU TECLADO ---
st.subheader("🎙️ Identificar Produto")
codigo_input = st.text_input("Fale ou digite o código de barras:", key="input_bip")

if codigo_input:
    # Limpa espaços e letras, deixa só números
    cod_limpo = re.sub(r'\D', '', codigo_input)
    
    if cod_limpo:
        with st.spinner(f"Buscando {cod_limpo}..."):
            nome_p = buscar_nome(cod_limpo)
            
            if nome_p:
                st.success(f"✅ IDENTIFICADO: {nome_p}")
                preco = st.number_input(f"Qual o preço do(a) {nome_p}?", min_value=0.0, step=0.01, key=f"p_{cod_limpo}")
                if st.button("➕ ADICIONAR AO CAIXA"):
                    st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                    st.session_state.input_bip = "" # Limpa para o próximo
                    st.rerun()
            else:
                st.warning(f"O Google ainda não conhece o código {cod_limpo}.")
                n_man = st.text_input("Digite o nome desse produto uma única vez:", key="n_man")
                p_man = st.number_input("Preço R$:", key="p_man")
                if st.button("Salvar e Somar"):
                    st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                    st.rerun()

# --- LISTA DE ITENS NO CARRINHO ---
st.write("---")
for nome in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[nome]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{nome}**")
    item['qtd'] = c2.number_input("Qtd", value=item['qtd'], key=f"q_{nome}", min_value=1)
    if c3.button("X", key=f"d_{nome}"):
        del st.session_state.carrinho[nome]
        st.rerun()
