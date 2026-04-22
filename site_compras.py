import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from pyzbar.pyzbar import decode
from PIL import Image
from datetime import datetime

# --- CONFIGURAÇÕES ---
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
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome: return nome.strip().upper(), 0.0
    except: pass
    return None, 0.0

# --- ESTILO VISUAL REGISTRADORA ---
st.markdown("""
    <style>
    .visor-preto { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; box-shadow: inset 0 0 10px #00ff00; }
    .stButton>button { width:100%; height:3.5em; font-weight:bold; border-radius:12px; }
    </style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- LOGIN (Simplificado para o teste) ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 CAIXA REGISTRADORA</h1>", unsafe_allow_html=True)
    u = st.text_input("Login (CPF):")
    s = st.text_input("Senha:", type="password")
    if st.button("ABRIR CAIXA 🚀"):
        d = carregar_json(ARQUIVO_DADOS)
        if u in d.get("usuarios", {}) and d["usuarios"][u]["senha"] == s:
            st.session_state.logado = True; st.session_state.usuario_id = u; st.rerun()
        else: st.error("Dados incorretos!")
else:
    # --- TELAS DO APP ---
    c1, c2, c3 = st.columns(3)
    if c1.button("🛍️ BIPAR"): st.session_state.tela = "comprar"; st.rerun()
    if c2.button("🛒 CARRINHO"): st.session_state.tela = "carrinho"; st.rerun()
    if c3.button("📂 HISTÓRICO"): st.session_state.tela = "historico"; st.rerun()

    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor-preto'><small>SISTEMA PRONTO</small><h1>BIPAR AGORA</h1></div>", unsafe_allow_html=True)
        
        foto = st.camera_input("Aponte para o código e tire a foto")
        
        if foto:
            # USANDO O MOTOR PYZBAR (MUITO MAIS POTENTE)
            img_pil = Image.open(foto)
            decoded_objects = decode(img_pil)
            
            if decoded_objects:
                # Se encontrou o código na imagem
                cod = decoded_objects[0].data.decode('utf-8')
                st.success(f"📟 Código detectado: {cod}")
                
                nome, preco_sug = buscar_produto(cod)
                if nome:
                    st.info(f"📦 PRODUTO: {nome}")
                    p = st.number_input("Preço R$:", value=float(preco_sug), step=0.01)
                    if st.button("➕ REGISTRAR"):
                        st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, {'preco': p, 'qtd': 0})
                        st.session_state.carrinho[nome]['qtd'] += 1
                        mem = carregar_json(ARQUIVO_MEMORIA); mem[cod] = {"nome": nome, "preco": p}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.toast("Adicionado!")
                else:
                    st.warning("NÃO ACHEI O NOME NA INTERNET")
                    n_m = st.text_input("Nome do Produto:")
                    p_m = st.number_input("Preço unitário:", min_value=0.0)
                    if st.button("SALVAR E ADICIONAR"):
                        st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                        mem = carregar_json(ARQUIVO_MEMORIA); mem[cod] = {"nome": n_m, "preco": p_m}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.rerun()
            else:
                st.error("Não li as barras. Tente tirar a foto com o produto um pouco mais longe ou com mais luz!")

    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-preto'><small>TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        for n, i in list(st.session_state.carrinho.items()):
            col1, col2, col3 = st.columns([2, 1, 0.5])
            col1.write(f"**{n}**")
            col2.write(f"{i['qtd']}x R${i['preco']:.2f}")
            if col3.button("X", key=f"del_{n}"): del st.session_state.carrinho[n]; st.rerun()
