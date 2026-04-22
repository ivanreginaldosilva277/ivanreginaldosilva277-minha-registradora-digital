import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests

st.set_page_config(page_title="Minha Registradora", layout="centered")
st.title("🛒 Minha Registradora Digital")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Função que consulta a "Base de Dados Mundial" (Supermercados)
def consultar_supermercado(codigo):
    try:
        # API gratuita que contém milhões de produtos de supermercado
        url = f"https://openfoodfacts.org{codigo}.json"
        response = requests.get(url, timeout=5).json()
        
        if response.get("status") == 1:
            produto_data = response["product"]
            nome = produto_data.get("product_name", "Produto sem nome")
            marca = produto_data.get("brands", "")
            return f"{nome} {marca}".strip()
    except:
        return None
    return None

# Câmera
st.subheader("Tire uma foto do código de barras")
foto = st.camera_input("Scanner")

if foto:
    imagem_bytes = np.frombuffer(foto.getvalue(), np.uint8)
    imagem = cv2.imdecode(imagem_bytes, cv2.IMREAD_COLOR)
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    objetos = decode(cinza)
    
    if objetos:
        codigo = objetos[0].data.decode('utf-8').strip()
        st.write(f"**Código detectado:** `{codigo}`")
        
        # BUSCA NA BASE EXTERNA (Supermercados)
        with st.spinner('Buscando nos bancos de dados de supermercados...'):
            nome_encontrado = consultar_supermercado(codigo)
        
        if nome_encontrado:
            st.success(f"Encontrado: **{nome_encontrado}**")
            # Como a base mundial não tem o PREÇO (pois muda de mercado para mercado)
            # Precisamos pedir o preço para somar no carrinho
            preco = st.number_input(f"Qual o preço do {nome_encontrado}?", min_value=0.0, step=0.01, key="preco_input")
            
            if st.button("Adicionar ao Carrinho"):
                st.session_state.carrinho.append({"nome": nome_encontrado, "preco": preco})
                st.rerun()
        else:
            st.error("Este produto não foi encontrado nem na base mundial. Tente digitar o nome manualmente.")
            nome_manual = st.text_input("Nome do produto:")
            preco_manual = st.number_input("Preço:", min_value=0.0)
            if st.button("Adicionar Manualmente"):
                st.session_state.carrinho.append({"nome": nome_manual, "preco": preco_manual})
                st.rerun()
    else:
        st.warning("Não consegui ler. Tente focar melhor no código de barras.")

# Carrinho
st.divider()
st.subheader("📋 Itens no Carrinho")
total = sum(item['preco'] for item in st.session_state.carrinho)

for item in st.session_state.carrinho:
    st.write(f"🔹 {item['nome']} - R$ {item['preco']:.2f}")

st.write(f"## TOTAL: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
