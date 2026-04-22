import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Configuração visual
st.set_page_config(page_title="Registradora Digital", layout="centered")
st.title("--- REGISTRADORA DIGITAL ---")

# 1. Seu Banco de Dados (que você mandou agora)
if 'produtos_do_mercado' not in st.session_state:
    st.session_state.produtos_do_mercado = {
        "123": {"nome": "Arroz 5kg", "preco": 25.50},
        "456": {"nome": "Feijão 1kg", "preco": 8.90},
        "789": {"nome": "Leite 1L", "preco": 5.20},
        "001": {"nome": "Pão de Forma", "preco": 7.50},
        "002": {"nome": "Café 500g", "preco": 14.00},
        "003": {"nome": "Açúcar 1kg", "preco": 4.50},
    }

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Scanner por Câmera
st.subheader("Aponte para o código de barras")
foto = st.camera_input("Scanner")

if foto:
    # Processamento da imagem
    img_bytes = np.frombuffer(foto.getvalue(), np.uint8)
    img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    objetos = decode(cinza)
    
    if objetos:
        codigo = objetos[0].data.decode('utf-8').strip()
        
        if codigo in st.session_state.produtos_do_mercado:
            item = st.session_state.produtos_do_mercado[codigo]
            # Adiciona ao carrinho (1 unidade por vez para ser rápido)
            st.session_state.carrinho.append(item)
            st.success(f"Produto encontrado: {item['nome']} - R$ {item['preco']}")
        else:
            st.error(f"Código {codigo} não cadastrado! Teste com 123 ou 456.")
    else:
        st.warning("Foque bem no código de barras e tire a foto.")

# 3. Resumo da Compra (Soma Automática)
st.write("\n========== RESUMO DA COMPRA ==========")
total_da_compra = 0

if st.session_state.carrinho:
    for produto in st.session_state.carrinho:
        st.write(f"🔹 {produto['nome']} - R$ {produto['preco']:.2f}")
        total_da_compra += produto['preco']

    st.write(f"### VALOR TOTAL A PAGAR: R$ {total_da_compra:.2f}")
    
    if st.button("Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("Carrinho vazio.")
