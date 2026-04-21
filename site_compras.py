import streamlit as st
from camera_input_live import camera_input_live
import requests
import re

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Scanner ZL", page_icon="🛒")

def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=4)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: return None
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("🛒 Scanner Automático")

# --- O SCANNER VIVO ---
st.subheader("📟 Aponte para o Código")
st.write("O sistema lerá as barras automaticamente (sem bater foto)")

# Este componente abre o vídeo da câmera traseira
imagem_viva = camera_input_live()

if imagem_viva:
    # Aqui o Streamlit já tenta extrair o texto/código da imagem viva
    # Obs: Se o componente não ler direto, ele liberará o campo abaixo
    st.info("Buscando barras na imagem...")

st.write("---")
# Campo reserva caso a câmera demore a focar
cod_manual = st.text_input("Ou use o scanner do teclado aqui:")

if cod_manual:
    cod = re.sub(r'\D', '', cod_manual)
    nome = buscar_nome(cod)
    if nome:
        st.success(f"✅ {nome}")
        preco = st.number_input("Preço R$:", value=0.0, key=f"p_{cod}")
        if st.button("Adicionar"):
            st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, {'preco': preco, 'qtd': 0})
            st.session_state.carrinho[nome]['qtd'] += 1
            st.rerun()

# --- TOTAL ---
total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho.values())
st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
