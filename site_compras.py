import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES IVAN ---
WHATSAPP_LINK = "https://whatsapp.com!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE BUSCA TURBINADA BRASIL ---
def buscar_produto_total(codigo):
    # 1. Verifica na SUA MEMÓRIA (O que você já ensinou)
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    # 2. BUSCA MULTICAMADAS (Tenta 3 caminhos diferentes)
    urls_tentar = [
        f"https://openfoodfacts.org{codigo}.json",
        f"https://openfoodfacts.org{codigo}.json",
        f"https://openfoodfacts.org{codigo}.json"
    ]
    
    for url in urls_tentar:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                dados = r.json()
                if dados.get("status") == 1:
                    p = dados["product"]
                    # Tenta pegar o nome mais claro possível
                    nome = p.get("product_name_pt") or p.get("product_name") or p.get("generic_name_pt")
                    if nome:
                        return nome.strip().upper(), 0.0
        except:
            continue

    # 3. Se for código brasileiro (789...), tenta uma busca simplificada
    if codigo.startswith("789"):
        try:
            # Simula uma busca de metadados de mercado
            url_aux = f"https://upcitemdb.com{codigo}"
            r_aux = requests.get(url_aux, timeout=3)
            if r_aux.status_code == 200:
                itens = r_aux.json().get("items", [])
                if itens:
                    return itens[0].get("title").upper(), 0.0
        except: pass

    return None, 0.0

# --- FUNÇÕES DE DADOS (MANTIDAS) ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False)

# --- ESTILO ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white !important; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- LÓGICA DE LOGIN/APP (RESUMIDA - USE SEU CÓDIGO COMPLETO) ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 Fale com o Ivan no WhatsApp</a>', unsafe_allow_html=True)
    with st.form("login_form"):
        u_log = st.text_input("Login:").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR"):
            dados = carregar_json(ARQUIVO_DADOS)
            if u_log in dados.get("usuarios", {}) and dados["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Erro no login.")
    if st.button("Criar Conta 📝"): st.session_state.tela = "cadastro"; st.rerun()

elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado}")
    aba1, aba2 = st.tabs(["🛒 Scanner", "📂 Histórico"])

    with aba1:
        foto = st.camera_input("Aponte para o código de barras")
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            ok, pontos, codigos, tipos = detector.detectAndDecode(img)
            
            if ok:
                cod = str(codigos[0]).strip()
                with st.spinner(f"Buscando {cod} no Brasil..."):
                    nome_p, preco_sug = buscar_produto_total(cod)
                    
                    if nome_p:
                        st.success(f"📦 ITEM: {nome_p}")
                        preco = st.number_input("Preço R$:", value=float(preco_sug), key=f"p_{cod}")
                        if st.button(f"Adicionar {nome_p}"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": nome_p, "preco": preco}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[nome_p] = st.session_state.carrinho.get(nome_p, {'preco': preco, 'qtd': 0})
                            st.session_state.carrinho[nome_p]['qtd'] += 1
                            st.rerun()
                    else:
                        st.warning(f"Código {cod} não achado na internet.")
                        n_man = st.text_input("Qual o nome do produto?")
                        p_man = st.number_input("Qual o preço?")
                        if st.button("Salvar na minha memória"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": n_man, "preco": p_man}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.metric("TOTAL", f"R$ {total:.2f}")

    if st.sidebar.button("Sair"): st.session_state.tela = "login"; st.rerun()
