import streamlit as st
import requests
import re
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Registradora por Voz", page_icon="🎙️")

# --- FUNÇÃO DE BUSCA TURBINADA (Link corrigido para produtos BR) ---
def buscar_nome(codigo):
    try:
        # Usamos a API v2 que é muito mais completa para o Brasil
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            dados = r.json()
            if dados.get("status") == 1:
                p = dados["product"]
                # Tentamos o nome em PT, depois o nome geral, depois a marca
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome:
                    return nome.strip().upper()
    except:
        pass
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- ESTILO ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; }
    </style>
""", unsafe_allow_html=True)

total_compra = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>TOTAL</small><h1>R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA POR VOZ ---
st.subheader("🎙️ Fale o Código de Barras")
codigo_ditado = st.text_input("Toque no microfone do teclado e diga o código:", key="input_voz")

if codigo_ditado:
    # Limpa o texto (remove espaços e letras se o celular entendeu errado)
    cod_limpo = re.sub(r'\D', '', codigo_ditado)
    
    if cod_limpo:
        with st.spinner(f"Consultando banco de dados para {cod_limpo}..."):
            nome_p = buscar_nome(cod_limpo)
            
            if nome_p:
                st.success(f"✅ Identificado: {nome_p}")
                preco = st.number_input(f"Valor de {nome_p}:", min_value=0.0, step=0.01, key=f"p_{cod_limpo}")
                if st.button("➕ SOMAR ITEM"):
                    st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                    st.session_state.input_voz = "" # Limpa para o próximo
                    st.rerun()
            else:
                st.warning(f"Código {cod_limpo} não tem nome na rede. Digite uma vez:")
                n_man = st.text_input("Qual o nome do produto?", key="n_man")
                p_man = st.number_input("Qual o preço?", key="p_man")
                if st.button("Salvar Manual"):
                    st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                    st.rerun()

# --- LISTA ---
st.write("---")
for nome in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[nome]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{nome}**")
    item['qtd'] = c2.number_input("Qtd", value=item['qtd'], key=f"q_{nome}", min_value=1)
    if c3.button("X", key=f"d_{nome}"):
        del st.session_state.carrinho[nome]
        st.rerun()
