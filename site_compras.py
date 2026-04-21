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

# --- FUNÇÕES DE DADOS E BUSCA ---
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

# --- ESTILO VISUAL "CAIXA PROFISSIONAL" ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .visor-caixa {
        background-color: #000;
        color: #00ff00;
        padding: 25px;
        border-radius: 15px;
        font-family: 'monospace';
        text-align: right;
        border: 5px solid #333;
        margin-bottom: 20px;
        box-shadow: inset 0 0 10px #00ff00;
    }
    .cupom-estilo {
        background-color: #fff;
        padding: 20px;
        border: 1px dashed #000;
        font-family: 'Courier New', Courier, monospace;
        color: #000;
    }
    .stButton>button { height: 3.5em; border-radius: 12px; font-weight: bold; width: 100%; }
    .btn-bipar { background-color: #2e7d32 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "tela" not in st.session_state: st.session_state.tela = "comprar"

# --- LOGIN ---
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>📟 PDV REGISTRADORA</h1>", unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Operador (CPF):")
        s = st.text_input("Senha:", type="password")
        if st.form_submit_button("ABRIR CAIXA 🚀"):
            dados = carregar_json(ARQUIVO_DADOS)
            if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                st.session_state.logado = True; st.session_state.usuario_id = u; st.rerun()
            else: st.error("Acesso Negado")
    st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none; color:white; background:#25d366; padding:15px; border-radius:10px; display:block; text-align:center; font-weight:bold;">💬 ADQUIRIR ESTE APP</a>', unsafe_allow_html=True)

else:
    # --- TELA 1: BIPAR PRODUTO ---
    if st.session_state.tela == "comprar":
        st.markdown("<div class='visor-caixa'><small>CAIXA LIVRE</small><h1>R$ 0.00</h1></div>", unsafe_allow_html=True)
        
        st.subheader("📟 BIPAR AGORA")
        # Este campo é o segredo: ao clicar nele, use o scanner do seu teclado Samsung
        codigo_bipado = st.text_input("Clique aqui e use o Scanner do Teclado:", key="input_bip")
        
        if codigo_bipado:
            cod = re.sub(r'\D', '', codigo_bipado)
            nome, preco_sug = buscar_produto(cod)
            if nome:
                st.success(f"PRODUTO: {nome}")
                p = st.number_input("PREÇO R$:", value=float(preco_sug), step=0.01)
                q = st.number_input("QUANTIDADE:", value=1, min_value=1)
                if st.button("CONFIRMAR E REGISTRAR ➕"):
                    st.session_state.carrinho[nome] = {'preco': p, 'qtd': q}
                    mem = carregar_json(ARQUIVO_MEMORIA); mem[cod] = {"nome": nome, "preco": p}
                    salvar_json(ARQUIVO_MEMORIA, mem)
                    st.session_state.input_bip = "" # Limpa para o próximo bip
                    st.toast("REGISTRADO!")
            else:
                st.warning("PRODUTO NÃO CADASTRADO")
                n_m = st.text_input("NOME:")
                p_m = st.number_input("PREÇO R$:")
                if st.button("ADICIONAR MANUAL"):
                    st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}; st.rerun()

        st.write("---")
        if st.button("🛒 VER CUPOM ATUAL"): st.session_state.tela = "carrinho"; st.rerun()

    # --- TELA 2: CUPOM (CARRINHO) ---
    elif st.session_state.tela == "carrinho":
        total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>SUB-TOTAL</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='cupom-estilo'><b>*** CONFERÊNCIA DE ITENS ***</b><br>", unsafe_allow_html=True)
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            col1, col2, col3 = st.columns([2, 1, 0.5])
            col1.write(f"{item['qtd']}x {n}")
            col2.write(f"R${item['preco']*item['qtd']:.2f}")
            if col3.button("X", key=f"d_{n}"): del st.session_state.carrinho[n]; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")
        c1, c2 = st.columns(2)
        if c1.button("🔙 VOLTAR"): st.session_state.tela = "comprar"; st.rerun()
        if c2.button("🏁 FECHAR COMPRA"): st.session_state.tela = "historico"; st.rerun()

    # --- TELA 3: FINALIZAR ---
    elif st.session_state.tela == "historico":
        total_f = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
        st.markdown(f"<div class='visor-caixa'><small>TOTAL FINAL</small><h1>R$ {total_f:.2f}</h1></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        if col1.button("🔙 REVISAR"): st.session_state.tela = "carrinho"; st.rerun()
        if col2.button("💾 SALVAR NO HISTÓRICO"):
            d = carregar_json(ARQUIVO_DADOS)
            d.setdefault("historico", {}).setdefault(st.session_state.usuario_id, []).append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"), "total": total_f
            })
            salvar_json(ARQUIVO_DADOS, d)
            st.session_state.carrinho = {}; st.success("SALVO!"); st.rerun()
        
        if st.sidebar.button("FECHAR CAIXA"): st.session_state.logado = False; st.rerun()
