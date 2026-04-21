import streamlit as st
import re
import json
import os
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÃO PARA BUSCAR NOME NA INTERNET ---
def buscar_nome_internet(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == 1:
                return dados["product"].get("product_name", "Produto Desconhecido")
    except:
        return None
    return None

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}, "produtos_novos": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

# Produtos base para teste rápido
produtos_base = {
    "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
    "7891000100170": {"nome": "Chá Leão Hortelã", "preco": 3.50}
}

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://wa.me{WHATSAPP_CONTATO}" style="background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px;">💬 Fale com o Ivan</a>', unsafe_allow_html=True)
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
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado:
                cod = str(resultado).strip()
                cod = re.sub(r'\W+', '', cod)
                
                dados_globais = carregar_dados()
                nome_p = None
                preco_p = 0.0

                if cod in produtos_base:
                    nome_p = produtos_base[cod]['nome']
                    preco_p = produtos_base[cod]['preco']
                elif cod in dados_globais["produtos_novos"]:
                    nome_p = dados_globais["produtos_novos"][cod]['nome']
                    preco_p = dados_globais["produtos_novos"][cod]['preco']
                else:
                    with st.spinner("Buscando na internet..."):
                        nome_p = buscar_nome_internet(cod)
                
                if nome_p:
                    st.write(f"🔎 **Encontrado:** {nome_p}")
                    p_atual = st.number_input(f"Preço R$:", value=preco_p, key=f"p_{cod}")
                    if st.button(f"Confirmar {nome_p}"):
                        dados_globais["produtos_novos"][cod] = {"nome": nome_p, "preco": p_atual}
                        salvar_dados(dados_globais)
                        if nome_p in st.session_state.carrinho:
                            st.session_state.carrinho[nome_p]['qtd'] += 1
                        else:
                            st.session_state.carrinho[nome_p] = {'preco': p_atual, 'qtd': 1}
                        st.success("Adicionado!")
                        st.rerun()
                else:
                    st.warning(f"Código {cod} não encontrado. Digite manualmente.")
            else:
                st.warning("Não consegui ler. Tente focar melhor!")

        st.write("---")
        total = 0
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x {n}** - R$ {sub:.2f}")
        st.metric("TOTAL", f"R$ {total:.2f}")
