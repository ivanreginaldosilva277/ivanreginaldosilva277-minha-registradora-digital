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
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name"), 0.0
    except: pass
    return None, 0.0

# --- ESTILO ---
st.markdown("<style>.stButton>button { width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; font-weight: bold; }</style>", unsafe_allow_html=True)

# --- CONTROLE DE TELAS ---
if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}
if "usuario_nome" not in st.session_state: st.session_state.usuario_nome = ""

# --- 1. TELA DE LOGIN / CADASTRO ---
if not st.session_state.logado:
    tab_l, tab_c = st.tabs(["Login", "Cadastrar Novo"])
    
    with tab_l:
        st.title("🛒 Entrar")
        with st.form("login"):
            u = st.text_input("CPF ou Login:").strip().lower()
            s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ENTRAR 🚀"):
                dados = carregar_json(ARQUIVO_DADOS)
                if u in dados.get("usuarios", {}) and dados["usuarios"][u]["senha"] == s:
                    st.session_state.logado = True
                    st.session_state.usuario_nome = u
                    st.rerun()
                else: st.error("Erro no login.")
        st.markdown(f'<a href="{WHATSAPP_LINK}" target="_blank" style="text-decoration:none; color:white; background:#25d366; padding:10px; border-radius:10px; display:block; text-align:center;">💬 Fale com o Ivan</a>', unsafe_allow_html=True)

    with tab_c:
        st.title("📝 Cadastro")
        with st.form("cadastro"):
            nc = st.text_input("Nome Completo:")
            cc = st.text_input("CPF (será seu login):")
            sc = st.text_input("Senha:")
            if st.form_submit_button("FINALIZAR"):
                login_id = re.sub(r'\D', '', cc)
                if nc and login_id and sc:
                    dados = carregar_json(ARQUIVO_DADOS)
                    if "usuarios" not in dados: dados["usuarios"] = {}
                    dados["usuarios"][login_id] = {"nome": nc, "senha": sc, "historico": []}
                    salvar_json(ARQUIVO_DADOS, dados)
                    st.success("Cadastrado! Faça o login na aba ao lado.")
else:
    # MENU LATERAL PARA NAVEGAR ENTRE AS TELAS 2, 3 e 4
    st.sidebar.title(f"Olá, {st.session_state.usuario_nome}")
    menu = st.sidebar.radio("Ir para:", ["🛍️ Comprar", "🛒 Meu Carrinho", "📂 Histórico"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # --- 2. TELA DE COMPRAS (SCANNER) ---
    if menu == "🛍️ Comprar":
        st.title("🛍️ Escanear Produto")
        foto = st.camera_input("Aponte para o código")
        if foto:
            img = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
            res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
            if res and res[0]:
                cod = re.sub(r'\D', '', str(res[0]))
                nome, preco_sug = buscar_produto(cod)
                
                if nome:
                    st.success(f"Item: {nome}")
                    p_venda = st.number_input("Preço Unitário R$:", value=float(preco_sug), step=0.01)
                    q_venda = st.number_input("Quantidade:", value=1, min_value=1)
                    if st.button("➕ JOGAR PARA O CARRINHO"):
                        st.session_state.carrinho[nome] = {'preco': p_venda, 'qtd': q_venda, 'cod': cod}
                        # Salva na memória do app para a próxima vez
                        memoria = carregar_json(ARQUIVO_MEMORIA)
                        memoria[cod] = {"nome": nome, "preco": p_venda}
                        salvar_json(ARQUIVO_MEMORIA, memoria)
                        st.toast("Adicionado!")
                else:
                    st.warning("Produto não identificado.")
                    n_man = st.text_input("Nome do Produto:")
                    p_man = st.number_input("Preço R$:", min_value=0.0)
                    q_man = st.number_input("Qtd:", value=1, min_value=1)
                    if st.button("Adicionar Manual"):
                        st.session_state.carrinho[n_man] = {'preco': p_man, 'qtd': q_man}
                        st.rerun()

    # --- 3. TELA DO CARRINHO (REVISÃO) ---
    elif menu == "🛒 Meu Carrinho":
        st.title("🛒 Revisar Compras")
        total = 0.0
        if st.session_state.carrinho:
            for n in list(st.session_state.carrinho.keys()):
                item = st.session_state.carrinho[n]
                with st.expander(f"{n} - R$ {item['preco'] * item['qtd']:.2f}"):
                    c1, c2 = st.columns(2)
                    nova_q = c1.number_input("Mudar Qtd:", value=int(item['qtd']), key=f"q_{n}")
                    if c2.button("❌ Excluir", key=f"del_{n}"):
                        del st.session_state.carrinho[n]
                        st.rerun()
                    st.session_state.carrinho[n]['qtd'] = nova_q
                    total += item['preco'] * nova_q
            
            st.metric("VALOR TOTAL DA COMPRA", f"R$ {total:.2f}")
            if st.button("✅ FINALIZAR COMPRA"):
                st.session_state.temp_total = total
                st.success("Compra revisada! Vá para a tela de Histórico para salvar.")
        else:
            st.info("Carrinho vazio.")

    # --- 4. TELA DE HISTÓRICO ---
    elif menu == "📂 Histórico":
        st.title("📂 Histórico e Salvar")
        if st.session_state.carrinho:
            st.subheader("Compra Atual:")
            for n, i in st.session_state.carrinho.items():
                st.text(f"• {i['qtd']}x {n} = R$ {i['preco']*i['qtd']:.2f}")
            
            if st.button("💾 CONFIRMAR E SALVAR NO HISTÓRICO"):
                dados = carregar_json(ARQUIVO_DADOS)
                if "historico" not in dados: dados["historico"] = {}
                # Salva com data e hora
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                dados["historico"].setdefault(st.session_state.usuario_nome, []).append({
                    "data": agora, "itens": st.session_state.carrinho, "total": sum(x['preco']*x['qtd'] for x in st.session_state.carrinho.values())
                })
                salvar_json(ARQUIVO_DADOS, dados)
                st.session_state.carrinho = {}
                st.success("✅ Compra salva com sucesso!")
                st.rerun()
        
        st.write("---")
        st.subheader("Minhas Compras Antigas")
        dados = carregar_json(ARQUIVO_DADOS)
        minhas = dados.get("historico", {}).get(st.session_state.usuario_nome, [])
        for comp in reversed(minhas):
            with st.expander(f"Compra de {comp['data']} - Total R$ {comp['total']:.2f}"):
                for n, i in comp['itens'].items():
                    st.write(f"{i['qtd']}x {n}")
