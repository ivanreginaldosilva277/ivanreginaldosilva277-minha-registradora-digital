import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
WHATSAPP_LINK = "https://whatsapp.com!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE DADOS ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False)

def buscar_produto_total(codigo):
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    urls = [
        f"https://openfoodfacts.org{codigo}.json",
        f"https://openfoodfacts.org{codigo}.json"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                d = r.json()
                if d.get("status") == 1:
                    p = d["product"]
                    nome = p.get("product_name_pt") or p.get("product_name")
                    if nome: return nome.strip().upper(), 0.0
        except: continue
    return None, 0.0

# --- ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white !important; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- 1. TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 Fale com o Ivan no WhatsApp</a>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        u_log = st.text_input("Login (CPF ou Nome):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR 🚀"):
            dados = carregar_json(ARQUIVO_DADOS)
            usuarios = dados.get("usuarios", {})
            if u_log in usuarios and usuarios[u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Login ou senha incorretos.")
    
    if st.button("Não tem conta? Cadastre-se aqui 📝"):
        st.session_state.tela = "cadastro"
        st.rerun()

# --- 2. TELA DE CADASTRO (CORRIGIDA) ---
elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro Novo")
    st.write("Preencha os dados abaixo para criar sua conta.")
    
    with st.form("c_form"):
        n_c = st.text_input("Nome Completo:")
        c_c = st.text_input("CPF (será seu login):")
        s_c = st.text_input("Crie uma Senha:", type="password")
        if st.form_submit_button("FINALIZAR CADASTRO ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                dados = carregar_json(ARQUIVO_DADOS)
                if "usuarios" not in dados: dados["usuarios"] = {}
                exp = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                dados["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": exp, "pago": False}
                salvar_json(ARQUIVO_DADOS, dados)
                st.success("Cadastrado com sucesso!")
                st.info("Clique no botão 'Voltar' abaixo para fazer login.")
            else: st.error("Por favor, preencha todos os campos!")
    
    if st.button("⬅️ Voltar para o Login"):
        st.session_state.tela = "login"
        st.rerun()

# --- 3. TELA DO APLICATIVO ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}!")
    if st.sidebar.button("Sair"):
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
                with st.spinner(f"Buscando {cod}..."):
                    nome_p, preco_sug = buscar_produto_total(cod)
                    if nome_p:
                        st.success(f"✅ Encontrado: {nome_p}")
                        preco = st.number_input(f"Preço R$:", value=float(preco_sug), key=f"p_{cod}")
                        if st.button(f"Confirmar {nome_p}"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": nome_p, "preco": preco}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[nome_p] = st.session_state.carrinho.get(nome_p, {'preco': preco, 'qtd': 0})
                            st.session_state.carrinho[nome_p]['qtd'] += 1
                            st.rerun()
                    else:
                        st.warning("Produto novo! Digite o nome uma vez:")
                        n_man = st.text_input("Nome:", key="n_man")
                        p_man = st.number_input("Preço R$:", key="p_man")
                        if st.button("Salvar e Adicionar"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": n_man, "preco": p_man}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
        st.metric("TOTAL", f"R$ {total:.2f}")
