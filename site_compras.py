import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN (MANTIDAS) ---
WHATSAPP_LINK = "https://wa.me!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE DADOS (MANTIDAS) ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f: return json.load(f)
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f: json.dump(dados, f)

# --- NOVA BUSCA TURBINADA BRASIL ---
def buscar_produto_total(codigo):
    # 1. Verifica na memória do seu App (Produtos que você já ensinou)
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    # 2. Tenta busca na base brasileira (OpenFood/Cosmos Lite)
    # Testamos o código normal e com um '0' na frente (comum no Brasil)
    codigos_tentar = [codigo, codigo.lstrip('0'), '0' + codigo]
    
    for cod in codigos_tentar:
        try:
            url = f"https://openfoodfacts.org{cod}.json"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                dados = r.json()
                if dados.get("status") == 1:
                    prod = dados["product"]
                    nome = prod.get("product_name_pt") or prod.get("product_name") or prod.get("generic_name")
                    if nome:
                        return nome.capitalize(), 0.0
        except:
            continue
    return None, 0.0

# --- ESTILO VISUAL (MANTIDO) ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- LÓGICA DE LOGIN/CADASTRO (MANTIDA INTEGRALMENTE) ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" class="whatsapp-btn">💬 Fale com o Ivan no WhatsApp</a>', unsafe_allow_html=True)
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
        st.session_state.tela = "cadastro"
        st.rerun()

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
        st.session_state.tela = "login"
        st.rerun()

# --- TELA PRINCIPAL (FUNCIONALIDADE DO SCANNER) ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}!")
    if st.sidebar.button("⬅️ Sair"):
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
                
                with st.spinner(f"Buscando informações de {cod}..."):
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
                        st.warning("Produto não encontrado na base nacional. Ajude-nos a aprender:")
                        n_man = st.text_input("Nome do Produto (Ex: Arroz 5kg):")
                        p_man = st.number_input("Preço R$:", key="p_man")
                        if st.button("Salvar e Adicionar"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": n_man, "preco": p_man}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()
            else: st.warning("Não consegui ler. Tente focar mais de perto ou com mais luz!")

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
        st.metric("TOTAL", f"R$ {total:.2f}")
