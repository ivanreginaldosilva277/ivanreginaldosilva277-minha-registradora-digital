import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json
from datetime import datetime

# --- CONFIGURAÇÕES ---
WHATSAPP_LINK = "https://whatsapp.com!"
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="📟", layout="centered")

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
    if codigo in memoria: return memoria[codigo]["nome"], memoria[codigo]["preco"]
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name"), 0.0
    except: pass
    return None, 0.0

# --- ESTILO "REGISTRADORA PDV" ---
st.markdown("""
    <style>
    .main { background-color: #e0e0e0; }
    .visor-caixa {
        background-color: #1a1a1a;
        color: #33ff33;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        text-align: right;
        border: 4px solid #555;
        margin-bottom: 20px;
    }
    .cupom-fiscal {
        background-color: #fff;
        padding: 15px;
        border: 1px dashed #999;
        font-family: 'Courier New', Courier, monospace;
        color: #333;
        line-height: 1.2;
    }
    .stButton>button {
        height: 4em;
        border-radius: 10px;
        font-weight: bold;
        text-transform: uppercase;
    }
    /* Botões de Rodapé */
    .btn-bipar { background-color: #2e7d32 !important; color: white !important; }
    .btn-sacola { background-color: #f9a825 !important; color: black !important; }
    .btn-fechar { background-color: #c62828 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 CAIXA REGISTRADORA</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none; color:white; background:#25d366; padding:15px; border-radius:10px; display:block; text-align:center; font-weight:bold; margin-bottom:10px;">💬 ADQUIRIR ESTE APP COM IVAN</a>', unsafe_allow_html=True)
    
    aba1, aba2 = st.tabs(["ABRIR CAIXA", "NOVO OPERADOR"])
    with aba1:
        u = st.text_input("Operador (CPF):")
        s = st.text_input("Senha:", type="password")
        if st.button("LOGON 🚀"):
            dados = carregar_json(ARQUIVO_DADOS)
            if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                st.session_state.logado = True
                st.session_state.usuario_id = u
                st.rerun()
            else: st.error("Acesso Negado.")
    with aba2:
        nc = st.text_input("Nome:")
        cc = st.text_input("CPF:")
        sc = st.text_input("Senha:")
        if st.button("CADASTRAR"):
            d = carregar_json(ARQUIVO_DADOS)
            d.setdefault("usuarios", {})[re.sub(r'\D', '', cc)] = {"nome": nc, "senha": sc}
            salvar_json(ARQUIVO_DADOS, d)
            st.success("Operador Cadastrado!")

else:
    # --- TELA 2: SCANNER (BIPAR) ---
    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor-caixa'><small>AGUARDANDO PRODUTO</small><h1>R$ 0.00</h1></div>", unsafe_allow_html=True)
        foto = st.camera_input("BIPAR CÓDIGO")
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
            if res and res:
                cod = re.sub(r'\D', '', str(res))
                nome, preco_sug = buscar_produto(cod)
                if nome:
                    st.info(f"ITEM: {nome}")
                    p = st.number_input("VALOR UNITÁRIO:", value=float(preco_sug), step=0.01)
                    q = st.number_input("QTD:", value=1, min_value=1)
                    if st.button("REGISTRAR ITEM ➕"):
                        st.session_state.carrinho[nome] = {'preco': p, 'qtd': q}
                        mem = carregar_json(ARQUIVO_MEMORIA); mem[cod] = {"nome": nome, "preco": p}
                        salvar_json(ARQUIVO_MEMORIA, mem)
                        st.toast("ITEM REGISTRADO")
                else:
                    n_m = st.text_input("NOME PRODUTO:")
                    p_m = st.number_input("PREÇO:")
                    if st.button("ADICIONAR MANUAL"):
                        st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}; st.rerun()

        st.write("---")
        if st.button("🛒 VER SUB-TOTAL", key="btn_sacola"):
            st.session_state.tela = "carrinho"; st.rerun()

    # --- TELA 3: CARRINHO (CUPOM) ---
    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='cupom-fiscal'><b>*** CUPOM DE CONFERÊNCIA ***</b><br>", unsafe_allow_html=True)
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            col1, col2, col3 = st.columns([2, 1, 0.5])
            col1.write(f"{item['qtd']}x {n[:15]}")
            col2.write(f"R${item['preco']*item['qtd']:.2f}")
            if col3.button("X", key=f"del_{n}"):
                del st.session_state.carrinho[n]; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")
        c1, c2 = st.columns(2)
        if c1.button("🔙 BIPAR +"): st.session_state.tela = "comprar"; st.rerun()
        if c2.button("🏁 FECHAR"): st.session_state.tela = "historico"; st.rerun()

    # --- TELA 4: FINALIZAR ---
    elif st.session_state.tela == "historico":
        total_f = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>TOTAL A PAGAR</small><h1>R$ {total_f:.2f}</h1></div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("🔙 REVISAR"): st.session_state.tela = "carrinho"; st.rerun()
        if c2.button("💾 SALVAR"):
            d = carregar_json(ARQUIVO_DADOS)
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            d.setdefault("historico", {}).setdefault(st.session_state.usuario_id, []).append({"data": agora, "total": total_f})
            salvar_json(ARQUIVO_DADOS, d)
            st.session_state.carrinho = {}; st.success("VENDA SALVA!"); st.rerun()
        
        st.sidebar.button("FECHAR CAIXA (SAIR)", on_click=lambda: st.session_state.update({"logado": False}))
