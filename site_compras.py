import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

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

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}, "produtos_novos": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- TELAS DE LOGIN/CADASTRO ---
if st.session_state.tela == "login":
    st.title("🛒 Calculadora de Mercado")
    with st.form("login_form"):
        u_log = st.text_input("Login (CPF):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR"):
            d = carregar_dados()
            if u_log in d["usuarios"] and d["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Dados incorretos.")
    if st.button("Cadastrar 📝"): st.session_state.tela = "cadastro"; st.rerun()

elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro Novo")
    with st.form("c_form"):
        n_c = st.text_input("Nome:")
        c_c = st.text_input("CPF:")
        s_c = st.text_input("Senha:", type="password")
        if st.form_submit_button("CADASTRAR"):
            login_id = re.sub(r'\D', '', c_c)
            d = carregar_dados()
            d["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": "2026-12-31", "pago": False}
            d["historico"][login_id] = {}
            salvar_dados(d)
            st.success("Sucesso! Volte ao login.")
    if st.button("⬅️ Voltar"): st.session_state.tela = "login"; st.rerun()

elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado}")
    aba1, aba2 = st.tabs(["🛒 Compra", "📂 Histórico"])

    with aba1:
        st.subheader("🚀 Scanner Rápido")
        # Campo preparado para o scanner do teclado
        input_rapido = st.text_input("Clique aqui e use o scanner do teclado:", key="input_direto")
        
        if input_rapido:
            cod = re.sub(r'\D', '', input_rapido)
            with st.spinner("Buscando produto..."):
                nome_p = buscar_nome_internet(cod)
                if nome_p:
                    st.success(f"✅ {nome_p}")
                    if nome_p not in st.session_state.carrinho:
                        st.session_state.carrinho[nome_p] = {'preco': 0.0, 'qtd': 0}
                    st.session_state.carrinho[nome_p]['qtd'] += 1
                    # Limpa o campo e recarrega
                    st.session_state.input_direto = ""
                    st.rerun()
                else:
                    st.warning("Produto não encontrado na internet.")

        st.write("---")
        total = 0
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            sub = item['preco'] * item['qtd']
            total += sub
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(f"**{n}**")
            with col2:
                # Permite ajustar o preço na hora
                p = st.number_input("Preço R$", value=float(item['preco']), key=f"p_{n}")
                st.session_state.carrinho[n]['preco'] = p
            with col3:
                q = st.number_input("Qtd", 0, 100, int(item['qtd']), key=f"q_{n}")
                if q == 0: del st.session_state.carrinho[n]; st.rerun()
                st.session_state.carrinho[n]['qtd'] = q
        
        st.metric("TOTAL ATUAL", f"R$ {total:.2f}")
        
        if st.sidebar.button("Sair"):
            del st.session_state.usuario_logado
            st.session_state.tela = "login"
            st.rerun()
