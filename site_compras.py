import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES (MANTIDAS) ---
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

# --- BUSCA INTELIGENTE DE PRODUTOS ---
def buscar_produto_total(codigo):
    # 1. Verifica na sua própria memória (O que o app já aprendeu)
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    # 2. Tenta busca na base oficial de produtos brasileira
    try:
        # Usando a API do Cosmos/OpenFoodFacts que é a mais rápida para produtos BR
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                # Pega o nome mais completo disponível
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome: return nome.strip().upper(), 0.0
    except: pass
    
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

# --- LÓGICA DE LOGIN (INTEGRAL) ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 Fale com o Ivan no WhatsApp</a>', unsafe_allow_html=True)
    with st.form("login_form"):
        u_log = st.text_input("Login (CPF ou Nome):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR 🚀"):
            dados = carregar_json(ARQUIVO_DADOS)
            if u_log in dados.get("usuarios", {}) and dados["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Login ou senha incorretos.")
    if st.button("Não tem conta? Cadastre-se aqui 📝"):
        st.session_state.tela = "cadastro"; st.rerun()

elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro Novo")
    with st.form("c_form"):
        n_c = st.text_input("Nome Completo:")
        c_c = st.text_input("CPF (Login):")
        s_c = st.text_input("Senha:", type="password")
        if st.form_submit_button("FINALIZAR ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                dados = carregar_json(ARQUIVO_DADOS)
                if "usuarios" not in dados: dados["usuarios"] = {}
                exp = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                dados["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": exp, "pago": False}
                salvar_json(ARQUIVO_DADOS, dados)
                st.success("Cadastrado! Volte ao login.")
            else: st.error("Preencha tudo!")
    if st.button("⬅️ Voltar"):
        st.session_state.tela = "login"; st.rerun()

# --- TELA DO APP (FOCO NO SCANNER) ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}!")
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
                with st.spinner(f"Consultando Google e Bancos de Dados..."):
                    nome_p, preco_sug = buscar_produto_total(cod)
                    
                    if nome_p:
                        st.success(f"✅ Identificado: {nome_p}")
                        preco = st.number_input(f"Preço de hoje (R$):", value=float(preco_sug), key=f"p_{cod}", step=0.01)
                        if st.button(f"Confirmar e Adicionar ao Total"):
                            # Salva na memória do App para sempre
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": nome_p, "preco": preco}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            # Adiciona no carrinho
                            st.session_state.carrinho[nome_p] = st.session_state.carrinho.get(nome_p, {'preco': preco, 'qtd': 0})
                            st.session_state.carrinho[nome_p]['qtd'] += 1
                            st.rerun()
                    else:
                        st.warning("Google não identificou o nome. Digite uma vez para o sistema aprender:")
                        n_man = st.text_input("Nome do Produto:", key="n_man")
                        p_man = st.number_input("Preço R$:", key="p_man", step=0.01)
                        if st.button("Salvar na Memória do App"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": n_man, "preco": p_man}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()
            else: st.warning("Leitura falhou. Tente centralizar as barras pretas na foto.")

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
        st.metric("VALOR TOTAL DA COMPRA", f"R$ {total:.2f}")

    if st.sidebar.button("Sair"):
        st.session_state.tela = "login"; st.rerun()
