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
        # Link corrigido para busca global de produtos
        url = f"https://openfoodfacts.org{codigo}.json"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == 1:
                return dados["product"].get("product_name", "Produto Desconhecido")
    except:
        return None
    return None

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f:
            return json.load(f)
    return {"usuarios": {}, "historico": {}, "produtos_novos": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f)

if "tela" not in st.session_state:
    st.session_state.tela = "login"
if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

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
            else:
                st.error("Dados incorretos.")
    if st.button("Cadastrar 📝"):
        st.session_state.tela = "cadastro"
        st.rerun()

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
    if st.button("⬅️ Voltar"):
        st.session_state.tela = "login"
        st.rerun()

elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado}")
    aba1, aba2 = st.tabs(["🛒 Compra", "📂 Histórico"])

    with aba1:
        st.subheader("📸 Escanear por Foto")
        foto = st.camera_input("Aponte para o código de barras")
        
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            
            # Correção para evitar erro de desempacotamento (ValueError)
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado[0]:
                cod = resultado[0][0] # Pega o primeiro código detectado
                st.success(f"Código detectado: {cod}")
                
                dados_globais = carregar_dados()
                prod_info = dados_globais["produtos_novos"].get(cod, {})
                nome_p = prod_info.get("nome")
                preco_p = prod_info.get("preco", 0.0)

                if not nome_p:
                    with st.spinner("Buscando na internet..."):
                        nome_p = buscar_nome_internet(cod)
                
                if nome_p:
                    st.write(f"🔎 **Item:** {nome_p}")
                    p_atual = st.number_input("Preço R$:", value=float(preco_p), key=f"p_{cod}")
                    if st.button(f"Confirmar {nome_p}"):
                        dados_globais["produtos_novos"][cod] = {"nome": nome_p, "preco": p_atual}
                        salvar_dados(dados_globais)
                        if nome_p not in st.session_state.carrinho:
                            st.session_state.carrinho[nome_p] = {'preco': p_atual, 'qtd': 0}
                        st.session_state.carrinho[nome_p]['qtd'] += 1
                        st.rerun()
                else:
                    st.warning("Não achei o nome na internet. Tente focar melhor!")
            else:
                st.warning("Não li as barras. Tente deixar o código bem reto e nítido!")

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
        
        st.metric("TOTAL", f"R$ {total:.2f}")
        
        if st.sidebar.button("Sair"):
            del st.session_state.usuario_logado
            st.session_state.tela = "login"
            st.rerun()
