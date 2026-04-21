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
    .stButton>button { width: 100%; border-radius: 15px; font-weight: bold; height: 3.5em; transition: 0.3s; }
    .btn-nav { background: #1e88e5 !important; color: white !important; }
    .btn-add { background: #2e7d32 !important; color: white !important; }
    .whatsapp-btn { background: #25d366; color: white !important; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .card-item { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 6px solid #2e7d32; }
    .logo-container { text-align: center; padding: 20px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "inicio"

# --- TELA 1: INÍCIO / LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.markdown("<div class='logo-container'><span style='font-size:70px;'>🛒</span><h1 style='color:#1b5e20; margin:0;'>MINHA COMPRA SEGURA</h1><p>Seu assistente inteligente de mercado</p></div>", unsafe_allow_html=True)
    
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">🚀 QUERO ADQUIRIR ESTE APLICATIVO</a>', unsafe_allow_html=True)
    
    aba1, aba2 = st.tabs(["🔐 ACESSAR CONTA", "📝 CRIAR CADASTRO"])
    
    with aba1:
        with st.form("login"):
            u = st.text_input("CPF ou Nome de Usuário:").strip().lower()
            s = st.text_input("Sua Senha:", type="password")
            if st.form_submit_button("ENTRAR NO APP 🚀"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_id = u
                    st.session_state.tela = "comprar"
                    st.rerun()
                else: st.error("Dados incorretos!")

    with aba2:
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (Login):")
            sc = st.text_input("Crie uma Senha:")
            if st.form_submit_button("FINALIZAR CADASTRO ✅"):
                id_limpo = re.sub(r'\D', '', cc)
                if nc and id_limpo and sc:
                    d = carregar_json(ARQUIVO_DADOS)
                    d.setdefault("usuarios", {})[id_limpo] = {"nome": nc, "senha": sc}
                    salvar_json(ARQUIVO_DADOS, d)
                    st.success("Cadastro realizado! Entre na aba ACESSAR.")

else:
    # Navegação entre as telas 2, 3 e 4
    col_n1, col_n2, col_n3 = st.columns(3)
    if col_n1.button("🛍️ COMPRAR"): st.session_state.tela = "comprar"; st.rerun()
    if col_n2.button("🛒 CARRINHO"): st.session_state.tela = "carrinho"; st.rerun()
    if col_n3.button("📂 HISTÓRICO"): st.session_state.tela = "historico"; st.rerun()

    # --- TELA 2: COMPRAR (SCANNER) ---
    if st.session_state.tela == "comprar":
        st.header("🛍️ Escanear Produto")
        foto = st.camera_input("Aponte para o código de barras")
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
            if res and res:
                cod = re.sub(r'\D', '', str(res))
                nome, preco_sug = buscar_produto(cod)
                if nome:
                    st.success(f"PRODUTO: {nome}")
                    p = st.number_input("Preço Unitário R$:", value=float(preco_sug), step=0.01)
                    q = st.number_input("Quantidade:", value=1, min_value=1)
                    if st.button("➕ ADICIONAR AO CARRINHO", key="add"):
                        st.session_state.carrinho[nome] = {'preco': p, 'qtd': q}
                        mem = carregar_json(ARQUIVO_MEMORIA)
                        mem[cod] = {"nome": nome, "preco": p}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.toast("✅ Item adicionado!")
                else:
                    st.warning("Produto não identificado.")
                    n_m = st.text_input("Nome do Produto:")
                    p_m = st.number_input("Preço R$:", min_value=0.0)
                    if st.button("Salvar e Adicionar Manual"):
                        st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                        st.rerun()
        
        if st.session_state.carrinho:
            st.write("---")
            if st.button("➡️ VER CARRINHO AGORA", key="go_cart"):
                st.session_state.tela = "carrinho"; st.rerun()

    # --- TELA 3: CARRINHO (REVISÃO + - X) ---
    elif st.session_state.tela == "carrinho":
        st.header("🛒 Revisão da Compra")
        total = 0.0
        if not st.session_state.carrinho:
            st.info("O carrinho está vazio!")
        else:
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                sub = item['preco'] * item['qtd']
                total += sub
                with st.container():
                    st.markdown(f"<div class='card-item'><b>{n}</b><br>Preço: R$ {item['preco']:.2f} | Subtotal: R$ {sub:.2f}</div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1,2,1,1])
                    if c1.button("➖", key=f"m_{n}"):
                        if item['qtd'] > 1: st.session_state.carrinho[n]['qtd'] -= 1; st.rerun()
                    c2.markdown(f"<h4 style='text-align:center;'>Qtd: {item['qtd']}</h4>", unsafe_allow_html=True)
                    if c3.button("➕", key=f"p_{n}"):
                        st.session_state.carrinho[n]['qtd'] += 1; st.rerun()
                    if c4.button("❌", key=f"d_{n}"):
                        del st.session_state.carrinho[n]; st.rerun()
            
            st.divider()
            st.metric("VALOR TOTAL", f"R$ {total:.2f}")
            if st.button("➡️ FINALIZAR E SALVAR COMPRA"):
                st.session_state.tela = "historico"; st.rerun()

    # --- TELA 4: HISTÓRICO ---
    elif st.session_state.tela == "historico":
        st.header("📂 Finalizar e Histórico")
        if st.session_state.carrinho:
            total_f = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
            st.subheader(f"Total desta compra: R$ {total_f:.2f}")
            col_h1, col_h2 = st.columns(2)
            if col_h1.button("🔙 VOLTAR AO CARRINHO"): st.session_state.tela = "carrinho"; st.rerun()
            if col_h2.button("💾 CONFIRMAR E SALVAR"):
                d = carregar_json(ARQUIVO_DADOS)
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                d.setdefault("historico", {}).setdefault(st.session_state.usuario_id, []).append({"data": agora, "total": total_f})
                salvar_json(ARQUIVO_DADOS, d)
                st.session_state.carrinho = {}
                st.success("✅ Compra arquivada com sucesso!")
                st.rerun()
        
        st.write("---")
        st.subheader("Compras Guardadas")
        h = carregar_json(ARQUIVO_DADOS).get("historico", {}).get(st.session_state.usuario_id, [])
        if h:
            for comp in reversed(h):
                st.info(f"📅 {comp['data']} - Valor: R$ {comp['total']:.2f}")
        else: st.write("Nenhuma compra salva ainda.")
        
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()
