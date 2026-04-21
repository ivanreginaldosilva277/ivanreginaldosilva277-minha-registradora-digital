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
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name"), 0.0
    except: pass
    return None, 0.0

# --- ESTILO LIMPO E PROFISSIONAL ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; height: 3em; }
    /* Botão de Rodapé (Ação Principal) */
    div.stButton > button:first-child { background-color: #2e7d32; color: white; border: none; }
    .whatsapp-btn { background-color: #25d366; color: white !important; padding: 12px; border-radius: 8px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }
    .item-carrinho { border-bottom: 1px solid #eee; padding: 10px 0; }
    .total-fixo { background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DO SISTEMA ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- 1. TELA DE LOGIN / INÍCIO ---
if not st.session_state.logado:
    st.markdown("<h2 style='text-align: center; color: #1b5e20;'>🛒 Minha Compra Segura</h2>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">💬 Fale com o Ivan</a>', unsafe_allow_html=True)
    
    aba1, aba2 = st.tabs(["Entrar", "Criar Conta"])
    with aba1:
        with st.form("login"):
            u = st.text_input("Usuário (CPF):")
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_id = u
                    st.rerun()
                else: st.error("Login ou senha inválidos.")
    with aba2:
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (Login):")
            sc = st.text_input("Senha:")
            if st.form_submit_button("CADASTRAR"):
                id_l = re.sub(r'\D', '', cc)
                if nc and id_l and sc:
                    d = carregar_json(ARQUIVO_DADOS)
                    d.setdefault("usuarios", {})[id_l] = {"nome": nc, "senha": sc}
                    salvar_json(ARQUIVO_DADOS, d)
                    st.success("Sucesso! Use a aba Entrar.")

else:
    # --- BARRA LATERAL (OPÇÕES GERAIS) ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state.usuario_id}**")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- TELA 2: COMPRAR (SCANNER) ---
    if st.session_state.tela == "comprar":
        st.subheader("🛍️ Adicionar Produto")
        foto = st.camera_input("Aponte para o código de barras")
        
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
            if res and res:
                cod = re.sub(r'\D', '', str(res))
                nome, preco_sug = buscar_produto(cod)
                if nome:
                    st.success(f"**{nome}**")
                    p = st.number_input("Preço R$:", value=float(preco_sug), step=0.01)
                    q = st.number_input("Quantidade:", value=1, min_value=1)
                    if st.button("CONFIRMAR E SOMAR"):
                        st.session_state.carrinho[nome] = {'preco': p, 'qtd': q}
                        mem = carregar_json(ARQUIVO_MEMORIA)
                        mem[cod] = {"nome": nome, "preco": p}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.toast("Adicionado!")
                else:
                    n_m = st.text_input("Nome do Produto:")
                    p_m = st.number_input("Preço R$:", min_value=0.0)
                    if st.button("SALVAR MANUAL"):
                        st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                        st.rerun()

        st.write("---")
        # BOTÃO NO RODAPÉ
        if st.button("🛒 IR PARA O CARRINHO"):
            st.session_state.tela = "carrinho"
            st.rerun()

    # --- TELA 3: CARRINHO (REVISÃO LIMPA) ---
    elif st.session_state.tela == "carrinho":
        st.subheader("🛒 Revisar sua Lista")
        total = 0.0
        
        if not st.session_state.carrinho:
            st.info("Nenhum item adicionado.")
            if st.button("🔙 VOLTAR AO SCANNER"):
                st.session_state.tela = "comprar"; st.rerun()
        else:
            # Lista compacta de itens
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                sub = item['preco'] * item['qtd']
                total += sub
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
                col1.write(f"**{n}**")
                item['qtd'] = col2.number_input("Qtd", value=int(item['qtd']), key=f"q_{n}", min_value=0, label_visibility="collapsed")
                col3.write(f"R${sub:.2f}")
                if col4.button("❌", key=f"d_{n}"):
                    del st.session_state.carrinho[n]
                    st.rerun()
            
            st.markdown(f"<div class='total-fixo'><h3>TOTAL: R$ {total:.2f}</h3></div>", unsafe_allow_html=True)
            
            # BOTÕES NO RODAPÉ
            c1, c2 = st.columns(2)
            if c1.button("🔙 VOLTAR"): st.session_state.tela = "comprar"; st.rerun()
            if c2.button("✅ FINALIZAR"): st.session_state.tela = "historico"; st.rerun()

    # --- TELA 4: HISTÓRICO ---
    elif st.session_state.tela == "historico":
        st.subheader("📂 Finalizar e Salvar")
        
        if st.session_state.carrinho:
            total_f = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
            st.write(f"Confirma o valor de **R$ {total_f:.2f}**?")
            
            # BOTÕES NO RODAPÉ
            c1, c2 = st.columns(2)
            if c1.button("🔙 REVISAR"): st.session_state.tela = "carrinho"; st.rerun()
            if c2.button("💾 SALVAR COMPRA"):
                d = carregar_json(ARQUIVO_DADOS)
                d.setdefault("historico", {}).setdefault(st.session_state.usuario_id, []).append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"), "total": total_f
                })
                salvar_json(ARQUIVO_DADOS, d)
                st.session_state.carrinho = {}
                st.success("Salvo!")
                st.rerun()
        
        st.write("---")
        st.write("**Compras Anteriores:**")
        h = carregar_json(ARQUIVO_DADOS).get("historico", {}).get(st.session_state.usuario_id, [])
        for comp in reversed(h):
            st.write(f"📅 {comp['data']} - **R$ {comp['total']:.2f}**")
