import streamlit as st
import cv2
import numpy as np
import requests
import re

st.set_page_config(page_title="Calculadora Ivan", page_icon="🛒")

# Função para buscar o nome do produto na internet (Banco de dados mundial)
def buscar_produto(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("status") == 1:
            return r.json()["product"].get("product_name", "Produto Desconhecido")
    except: return None
    return None

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

st.title("🛒 Calculadora de Mercado")

# --- BOTÃO DE LER CÓDIGO ---
st.subheader("📟 Escanear Produto")
foto = st.camera_input("Clique no botão abaixo para ler o código")

if foto:
    # 1. Converter a foto para o leitor entender
    imagem = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    
    # 2. Motor de leitura de barras
    detector = cv2.barcode.BarcodeDetector()
    resultado = detector.detectAndDecode(imagem)
    
    if resultado and resultado[0]:
        codigo = resultado[0]
        with st.spinner(f"Buscando código {codigo}..."):
            nome = buscar_produto(codigo)
            if nome:
                if nome not in st.session_state.carrinho:
                    st.session_state.carrinho[nome] = {"preco": 0.0, "qtd": 1}
                else:
                    st.session_state.carrinho[nome]["qtd"] += 1
                st.success(f"✅ {nome} adicionado!")
            else:
                st.warning(f"Código {codigo} lido, mas não achei o nome.")
    else:
        st.error("Não consegui ler as barras. Tente focar melhor ou deixar o código bem reto na foto.")

# --- EXIBIÇÃO DO CARRINHO ---
st.write("---")
total = 0
for n, i in st.session_state.carrinho.items():
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.write(f"**{n}**")
    p = col2.number_input("R$", value=float(i['preco']), key=f"p_{n}")
    st.session_state.carrinho[n]['preco'] = p
    col3.write(f"Qtd: {i['qtd']}")
    total += p * i['qtd']

st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
