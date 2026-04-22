import streamlit as st
from streamlit_webrtc import webrtc_streamer
import cv2
from pyzbar.pyzbar import decode
import numpy as np

st.set_page_config(page_title="Scanner de Compras", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Memória do App (Carrinho)
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Banco de Dados Simples
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50} # Exemplo
}

# 3. Função que processa a imagem
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    codigos = decode(img)
    
    for obj in codigos:
        codigo = obj.data.decode('utf-8')
        if codigo in mercado_db:
            item = mercado_db[codigo]
            # Adiciona ao carrinho se não tiver sido lido agora
            if not st.session_state.carrinho or st.session_state.carrinho[-1]['codigo'] != codigo:
                st.session_state.carrinho.append({"codigo": codigo, **item})
    
    return frame

# 4. Interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("Scanner")
    webrtc_streamer(key="scanner", video_frame_callback=video_frame_callback)

with col2:
    st.subheader("Seu Carrinho")
    total = 0
    for i, produto in enumerate(st.session_state.carrinho):
        st.write(f"{i+1}. {produto['nome']} - R$ {produto['preco']:.2f}")
        total += produto['preco']
    
    st.divider()
    st.write(f"### TOTAL: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
