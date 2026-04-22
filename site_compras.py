import streamlit as st
import requests
import re
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Registradora por Voz", page_icon="🎙️")

# --- FUNÇÃO DE BUSCA NA INTERNET ---
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=4)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- VISOR DE CAIXA ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; }
    </style>
""", unsafe_allow_html=True)

total_compra = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>TOTAL</small><h1>R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA POR MICROFONE (VOZ) ---
st.subheader("🎙️ Dite o Código de Barras")
st.info("Toque no campo abaixo, use o MICROFONE do seu teclado e diga os números do código:")

# O campo de texto recebe os números que você ditar pelo teclado
codigo_ditado = st.text_input("Clique aqui e fale o código:", key="input_voz")

if codigo_ditado:
    # Limpa o texto para deixar apenas os números
    cod_limpo = re.sub(r'\D', '', codigo_ditado)
    
    if cod_limpo:
        with st.spinner(f"Identificando código {cod_limpo}..."):
            nome_p = buscar_nome(cod_limpo)
            
            if nome_p:
                st.success(f"✅ Identificado: {nome_p}")
                preco = st.number_input(f"Preço de {nome_p}:", min_value=0.0, step=0.01, key=f"p_{cod_limpo}")
                if st.button("➕ ADICIONAR"):
                    st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                    st.session_state.input_voz = "" # Limpa para o próximo
                    st.rerun()
            else:
                st.warning("Não achei esse código. Digite o nome manualmente:")
                n_man = st.text_input("Nome do produto:")
                p_man = st.number_input("Preço R$:", key="p_man")
                if st.button("Salvar Manual"):
                    st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                    st.rerun()

# --- LISTA DE CONFERÊNCIA ---
st.write("---")
for nome in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[nome]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{nome}**")
    # Botões de + e - integrados
    item['qtd'] = c2.number_input("Qtd", value=item['qtd'], key=f"q_{nome}", min_value=1)
    if c3.button("X", key=f"d_{nome}"):
        del st.session_state.carrinho[nome]
        st.rerun()
