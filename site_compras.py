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

# --- ESTILO VISUAL TURBINADO ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 20px; background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%); color: white; height: 3.5em; font-weight: bold; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: 0.3s; }}
    .stButton>button:hover {{ transform: scale(1.02); }}
    .whatsapp-btn {{ background: linear-gradient(135deg, #25d366 0%, #128c7e 100%); color: white !important; padding: 18px; border-radius: 20px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin: 20px 0; box-shadow: 0 4px 15px rgba(37,211,102,0.3); font-size: 18px; }}
    .logo-container {{ text-align: center; padding: 20px; background: white; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 30px; }}
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "usuario_nome" not in st.session_state: st.session_state.usuario_nome = ""

# --- 1. TELA INICIAL / LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.markdown("""
        <div class="logo-container">
            <span style="font-size: 80px;">🛒</span>
            <h1 style="color: #1b5e20; margin:0;">MINHA COMPRA SEGURA</h1>
            <p style="color: #666;">O controle total do seu bolso na hora do mercado.</p>
        </div>
    """, unsafe_allow_html=True)
    
    aba_entrar, aba_cadastrar = st.tabs(["🔑 ENTRAR NO APP", "📝 CRIAR CONTA"])
    
    with aba_entrar:
        with st.form("login"):
            u = st.text_input("Seu Login (CPF):").strip().lower()
            s = st.text_input("Sua Senha:", type="password")
            if st.form_submit_button("ACESSAR MINHA CONTA 🚀"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_nome = u
                    st.rerun()
                else: st.error("Login ou senha incorretos.")
        
        st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" class="whatsapp-btn">🚀 QUERO ADQUIRIR ESTE APP</a>', unsafe_allow_html=True)

    with aba_cadastrar:
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (será seu login):")
            sc = st.text_input("Crie uma Senha:")
            if st.form_submit_button("FINALIZAR MEU CADASTRO ✅"):
                login_id = re.sub(r'\D', '', cc)
                if nc and login_id and sc:
                    dados = carregar_json(ARQUIVO_DADOS)
                    if "usuarios" not in dados: dados["usuarios"] = {}
                    dados["usuarios"][login_id] = {"nome": nc, "senha": sc, "historico": []}
                    salvar_json(ARQUIVO_DADOS, dados)
                    st.success("Conta criada! Vá em 'ENTRAR' para acessar.")
else:
    # MENU LATERAL
    st.sidebar.markdown(f"### 👤 Olá, {st.session_state.usuario_nome}")
    menu = st.sidebar.radio("Navegação", ["🛍️ Bipar Produto", "🛒 Ver Carrinho", "📂 Histórico de Gastos"])
    
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.logado = False
        st.rerun()

    # --- 2. TELA DE COMPRAS ---
    if menu == "🛍️ Bipar Produto":
        st.header("🛍️ Escanear Agora")
        foto = st.camera_input("Aponte para as barras do produto")
        
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.barcode.BarcodeDetector()
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado:
                cod = re.sub(r'\D', '', str(resultado))
                nome, preco_sug = buscar_produto(cod)
                
                if nome:
                    st.success(f"PRODUTO ENCONTRADO: {nome}")
                    p_venda = st.number_input("Preço Unitário R$:", value=float(preco_sug), step=0.01)
                    q_venda = st.number_input("Quantas unidades?", value=1, min_value=1)
                    if st.button("➕ ADICIONAR AO CARRINHO"):
                        st.session_state.carrinho[nome] = {'preco': p_venda, 'qtd': q_venda}
                        memoria = carregar_json(ARQUIVO_MEMORIA)
                        memoria[cod] = {"nome": nome, "preco": p_venda}
                        salvar_json(ARQUIVO_MEMORIA, memoria)
                        st.toast(f"{nome} adicionado!")
                else:
                    st.warning("Não achei o nome na internet.")
                    n_man = st.text_input("Digite o Nome do Produto:")
                    p_man = st.number_input("Digite o Preço R$:", min_value=0.0)
                    if st.button("Salvar Manualmente"):
                        st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': 1}
                        st.rerun()

    # --- 3. TELA DO CARRINHO ---
    elif menu == "🛒 Ver Carrinho":
        st.header("🛒 Seu Carrinho")
        total = 0.0
        if st.session_state.carrinho:
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                sub = item['preco'] * item['qtd']
                with st.expander(f"{n} - R$ {sub:.2f}"):
                    c1, c2 = st.columns(2)
                    nova_q = c1.number_input("Mudar Qtd:", value=int(item['qtd']), key=f"q_{n}", min_value=0)
                    if c2.button("🗑️ Remover", key=f"del_{n}"):
                        del st.session_state.carrinho[n]
                        st.rerun()
                    st.session_state.carrinho[n]['qtd'] = nova_q
                    total += item['preco'] * nova_q
            
            st.divider()
            st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
            st.info("💡 Tudo certo? Finalize a compra na aba 'Histórico'.")
        else:
            st.info("O carrinho está vazio.")

    # --- 4. TELA DE HISTÓRICO ---
    elif menu == "📂 Histórico de Gastos":
        st.header("📂 Finalizar e Histórico")
        if st.session_state.carrinho:
            total_final = sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
            st.subheader(f"Total Atual: R$ {total_final:.2f}")
            if st.button("💾 FINALIZAR E SALVAR COMPRA DEFINITIVAMENTE"):
                dados = carregar_json(ARQUIVO_DADOS)
                if "historico" not in dados: dados["historico"] = {}
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                dados["historico"].setdefault(st.session_state.usuario_nome, []).append({
                    "data": agora, "total": total_final, "itens": list(st.session_state.carrinho.keys())
                })
                salvar_json(ARQUIVO_DADOS, dados)
                st.session_state.carrinho = {}
                st.success("✅ Compra registrada no histórico!")
                st.rerun()
        
        st.write("---")
        st.subheader("Compras Passadas")
        minhas = carregar_json(ARQUIVO_DADOS).get("historico", {}).get(st.session_state.usuario_nome, [])
        if minhas:
            for comp in reversed(minhas):
                st.write(f"📅 {comp['data']} | **Total: R$ {comp['total']:.2f}**")
        else:
            st.write("Nenhuma compra salva ainda.")
