import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_usuarios_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE DADOS E INTERNET ---
def buscar_nome_internet(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("status") == 1:
            prod = r.json()["product"]
            return prod.get("product_name_pt") or prod.get("product_name") or "Produto Desconhecido"
    except: return None
    return None

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; font-weight: bold; }
    .whatsapp-btn { background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGAÇÃO ---
if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- 1. TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center; color: #1e3d59;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://wa.me{WHATSAPP_CONTATO}" class="whatsapp-btn">💬 Dúvidas? Fale com o Ivan</a>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("🔑 Entre na sua conta")
        u_log = st.text_input("Login (CPF ou Nome):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR 🚀"):
            dados = carregar_dados()
            if u_log in dados["usuarios"] and dados["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Login ou senha incorretos.")
    
    if st.button("Não tem conta? Cadastre-se aqui 📝"):
        st.session_state.tela = "cadastro"
        st.rerun()

# --- 2. TELA DE CADASTRO ---
elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro de Novo Usuário")
    with st.form("cadastro_form"):
        n_c = st.text_input("Nome Completo:")
        c_c = st.text_input("CPF (será seu login):")
        s_c = st.text_input("Crie uma Senha:", type="password")
        if st.form_submit_button("FINALIZAR CADASTRO ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                dados = carregar_dados()
                exp = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                dados["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": exp, "pago": False}
                dados["historico"][login_id] = {}
                salvar_dados(dados)
                st.success("Cadastro realizado! Volte para a tela de login.")
            else: st.error("Preencha todos os campos!")
    if st.button("⬅️ Voltar para Login"):
        st.session_state.tela = "login"
        st.rerun()

# --- 3. TELA DO APLICATIVO ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}!")
    
    if st.sidebar.button("⬅️ Sair / Voltar ao Início"):
        st.session_state.tela = "login"
        st.rerun()

    aba1, aba2 = st.tabs(["🛒 Compra Atual", "📂 Histórico"])

    with aba1:
        st.subheader("📸 Escanear Produto")
        foto = st.camera_input("Aponte para o código de barras")
        
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado:
                cod = re.sub(r'\D', '', str(resultado))
                with st.spinner(f"Buscando código {cod}..."):
                    nome_p = buscar_nome_internet(cod)
                    if nome_p:
                        st.success(f"✅ Encontrado: {nome_p}")
                        preco = st.number_input(f"Preço de {nome_p}:", min_value=0.0, key=f"p_{cod}")
                        if st.button(f"Adicionar ao Carrinho"):
                            if nome_p not in st.session_state.carrinho:
                                st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
                            else:
                                st.session_state.carrinho[nome_p]['qtd'] += 1
                            st.rerun()
                    else:
                        st.warning("Produto não achado na internet. Digite o nome abaixo:")
                        n_man = st.text_input("Nome do Produto:")
                        p_man = st.number_input("Preço R$:", key="p_man")
                        if st.button("Salvar Manualmente"):
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()
            else:
                st.warning("Não consegui ler as barras. Tente focar melhor!")

        st.write("---")
        total = 0
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
            total += i['preco'] * i['qtd']
        st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
        
        if st.button("💾 Salvar no Histórico"):
            d = carregar_dados()
            d["historico"][st.session_state.usuario_logado] = st.session_state.carrinho
            salvar_dados(d)
            st.success("Salvo!")

    with aba2:
        st.header("📂 Compras Salvas")
        d = carregar_dados()
        hist = d["historico"].get(st.session_state.usuario_logado, {})
        if hist:
            for n, i in hist.items(): st.text(f"• {i['qtd']}x {n}")
            if st.button("🔄 Recuperar para o Carrinho"):
                st.session_state.carrinho = hist
                st.rerun()
        else: st.info("Nada salvo ainda.")
