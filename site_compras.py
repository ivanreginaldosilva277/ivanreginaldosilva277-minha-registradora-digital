import streamlit as st
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_MEMORIA = "banco_zona_leste.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="⚡")

# --- BANCO DE DADOS "INSTANTÂNEO" (ITENS QUE NUNCA VÃO FALHAR) ---
PRODUTOS_POPULARES = {
    "7891203010056": "LEITE CONDENSADO ITAMBÉ",
    "7894900011517": "COCA-COLA LATA 350ML",
    "7894900010015": "COCA-COLA PET 2L",
    "7891000053506": "FEIJÃO CAMIL 1KG",
    "7896005818018": "ARROZ TIO JOÃO 5KG",
    "7891000100101": "NESCAFÉ TRADICIONAL",
    "7891150004125": "DETERGENTE YPÊ NEUTRO",
    "7891910000197": "AÇÚCAR UNIÃO 1KG",
    "7896000705023": "MACARRÃO ADRIA ESPAGUETE",
    "7898080640019": "CAFÉ PILÃO 500G"
}

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def buscar_nome_ninja(codigo):
    # 1. Tenta na lista de populares (Instantâneo)
    if codigo in PRODUTOS_POPULARES:
        return PRODUTOS_POPULARES[codigo]
    
    # 2. Tenta na memória do que você já cadastrou
    memoria = carregar_memoria()
    if codigo in memoria:
        return memoria[codigo]

    # 3. Tenta na internet (Último recurso)
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == 1:
                p = d["product"]
                nome = p.get("product_name_pt") or p.get("product_name") or p.get("brands")
                if nome:
                    nome_final = nome.strip().upper()
                    memoria[codigo] = nome_final
                    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
                        json.dump(memoria, f, ensure_ascii=False)
                    return nome_final
    except: pass
    return None

# --- ESTILO VISUAL CAIXA ---
st.markdown("""
    <style>
    .visor { background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444; margin-bottom:20px; }
    .stButton>button { width:100%; border-radius:10px; font-weight:bold; height: 3.5em; background-color: #2e7d32; color: white; }
    </style>
""", unsafe_allow_html=True)

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

# --- VISOR DE TOTAL ---
total = sum(v['preco'] * v['qtd'] for v in st.session_state.carrinho.values())
st.markdown(f"<div class='visor'><small>VALOR ACUMULADO</small><h1>R$ {total:.2f}</h1></div>", unsafe_allow_html=True)

# --- ENTRADA DE DADOS ---
st.write("### 🛍️ Bipar ou Ditar")
codigo_input = st.text_input("Dite o código ou use o microfone:", key="input_bip")

if codigo_input:
    cod = re.sub(r'\D', '', codigo_input)
    if cod:
        nome_p = buscar_nome_ninja(cod)
        
        # Se não achou em NENHUM lugar, ele ainda sugere um nome pra não travar
        if not nome_p:
            nome_p = f"PRODUTO {cod[-4:]}"
        
        st.success(f"📦 {nome_p}")
        preco = st.number_input(f"Preço do item (R$):", min_value=0.0, step=0.01, key=f"p_{cod}")
        
        if st.button("➕ ADICIONAR AGORA"):
            if nome_p in st.session_state.carrinho:
                st.session_state.carrinho[nome_p]['qtd'] += 1
            else:
                st.session_state.carrinho[nome_p] = {'preco': preco, 'qtd': 1}
            st.rerun()

# --- LISTA NO CARRINHO ---
st.write("---")
for nome in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[nome]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{nome}**")
    item['qtd'] = c2.number_input(f"Qtd {nome}", value=item['qtd'], key=f"q_{nome}", min_value=1, label_visibility="collapsed")
    if c3.button("X", key=f"d_{nome}"):
        del st.session_state.carrinho[nome]
        st.rerun()
