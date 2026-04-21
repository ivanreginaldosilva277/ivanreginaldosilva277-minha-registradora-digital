import streamlit as st
import streamlit.components.v1 as components
import requests
import re
import json
import os
from datetime import datetime

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"
WHATSAPP_LINK = "https://whatsapp.com!"

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE BUSCA ---
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

def carregar_json(arq):
    if os.path.exists(arq):
        with open(arq, "r") as f: return json.load(f)
    return {}

# --- ESTILO ---
st.markdown("<style>.visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:3px solid #444; }</style>", unsafe_allow_html=True)

# --- ESTADOS ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "inicio"

# --- LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.title("🛒 Minha Compra Segura")
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" style="background:#25d366; color:white; padding:15px; border-radius:10px; display:block; text-align:center; font-weight:bold; text-decoration:none; margin-bottom:20px;">🚀 ADQUIRIR APP COM IVAN</a>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 CADASTRO"])
    with t1:
        u = st.text_input("CPF:")
        s = st.text_input("Senha:", type="password")
        if st.button("ENTRAR"):
            d = carregar_json(ARQUIVO_DADOS)
            if u in d.get("usuarios", {}) and d["usuarios"][u]["senha"] == s:
                st.session_state.logado = True; st.session_state.usuario_id = u; st.rerun()
    with t2:
        nc = st.text_input("Nome:")
        cc = st.text_input("CPF (Novo):")
        sc = st.text_input("Senha (Nova):")
        if st.button("CADASTRAR"):
            d = carregar_json(ARQUIVO_DADOS); d.setdefault("usuarios", {})[re.sub(r'\D', '', cc)] = {"nome": nc, "senha": sc}
            with open(ARQUIVO_DADOS, "w") as f: json.dump(d, f); st.success("OK! Vá em LOGIN.")

else:
    # --- NAVEGAÇÃO ---
    c1, c2, c3 = st.columns(3)
    if c1.button("🛍️ BIPAR"): st.session_state.tela = "comprar"; st.rerun()
    if c2.button("🛒 CUPOM"): st.session_state.tela = "carrinho"; st.rerun()
    if c3.button("📂 FIM"): st.session_state.tela = "historico"; st.rerun()

    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor'><small>SCANNER ATIVO</small><h1>BIPAR AGORA</h1></div>", unsafe_allow_html=True)
        
        # SCANNER AUTOMÁTICO VIA JAVASCRIPT (O MELHOR QUE EXISTE)
        components.html(
            """
            <script src="https://unpkg.com"></script>
            <div id="reader" style="width:100%; border-radius:10px; overflow:hidden;"></div>
            <script>
                function onScanSuccess(decodedText) {
                    window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'cod_bip', value: decodedText}, '*');
                }
                let config = { fps: 15, qrbox: {width: 250, height: 150}, aspectRatio: 1.0 };
                let html5QrcodeScanner = new Html5QrcodeScanner("reader", config, false);
                html5QrcodeScanner.render(onScanSuccess);
            </script>
            """,
            height=400,
        )

        cod_final = st.text_input("Código lido:", key="cod_bip")

        if cod_final:
            nome = buscar_nome(cod_final)
            if nome:
                st.success(f"📦 {nome}")
                preco = st.number_input("Preço R$:", min_value=0.0, step=0.01)
                if st.button("ADICIONAR"):
                    st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, {'preco': preco, 'qtd': 0})
                    st.session_state.carrinho[nome]['qtd'] += 1; st.toast("Adicionado!"); st.rerun()
            else:
                st.warning("Produto não achado. Digite o nome:")
                n_m = st.text_input("Nome:")
                p_m = st.number_input("Preço:", min_value=0.0)
                if st.button("SALVAR"):
                    st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}; st.rerun()

    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        for n, i in list(st.session_state.carrinho.items()):
            col1, col2, col3 = st.columns([2, 1, 0.5])
            col1.write(f"**{n}**")
            col2.write(f"{i['qtd']}x R${i['preco']:.2f}")
            if col3.button("X", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()

    elif st.session_state.tela == "historico":
        st.title("Finalizar Compra")
        if st.sidebar.button("FECHAR CAIXA"): st.session_state.logado = False; st.rerun()
