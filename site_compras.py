import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="📟", layout="centered")

# --- FUNÇÕES DE SISTEMA ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False)

def buscar_produto(codigo):
    memoria = carregar_json(ARQUIVO_MEMORIA)
    if codigo in memoria:
        return memoria[codigo]["nome"], memoria[codigo]["preco"]
    try:
        # Link corrigido para busca na base mundial/brasileira
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name")
                if nome:
                    return nome.strip().upper(), 0.0
    except:
        pass
    return None, 0.0

# --- ESTILO VISUAL REGISTRADORA ---
st.markdown("""
    <style>
    .visor-preto {
        background:#000;
        color:#0f0;
        padding:20px;
        border-radius:15px;
        text-align:right;
        font-family:monospace;
        border:4px solid #444;
        margin-bottom:20px;
    }
    .stButton>button {
        width:100%;
        height:3.5em;
        font-weight:bold;
        border-radius:12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE TELAS ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- 1. TELA DE ACESSO ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 CAIXA REGISTRADORA</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR"])
    
    with tab1:
        with st.form("login"):
            u = st.text_input("CPF (Login):")
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ABRIR CAIXA"):
                dados = carregar_json(ARQUIVO_DADOS)
                usuarios = dados.get("usuarios", {})
                if u in usuarios and usuarios[u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_id = u
                    st.rerun()
                else:
                    st.error("Dados incorretos!")
                
    with tab2:
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF:")
            sc = st.text_input("Senha:")
            if st.form_submit_button("CADASTRAR OPERADOR"):
                id_l = re.sub(r'\D', '', cc)
                if nc and id_l and sc:
                    d = carregar_json(ARQUIVO_DADOS)
                    if "usuarios" not in d: d["usuarios"] = {}
                    d["usuarios"][id_l] = {"nome": nc, "senha": sc}
                    salvar_json(ARQUIVO_DADOS, d)
                    st.success("Cadastrado! Use a aba ACESSAR.")

# --- 2. TELAS DO APP (PÓS LOGIN) ---
else:
    c1, c2, c3 = st.columns(3)
    if c1.button("🛍️ BIPAR"): st.session_state.tela = "comprar"; st.rerun()
    if c2.button("🛒 CARRINHO"): st.session_state.tela = "carrinho"; st.rerun()
    if c3.button("📂 HISTÓRICO"): st.session_state.tela = "historico"; st.rerun()

    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor-preto'><small>CAIXA LIVRE</small><h1>BIPAR AGORA</h1></div>", unsafe_allow_html=True)
        
        # O botão abaixo abre a câmera. Lembre-se de clicar no ícone 🔄 se abrir a frontal.
        foto = st.camera_input("Aponte para o código de barras")
        
        if foto:
            bytes_data = foto.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado[0]:
                cod = str(resultado[0]).strip()
                nome, preco_sug = buscar_produto(cod)
                
                if nome:
                    st.success(f"PRODUTO: {nome}")
                    p = st.number_input("PREÇO R$:", value=float(preco_sug), step=0.01)
                    if st.button("➕ REGISTRAR"):
                        if nome in st.session_state.carrinho:
                            st.session_state.carrinho[nome]['qtd'] += 1
                        else:
                            st.session_state.carrinho[nome] = {'preco': p, 'qtd': 1}
                        
                        # Salva na memória do app para a próxima vez
                        mem = carregar_json(ARQUIVO_MEMORIA)
                        mem[cod] = {"nome": nome, "preco": p}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.toast("REGISTRADO!")
                else:
                    st.warning(f"CÓDIGO {cod} NÃO IDENTIFICADO")
                    n_m = st.text_input("Nome do Produto:")
                    p_m = st.number_input("Preço unitário:", min_value=0.0)
                    if st.button("SALVAR MANUAL"):
                        st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                        mem = carregar_json(ARQUIVO_MEMORIA)
                        mem[cod] = {"nome": n_m, "preco": p_m}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.rerun()
            else:
                st.warning("Não consegui ler as barras. Tente focar melhor ou limpar a lente!")

    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-preto'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        
        if not st.session_state.carrinho:
            st.info("Nenhum item registrado.")
        else:
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                sub = item['preco'] * item['qtd']
                col1, col2, col3 = st.columns([2, 1, 0.5])
                col1.write(f"**{n}**")
                col2.write(f"{item['qtd']}x R${sub:.2f}")
                if col3.button("X", key=f"del_{n}"):
                    del st.session_state.carrinho[n]
                    st.rerun()
            
            if st.button("🏁 FINALIZAR COMPRA"):
                d = carregar_json(ARQUIVO_DADOS)
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                if "historico" not in d: d["historico"] = {}
                d["historico"].setdefault(st.session_state.usuario_id, []).append({
                    "data": agora, "total": total
                })
                salvar_json(ARQUIVO_DADOS, d)
                st.session_state.carrinho = {}
                st.success("Compra salva no histórico!")
                st.session_state.tela = "historico"
                st.rerun()

    elif st.session_state.tela == "historico":
        st.subheader("📂 Vendas Salvas")
        h = carregar_json(ARQUIVO_DADOS).get("historico", {}).get(st.session_state.usuario_id, [])
        if not h:
            st.write("Nenhuma venda no histórico.")
        else:
            for comp in reversed(h):
                st.info(f"📅 {comp['data']} - R$ {comp['total']:.2f}")
        
        if st.sidebar.button("SAIR"):
            st.session_state.logado = False
            st.rerun()
