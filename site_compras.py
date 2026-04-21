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

# --- FUNÇÕES DE SISTEMA ---
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
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name")
                if nome: return nome.strip().upper(), 0.0
    except: pass
    return None, 0.0

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; margin-top: 10px; }
    .whatsapp-btn { background-color: #25d366; color: white !important; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }
    .card-carrinho { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- 1. TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Minha Compra Segura</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 Fale com o Ivan no WhatsApp</a>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        u_log = st.text_input("CPF ou Nome de Usuário:").strip().lower()
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

# --- 2. TELA DE CADASTRO ---
elif st.session_state.tela == "cadastro":
    st.title("📝 Criar Nova Conta")
    with st.form("c_form"):
        n_c = st.text_input("Nome Completo:")
        c_c = st.text_input("CPF (será seu login):")
        s_c = st.text_input("Crie uma Senha:", type="password")
        if st.form_submit_button("FINALIZAR CADASTRO ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                dados = carregar_json(ARQUIVO_DADOS)
                if "usuarios" not in dados: dados["usuarios"] = {}
                dados["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "historico": {}}
                salvar_json(ARQUIVO_DADOS, dados)
                st.success("Cadastrado com sucesso! Clique em voltar para logar.")
            else: st.error("Preencha todos os campos!")
    if st.button("⬅️ Voltar para o Login"):
        st.session_state.tela = "login"
        st.rerun()

# --- 3. TELA DO APLICATIVO (CARRINHO ORGANIZADO) ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado}!")
    
    if st.sidebar.button("⬅️ Sair"):
        st.session_state.tela = "login"
        st.rerun()

    aba1, aba2 = st.tabs(["🛒 Carrinho de Compra", "📂 Histórico"])

    with aba1:
        st.subheader("📸 Escanear Produto")
        foto = st.camera_input("Tirar foto do código")
        
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado:
                cod = re.sub(r'\D', '', str(resultado))
                nome_p, preco_sug = buscar_produto_total(cod)
                
                if nome_p:
                    # Adiciona direto se já existir, ou abre para confirmar se for novo na sessão
                    if nome_p not in st.session_state.carrinho:
                        st.session_state.carrinho[nome_p] = {'preco': preco_sug, 'qtd': 1}
                    else:
                        st.session_state.carrinho[nome_p]['qtd'] += 1
                    st.success(f"✅ Adicionado: {nome_p}")
                else:
                    st.warning("Produto não identificado.")
                    n_man = st.text_input("Nome do Produto:")
                    p_man = st.number_input("Preço Unitário R$:", min_value=0.0)
                    if st.button("Adicionar Manualmente"):
                        st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                        st.rerun()

        st.write("---")
        st.subheader("📋 Sua Lista")
        
        total_compra = 0.0
        
        if st.session_state.carrinho:
            for nome in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[nome]
                with st.container():
                    st.markdown(f"<div class='card-carrinho'><b>{nome}</b></div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 2, 1])
                    
                    # Campo de Preço
                    novo_preco = c1.number_input(f"Preço (R$)", value=float(item['preco']), key=f"p_{nome}", step=0.01)
                    # Campo de Quantidade
                    nova_qtd = c2.number_input(f"Qtd", value=int(item['qtd']), min_value=0, key=f"q_{nome}")
                    
                    subtotal = novo_preco * nova_qtd
                    total_compra += subtotal
                    
                    st.session_state.carrinho[nome]['preco'] = novo_preco
                    st.session_state.carrinho[nome]['qtd'] = nova_qtd
                    
                    if nova_qtd == 0:
                        del st.session_state.carrinho[nome]
                        st.rerun()
                        
                    c3.write(f"R$ {subtotal:.2f}")
                    st.write("---")

            st.metric("VALOR TOTAL", f"R$ {total_compra:.2f}")
            
            if st.button("💾 FINALIZAR E SALVAR COMPRA"):
                dados = carregar_json(ARQUIVO_DADOS)
                if "historico" not in dados: dados["historico"] = {}
                dados["historico"][st.session_state.usuario_logado] = st.session_state.carrinho
                salvar_json(ARQUIVO_DADOS, dados)
                st.success("✅ Compra salva no seu histórico!")
        else:
            st.info("O carrinho está vazio. Escaneie um produto para começar!")

    with aba2:
        st.header("📂 Minhas Listas")
        dados = carregar_json(ARQUIVO_DADOS)
        hist = dados.get("historico", {}).get(st.session_state.usuario_logado, {})
        if hist:
            for n, i in hist.items():
                st.text(f"• {i['qtd']}x {n} - R$ {i['preco']*i['qtd']:.2f}")
            if st.button("🔄 Recuperar Lista para o Carrinho"):
                st.session_state.carrinho = hist
                st.rerun()
        else:
            st.write("Você ainda não salvou nenhuma compra.")
