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

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .visor-caixa { background:#000; color:#0f0; padding:25px; border-radius:15px; text-align:right; font-family:monospace; border:5px solid #333; margin-bottom:20px; box-shadow: inset 0 0 10px #00ff00; }
    .stButton>button { height: 3.5em; border-radius: 12px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 PDV REGISTRADORA</h1>", unsafe_allow_html=True)
    aba1, aba2 = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR"])
    with aba1:
        with st.form("login"):
            u = st.text_input("CPF:")
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ENTRAR"):
                d = carregar_json(ARQUIVO_DADOS)
                if u in d.get("usuarios", {}) and d["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True; st.session_state.usuario_id = u; st.rerun()
                else: st.error("Erro!")
    with aba2:
        with st.form("cad"):
            nc = st.text_input("Nome:")
            cc = st.text_input("CPF:")
            sc = st.text_input("Senha:")
            if st.form_submit_button("CADASTRAR"):
                d = carregar_json(ARQUIVO_DADOS)
                d.setdefault("usuarios", {})[re.sub(r'\D', '', cc)] = {"nome": nc, "senha": sc}
                salvar_json(ARQUIVO_DADOS, d); st.success("OK!")
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none; color:white; background:#25d366; padding:15px; border-radius:10px; display:block; text-align:center; font-weight:bold; margin-top:20px;">💬 ADQUIRIR APP COM IVAN</a>', unsafe_allow_html=True)

# --- SISTEMA ---
else:
    col1, col2, col3 = st.columns(3)
    if col1.button("🛍️ BIPAR"): st.session_state.tela = "comprar"; st.rerun()
    if col2.button("🛒 CUPOM"): st.session_state.tela = "carrinho"; st.rerun()
    if col3.button("📂 FIM"): st.session_state.tela = "historico"; st.rerun()

    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor-caixa'><small>AGUARDANDO PRODUTO</small><h1>R$ 0.00</h1></div>", unsafe_allow_html=True)
        
        st.subheader("📟 ACIONAR SCANNER TRASEIRO")
        st.info("Toque no campo abaixo e escolha o ícone de 'Scanner/Câmera' que aparecerá no seu teclado.")
        
        # Este campo de texto com 'placeholder' ativa a sugestão de scanner em muitos Androids
        cod_bip = st.text_input("TOQUE PARA ESCANEAR:", key="input_bip", placeholder="[Clique para abrir o leitor]")
        
        if cod_bip:
            cod = re.sub(r'\D', '', cod_bip)
            n, p_s = buscar_produto(cod)
            if n:
                st.success(f"LIDO: {n}")
                p = st.number_input("PREÇO R$:", value=float(p_s))
                q = st.number_input("QTD:", value=1, min_value=1)
                if st.button("REGISTRAR +"):
                    st.session_state.carrinho[n] = {'preco': p, 'qtd': q}
                    mem = carregar_json(ARQUIVO_MEMORIA); mem[cod] = {"nome": n, "preco": p}
                    salvar_json(ARQUIVO_MEMORIA, mem)
                    st.session_state.input_bip = ""; st.rerun()
            else:
                st.warning("NÃO LOCALIZADO")
                n_m = st.text_input("NOME:")
                p_m = st.number_input("PREÇO:")
                if st.button("ADC. MANUAL"):
                    st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}; st.rerun()

    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        for n, i in list(st.session_state.carrinho.items()):
            c_a, c_b, c_c = st.columns([2,1,0.5])
            c_a.write(f"{i['qtd']}x {n}")
            c_b.write(f"R${i['preco']*i['qtd']:.2f}")
            if c_c.button("X", key=f"d_{n}"): del st.session_state.carrinho[n]; st.rerun()

    elif st.session_state.tela == "historico":
        st.subheader("Finalizar Venda")
        if st.sidebar.button("FECHAR CAIXA"): st.session_state.logado = False; st.rerun()
