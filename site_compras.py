import streamlit as st
import re
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- BANCO DE DADOS ---
produtos = {
    "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
    "7894900010015": {"nome": "Coca-Cola Pet 2L", "preco": 11.90},
    "7894900700046": {"nome": "Guaraná Antarctica 2L", "preco": 9.50},
    "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
    "7896000705023": {"nome": "Feijão Camil 1kg", "preco": 9.20},
    "7891000100170": {"nome": "Chá Leão Hortelã", "preco": 3.50},
    "10": {"nome": "Pão Francês (Un)", "preco": 0.50}
}

# --- ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- FUNÇÃO PARA PROCESSAR CÓDIGO ---
def processar_codigo():
    input_usuario = st.session_state.input_scan
    cod_limpo = re.sub(r'\D', '', input_usuario)
    if cod_limpo in produtos:
        item = produtos[cod_limpo]
        n = item['nome']
        if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
        else: st.session_state.carrinho[n] = {'preco': item['preco'], 'qtd': 1}
        st.toast(f"✅ {n} adicionado!")
    st.session_state.input_scan = ""

# --- TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://wa.me{WHATSAPP_CONTATO}" class="whatsapp-btn">💬 Fale com o Ivan</a>', unsafe_allow_html=True)
    with st.form("login_form"):
        u_log = st.text_input("Login (CPF ou Nome):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR 🚀"):
            dados = carregar_dados()
            if u_log in dados["usuarios"] and dados["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Dados incorretos.")
    if st.button("Cadastrar Nova Conta 📝"):
        st.session_state.tela = "cadastro"
        st.rerun()

# --- TELA DE CADASTRO ---
elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro Novo")
    with st.form("c_form"):
        n_c = st.text_input("Nome:")
        c_c = st.text_input("CPF (Login):")
        s_c = st.text_input("Senha:", type="password")
        if st.form_submit_button("CADASTRAR ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                d = carregar_dados()
                exp = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                d["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": exp, "pago": False}
                d["historico"][login_id] = {}
                salvar_dados(d)
                st.success("Sucesso! Volte ao login.")
            else: st.error("Preencha tudo.")
    if st.button("⬅️ Voltar"):
        st.session_state.tela = "login"
        st.rerun()

# --- TELA DO APLICATIVO ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}")
    if st.sidebar.button("⬅️ Sair"):
        st.session_state.tela = "login"
        st.rerun()

    aba1, aba2 = st.tabs(["🛒 Compra", "📂 Histórico"])

    with aba1:
        st.subheader("📸 Escanear por Foto")
        foto = st.camera_input("Tire foto do código de barras")
        if foto:
            bytes_data = foto.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            ok, pontos, codigos, tipos = detector.detectAndDecode(img)
            if ok and codigos:
                # Se ler uma lista, pega o primeiro item. Se ler string, usa direto.
                cod = codigos[0] if isinstance(codigos, (list, np.ndarray)) else codigos
                if cod in produtos:
                    n = produtos[cod]['nome']
                    if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                    else: st.session_state.carrinho[n] = {'preco': produtos[cod]['preco'], 'qtd': 1}
                    st.success(f"✅ {n} lido!")
            else: st.warning("Não consegui ler as barras. Tente focar melhor!")

        st.write("---")
        st.subheader("⌨️ Digitar Código")
        st.text_input("Ou digite aqui:", key="input_scan", on_change=processar_codigo)
        
        total = 0
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            sub = item['preco'] * item['qtd']
            total += sub
            col1, col2, col3 = st.columns()
            col1.write(f"**{n}**")
            with col2:
                q = st.number_input("Qtd", 0, 100, int(item['qtd']), key=f"q_{n}")
                if q != item['qtd']:
                    if q == 0: del st.session_state.carrinho[n]
                    else: st.session_state.carrinho[n]['qtd'] = q
                    st.rerun()
            col3.write(f"R${sub:.2f}")
        
        st.metric("TOTAL", f"R$ {total:.2f}")
