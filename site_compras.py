import streamlit as st
import requests
import re
import os
import json
from datetime import datetime

# --- CONFIGURAÇÕES IVAN ---
WHATSAPP_LINK = "https://whatsapp.com!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="📟", layout="centered")

# --- FUNÇÕES DE DADOS ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False)

def buscar_produto(codigo):
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria: return memoria[codigo]["nome"], memoria[codigo]["preco"]
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name"), 0.0
    except: pass
    return None, 0.0

# --- ESTILO VISUAL "CAIXA PROFISSIONAL" ---
st.markdown("""
    <style>
    .visor-caixa {
        background-color: #000;
        color: #00ff00;
        padding: 25px;
        border-radius: 15px;
        font-family: 'monospace';
        text-align: right;
        border: 5px solid #333;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px #00ff00;
    }
    .stButton>button { height: 3.5em; border-radius: 12px; font-weight: bold; width: 100%; }
    .whatsapp-btn { background-color: #25d366; color: white !important; padding: 15px; border-radius: 10px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela_login" not in st.session_state: st.session_state.tela_login = "menu"

# --- TELA INICIAL (LOGIN / CADASTRO) ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 SISTEMA REGISTRADORA</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 ADQUIRIR ESTE APLICATIVO</a>', unsafe_allow_html=True)
    
    if st.session_state.tela_login == "menu":
        if st.button("🔐 ABRIR MEU CAIXA (LOGIN)"):
            st.session_state.tela_login = "entrar"
            st.rerun()
        if st.button("📝 CRIAR CONTA DE OPERADOR (CADASTRO)"):
            st.session_state.tela_login = "cadastrar"
            st.rerun()

    elif st.session_state.tela_login == "entrar":
        st.subheader("Acessar Sistema")
        with st.form("login_form"):
            u = st.text_input("CPF do Operador:")
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("LOGON 🚀"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_id = u
                    st.rerun()
                else: st.error("Acesso Negado. Verifique os dados.")
        if st.button("🔙 Voltar"):
            st.session_state.tela_login = "menu"
            st.rerun()

    elif st.session_state.tela_login == "cadastrar":
        st.subheader("Novo Cadastro")
        with st.form("cad_form"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (Login):")
            sc = st.text_input("Senha:")
            if st.form_submit_button("FINALIZAR CADASTRO ✅"):
                login_id = re.sub(r'\D', '', cc)
                if nc and login_id and sc:
                    d = carregar_json(ARQUIVO_DADOS)
                    if "usuarios" not in d: d["usuarios"] = {}
                    d["usuarios"][login_id] = {"nome": nc, "senha": sc}
                    salvar_json(ARQUIVO_DADOS, d)
                    st.success("Operador cadastrado com sucesso!")
        if st.button("🔙 Voltar"):
            st.session_state.tela_login = "menu"
            st.rerun()

# --- SISTEMA APÓS LOGIN ---
else:
    # (Mantém o mesmo código da Registradora que te passei antes)
    if "tela_app" not in st.session_state: st.session_state.tela_app = "bipar"
    
    if st.session_state.tela_app == "bipar":
        st.markdown("<div class='visor-caixa'><small>CAIXA LIVRE</small><h1>R$ 0.00</h1></div>", unsafe_allow_html=True)
        st.subheader("📟 BIPAR PRODUTO")
        codigo = st.text_input("Aponte o Scanner do Celular aqui:", key="bip")
        if codigo:
            cod = re.sub(r'\D', '', codigo)
            n, p_s = buscar_produto(cod)
            if n:
                st.success(f"LIDO: {n}")
                p = st.number_input("PREÇO R$:", value=float(p_s))
                q = st.number_input("QTD:", value=1, min_value=1)
                if st.button("REGISTRAR ➕"):
                    st.session_state.carrinho[n] = {'preco': p, 'qtd': q}
                    st.toast("OK!")
            else:
                st.warning("NÃO CADASTRADO")
                n_m = st.text_input("NOME:")
                p_m = st.number_input("PREÇO:")
                if st.button("ADICIONAR"):
                    st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                    st.rerun()
        if st.button("🛒 VER CUPOM"): st.session_state.tela_app = "carrinho"; st.rerun()

    elif st.session_state.tela_app == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        for n, i in list(st.session_state.carrinho.items()):
            c1, c2, c3 = st.columns([2,1,0.5])
            c1.write(f"{i['qtd']}x {n[:15]}")
            c2.write(f"R${i['preco']*i['qtd']:.2f}")
            if c3.button("X", key=f"d_{n}"): del st.session_state.carrinho[n]; st.rerun()
        if st.button("🔙 VOLTAR"): st.session_state.tela_app = "bipar"; st.rerun()
        if st.button("🏁 FECHAR"): st.session_state.tela_app = "historico"; st.rerun()

    elif st.session_state.tela_app == "historico":
        st.title("Finalizar Venda")
        if st.sidebar.button("SAIR"): st.session_state.logado = False; st.rerun()
