import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests # Para buscar o nome do produto na internet

st.set_page_config(page_title="Minha Registradora", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Banco de Dados Local (Seus itens favoritos)
if 'mercado_db' not in st.session_state:
    st.session_state.mercado_db = {
        "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
        "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
    }

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Função para tentar descobrir o nome do produto pelo código na internet
def buscar_nome_produto(codigo):
    try:
        # Usando uma busca simples (exemplo didático)
        url = f"https://openfoodfacts.org{codigo}.json"
        response = requests.get(url).json()
        if response.get("status") == 1:
            return response["product"].get("product_name", "Produto Desconhecido")
    except:
        return None
    return None

# 2. Câmera
st.subheader("Tire uma foto nítida do código de barras")
foto = st.camera_input("Scanner")

if foto:
    imagem_bytes = np.frombuffer(foto.getvalue(), np.uint8)
    imagem = cv2.imdecode(imagem_bytes, cv2.IMREAD_COLOR)
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    objetos_detectados = decode(cinza)
    
    if objetos_detectados:
        codigo = objetos_detectados[0].data.decode('utf-8').strip()
        st.write(f"**Código detectado:** `{codigo}`")
        
        # 1º Tenta no banco local
        if codigo in st.session_state.mercado_db:
            produto = st.session_state.mercado_db[codigo]
            st.session_state.carrinho.append(produto)
            st.success(f"✅ {produto['nome']} adicionado!")
        else:
            # 2º Tenta buscar na internet
            with st.spinner('Buscando produto na base de dados...'):
                nome_internet = buscar_nome_produto(codigo)
            
            if nome_internet:
                st.warning(f"Achei na internet: {nome_internet}")
            else:
                st.error("Produto não encontrado na base de dados.")
            
            # 3º Abre o cadastro para você dar o preço (já que preço varia de mercado para mercado)
            with st.form("cadastro_rapido"):
                nome_final = st.text_input("Confirmar Nome:", value=nome_internet if nome_internet else "")
                preco_final = st.number_input("Preço neste mercado (R$):", min_value=0.0, step=0.10)
                if st.form_submit_button("Confirmar e Adicionar"):
                    novo_item = {"nome": nome_final, "preco": preco_final}
                    st.session_state.mercado_db[codigo] = novo_item
                    st.session_state.carrinho.append(novo_item)
                    st.rerun()
    else:
        st.warning("Não consegui ler. Tente enquadrar apenas o código de barras na foto.")

# 3. Carrinho
st.divider()
st.subheader("📋 Carrinho Atual")
total = sum(item['preco'] for item in st.session_state.carrinho)

for p in st.session_state.carrinho:
    st.write(f"🔹 {p['nome']} — R$ {p['preco']:.2f}")

st.write(f"### 💰 TOTAL: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
