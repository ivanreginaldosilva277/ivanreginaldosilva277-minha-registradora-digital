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

# --- BANCO DE DADOS (LISTA SP ATUALIZADA) ---
produtos = {
    "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
    "7894900010015": {"nome": "Coca-Cola Pet 2L", "preco": 11.90},
    "7894900700046": {"nome": "Guaraná Antarctica 2L", "preco": 9.50},
    "7894900019810": {"nome": "Fanta Laranja 2L", "preco": 8.90},
    "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
    "7896000705023": {"nome": "Feijão Camil Carioca 1kg", "preco": 9.20},
    "7891080000018": {"nome": "Óleo de Soja Liza 900ml", "preco": 7.80},
    "7891150004125": {"nome": "Detergente Ypê Neutro", "preco": 2.60},
    "7891150022068": {"nome": "Sabão OMO Lavagem Perfeita", "preco": 26.90},
    "7891008121021": {"nome": "Café Pilão 500g", "preco": 24.90},
    "7891000021208": {"nome": "Leite Ninho Lata 400g", "preco": 19.50},
    # Você pode adicionar mais códigos aqui seguindo o mesmo padrão
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
        try:
            with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
        except: return {"usuarios": {}, "historico": {}}
    return {"usuarios": {}, "historico": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

def processar_codigo():
    input_usuario = st.session_state.input_scan
    cod_limpo = re.sub(r'\D', '', input_usuario)
    if cod_limpo in produtos:
        item = produtos[cod_limpo]
        n = item['nome']
        if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
        else: st.session_state.carrinho[n] = {'preco': item['preco'], 'qtd': 1}
        st.toast(f"✅ {n} adicionado!")
    else:
        st.error("Produto não cadastrado.")
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
                if login_id not in d["historico"]: d["historico"][login_id] = []
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
        st.subheader("📸 Escanear ou Digitar")
        foto = st.camera_input("Tire foto do código de barras")
        if foto:
            from pyzbar.pyzbar import decode
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            codigos = decode(img)
            if codigos:
                cod = codigos[0].data.decode('utf-8').strip()
                if cod in produtos:
                    n = produtos[cod]['nome']
                    if n in st.session_state.carrinho: st.session_state.carrinho[n]['qtd'] += 1
                    else: st.session_state.carrinho[n] = {'preco': produtos[cod]['preco'], 'qtd': 1}
                    st.success(f"✅ {n} adicionado!")
                else: st.error(f"Produto {cod} não cadastrado.")
            else: st.warning("Não consegui ler. Tente focar melhor!")

        st.text_input("Ou digite o código aqui:", key="input_scan", on_change=processar_codigo)
        
        st.write("---")
        total = 0.0
        itens_para_remover = []
        
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            sub = item['preco'] * item['qtd']
            total += sub
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(f"**{n}**")
            with col2:
                q = st.number_input("Qtd", 0, 100, int(item['qtd']), key=f"q_{n}")
                if q != item['qtd']:
                    if q == 0: itens_para_remover.append(n)
                    else: st.session_state.carrinho[n]['qtd'] = q
                    st.rerun()
            col3.write(f"R${sub:.2f}")
        
        for item in itens_para_remover: del st.session_state.carrinho[item]

        st.metric("TOTAL", f"R$ {total:.2f}")
        if st.button("💾 Salvar Compra"):
            if st.session_state.carrinho:
                dados = carregar_dados()
                nova_compra = {
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "itens": st.session_state.carrinho,
                    "total": total
                }
                dados["historico"][st.session_state.usuario_logado].append(nova_compra)
                salvar_dados(dados)
                st.session_state.carrinho = {}
                st.success("Compra salva no histórico!")
                st.rerun()
            else: st.warning("Carrinho vazio.")

    with aba2:
        dados = carregar_dados()
        user_hist = dados["historico"].get(st.session_state.usuario_logado, [])
        if user_hist:
            for compra in reversed(user_hist):
                with st.expander(f"📅 {compra['data']} - Total: R${compra['total']:.2f}"):
                    for nome, info in compra['itens'].items():
                        st.write(f"{info['qtd']}x {nome} - R${info['preco']*info['qtd']:.2f}")
        else: st.info("Nenhuma compra salva.")
