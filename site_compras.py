import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime

# --- CONFIGURAÇÕES IVAN ---
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

def buscar_produto(codigo):
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

# --- ESTILO VISUAL PREMIUM ---
st.markdown("""
    <style>
    @import url('https://googleapis.com');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: 700; height: 3.5em; border: none; transition: 0.3s; }
    
    /* Botões Específicos */
    div.stButton > button:first-child { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; }
    .btn-perigo button { background: #fee2e2 !important; color: #dc2626 !important; border: 1px solid #fecaca !important; }
    
    .whatsapp-btn { background: #25d366; color: white !important; padding: 18px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(37,211,102,0.2); }
    
    .card-item { background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px; border: 1px solid #e2e8f0; }
    .logo-container { text-align: center; padding: 40px 20px; background: white; border-radius: 0 0 40px 40px; margin: -100px -20px 40px -20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .total-container { background: #1e293b; color: white; padding: 20px; border-radius: 16px; text-align: center; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- TELA 1: LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.markdown("<div class='logo-container'><span style='font-size:80px;'>🛒</span><h1 style='color:#064e3b; margin-top:10px; font-weight:900;'>MINHA COMPRA SEGURA</h1><p style='color:#64748b;'>Seu dinheiro sob controle em cada corredor.</p></div>", unsafe_allow_html=True)
    
    aba1, aba2 = st.tabs(["👋 ACESSAR CONTA", "📝 CRIAR CADASTRO"])
    
    with aba1:
        with st.form("login"):
            u = st.text_input("Seu CPF ou Login:").strip().lower()
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ENTRAR NO APP 🚀"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_id = u
                    st.rerun()
                else: st.error("Dados incorretos!")
        st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">🚀 QUERO TER ESSE APLICATIVO</a>', unsafe_allow_html=True)

    with aba2:
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (será seu login):")
            sc = st.text_input("Crie uma Senha:")
            if st.form_submit_button("FINALIZAR CADASTRO ✅"):
                id_l = re.sub(r'\D', '', cc)
                if nc and id_l and sc:
                    d = carregar_json(ARQUIVO_DADOS)
                    d.setdefault("usuarios", {})[id_l] = {"nome": nc, "senha": sc}
                    salvar_json(ARQUIVO_DADOS, d)
                    st.success("Cadastro realizado! Mude para a aba ACESSAR.")

else:
    # NAVEGAÇÃO ELEGANTE
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario_id}")
    st.sidebar.divider()
    if st.sidebar.button("🛍️ BIPAR PRODUTO"): st.session_state.tela = "comprar"; st.rerun()
    if st.sidebar.button("🛒 MEU CARRINHO"): st.session_state.tela = "carrinho"; st.rerun()
    if st.sidebar.button("📂 HISTÓRICO"): st.session_state.tela = "historico"; st.rerun()
    st.sidebar.divider()
    if st.sidebar.button("🔒 SAIR"): st.session_state.logado = False; st.rerun()

    # --- TELA 2: COMPRAR ---
    if st.session_state.tela == "comprar":
        st.title("🛍️ Escanear")
        foto = st.camera_input("Posicione o código de barras no centro")
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
            if res and res:
                cod = re.sub(r'\D', '', str(res))
                nome, preco_sug = buscar_produto(cod)
                with st.container():
                    st.markdown(f"<div class='card-item'>📝 <b>PRODUTO LIDO:</b> {nome if nome else 'Não Identificado'}</div>", unsafe_allow_html=True)
                    if nome:
                        p = st.number_input("Preço Unitário R$:", value=float(preco_sug), step=0.01)
                        q = st.number_input("Quantidade:", value=1, min_value=1)
                        if st.button("➕ ADICIONAR AO CARRINHO"):
                            st.session_state.carrinho[nome] = {'preco': p, 'qtd': q}
                            mem = carregar_json(ARQUIVO_MEMORIA)
                            mem[cod] = {"nome": nome, "preco": p}
                            salvar_json(ARQUIVO_MEMORIA, mem)
                            st.toast("Item adicionado com sucesso!")
                    else:
                        n_m = st.text_input("Nome do Produto:")
                        p_m = st.number_input("Preço R$:", min_value=0.0)
                        if st.button("SALVAR E ADICIONAR"):
                            st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                            st.rerun()

    # --- TELA 3: CARRINHO ---
    elif st.session_state.tela == "carrinho":
        st.title("🛒 Meu Carrinho")
        total = 0.0
        if not st.session_state.carrinho:
            st.info("O seu carrinho ainda está vazio.")
        else:
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                sub = item['preco'] * item['qtd']
                total += sub
                with st.markdown(f"<div class='card-item'><b>{n}</b><br><small>R$ {item['preco']:.2f} x {item['qtd']} un</small><br><b>Subtotal: R$ {sub:.2f}</b></div>", unsafe_allow_html=True):
                    c1, c2, c3 = st.columns([1,1,1])
                    if c1.button("➖", key=f"m_{n}"):
                        if item['qtd'] > 1: st.session_state.carrinho[n]['qtd'] -= 1; st.rerun()
                    if c2.button("➕", key=f"p_{n}"):
                        st.session_state.carrinho[n]['qtd'] += 1; st.rerun()
                    with c3:
                        st.markdown("<div class='btn-perigo'>", unsafe_allow_html=True)
                        if st.button("❌", key=f"d_{n}"):
                            del st.session_state.carrinho[n]; st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='total-container'><h1>VALOR TOTAL: R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
            if st.button("➡️ TUDO CERTO, FINALIZAR"):
                st.session_state.tela = "historico"; st.rerun()

    # --- TELA 4: HISTÓRICO ---
    elif st.session_state.tela == "historico":
        st.title("📂 Compras")
        if st.session_state.carrinho:
            total_f = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
            st.markdown(f"<div class='card-item' style='background:#f0fdf4;'>✅ <b>Compra Atual: R$ {total_f:.2f}</b><br>Deseja salvar esta lista agora?</div>", unsafe_allow_html=True)
            if st.button("💾 CONFIRMAR E SALVAR AGORA"):
                d = carregar_json(ARQUIVO_DADOS)
                d.setdefault("historico", {}).setdefault(st.session_state.usuario_id, []).append({"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "total": total_f})
                salvar_json(ARQUIVO_DADOS, d)
                st.session_state.carrinho = {}
                st.success("Salvo com sucesso!")
                st.rerun()
        
        st.subheader("Compras Guardadas")
        h = carregar_json(ARQUIVO_DADOS).get("historico", {}).get(st.session_state.usuario_id, [])
        for comp in reversed(h):
            st.info(f"📅 {comp['data']} - Total: R$ {comp['total']:.2f}")
