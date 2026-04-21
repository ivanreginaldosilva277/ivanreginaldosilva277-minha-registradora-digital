import streamlit as st
import streamlit.components.v1 as components
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r") as f: return json.load(f)
        except: return {}
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f: json.dump(dados, f)

st.set_page_config(page_title="Registradora Ivan", page_icon="📟")

# --- ESTILO ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:10px; text-align:right; font-family:monospace; margin-bottom:10px; border:3px solid #444; }
    .stButton>button { width:100%; height:3em; font-weight:bold; border-radius:10px; }
    </style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela_app" not in st.session_state: st.session_state.tela_app = "bipar"

# --- TELA DE ACESSO ---
if not st.session_state.logado:
    st.title("📟 SISTEMA PDV")
    aba1, aba2 = st.tabs(["ENTRAR", "CADASTRAR"])
    with aba1:
        u = st.text_input("CPF:")
        s = st.text_input("Senha:", type="password")
        if st.button("ABRIR CAIXA"):
            d = carregar_json(ARQUIVO_DADOS)
            if u in d.get("usuarios", {}) and d["usuarios"][u]["senha"] == s:
                st.session_state.logado = True; st.session_state.usuario_id = u; st.rerun()
    with aba2:
        nc = st.text_input("Nome:")
        cc = st.text_input("CPF (Novo):")
        sc = st.text_input("Senha (Nova):")
        if st.button("CADASTRAR OPERADOR"):
            d = carregar_json(ARQUIVO_DADOS)
            d.setdefault("usuarios", {})[re.sub(r'\D', '', cc)] = {"nome": nc, "senha": sc}
            salvar_json(ARQUIVO_DADOS, d)
            st.success("Cadastrado!")

# --- SISTEMA ---
else:
    if st.session_state.tela_app == "bipar":
        st.markdown("<div class='visor'><small>CAIXA LIVRE</small><h1>R$ 0.00</h1></div>", unsafe_allow_html=True)
        
        st.subheader("📸 ESCANEADOR ATIVO")
        
        # O COMPONENTE MÁGICO QUE ABRE A CÂMERA SOZINHO
        components.html(
            """
            <script src="https://unpkg.com"></script>
            <div id="reader" style="width: 100%;"></div>
            <script>
                function onScanSuccess(decodedText) {
                    // Envia o código para o Streamlit através de um alerta ou input
                    alert("CÓDIGO LIDO: " + decodedText);
                    // Aqui o código pode ser copiado e colado no campo abaixo
                }
                let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
                html5QrcodeScanner.render(onScanSuccess);
            </script>
            """,
            height=400,
        )
        
        # Campo para receber o código do scanner
        codigo = st.text_input("Cole ou digite o código lido aqui:", key="input_cod")
        
        if codigo:
            st.success(f"Produto detectado! Informe o preço.")
            # ... lógica de busca e adição no carrinho ...

        if st.button("🛒 VER CUPOM"): st.session_state.tela_app = "carrinho"; st.rerun()

    elif st.session_state.tela_app == "carrinho":
        st.title("Cupom Atual")
        if st.button("🔙 VOLTAR"): st.session_state.tela_app = "bipar"; st.rerun()
