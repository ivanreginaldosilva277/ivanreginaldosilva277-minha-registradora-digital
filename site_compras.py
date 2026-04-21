import streamlit as st
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒")

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

# --- INTERFACE ---
st.title("🛒 Calculadora de Mercado")

st.subheader("📟 Scanner de Barras")
st.write("Clique no campo abaixo e use o **Scanner do Teclado** do seu Samsung:")

# Campo de texto que processa o código sozinho ao receber o dado
codigo_lido = st.text_input("Toque aqui para escanear:", key="input_scan")

if codigo_lido:
    cod = re.sub(r'\D', '', codigo_lido)
    with st.spinner(f"Buscando produto..."):
        nome_p = buscar_nome_internet(cod)
        if nome_p:
            if nome_p not in st.session_state.carrinho:
                st.session_state.carrinho[nome_p] = {'preco': 0.0, 'qtd': 0}
            st.session_state.carrinho[nome_p]['qtd'] += 1
            st.success(f"✅ {nome_p} adicionado!")
            # Limpa para o próximo
            st.session_state.input_scan = ""
            st.rerun()
        else:
            st.warning("Produto não encontrado. Tente outro!")

st.write("---")
total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
for n, i in st.session_state.carrinho.items():
    col1, col2 = st.columns([2,1])
    col1.write(f"**{i['qtd']}x {n}**")
    p = col2.number_input("R$", value=float(i['preco']), key=f"p_{n}")
    st.session_state.carrinho[n]['preco'] = p

st.metric("TOTAL", f"R$ {total:.2f}")
