import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
# Link direto para o seu celular (funciona no PC e Celular)
WHATSAPP_LINK = "https://wa.me!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE BUSCA E MEMÓRIA ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f: return json.load(f)
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f: json.dump(dados, f)

def buscar_produto_total(codigo):
    # 1. Tenta buscar na memória que o app já aprendeu
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    
    # 2. Se não conhece, busca na internet
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("status") == 1:
            prod = r.json()["product"]
            nome = prod.get("product_name_pt") or prod.get("product_name") or "Produto Desconhecido"
            return nome, 0.0
    except:
        return None, 0.0
    return None, 0.0

# --- ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- 1. TELA DE LOGIN ---
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

# --- 2. TELA DE CADASTRO ---
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

# --- 3. TELA DO APLICATIVO ---
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
                cod = str(resultado).strip()
                cod = re.sub(r'\W+', '', cod)
                
                with st.spinner("Buscando produto..."):
                    nome_p, preco_sug = buscar_produto_total(cod)
                    
                    if nome_p:
                        st.success(f"✅ Encontrado: {nome_p}")
                        preco = st.number_input(f"Preço R$:", value=float(preco_sug), key=f"p_{cod}")
                        if st.button(f"Confirmar {nome_p}"):
                            # Ensina ao app o nome e o preço para a próxima vez
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": nome_p, "preco": preco}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            
                            # Adiciona no carrinho
                            st.session_state.carrinho[nome_p] = st.session_state.carrinho.get(nome_p, {'preco': preco, 'qtd': 0})
                            st.session_state.carrinho[nome_p]['qtd'] += 1
                            st.rerun()
                    else:
                        st.warning("Produto não achado. Digite o nome e preço uma vez para o app aprender:")
                        n_man = st.text_input("Nome:")
                        p_man = st.number_input("Preço:", key="p_man")
                        if st.button("Salvar e Somar"):
                            memoria = carregar_json(ARQUIVO_MEMORIA)
                            memoria[cod] = {"nome": n_man, "preco": p_man}
                            salvar_json(ARQUIVO_MEMORIA, memoria)
                            st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                            st.rerun()
            else: st.warning("Não li as barras. Tente focar melhor!")

        st.write("---")
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        for n, i in st.session_state.carrinho.items():
            st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
        st.metric("TOTAL", f"R$ {total:.2f}")
