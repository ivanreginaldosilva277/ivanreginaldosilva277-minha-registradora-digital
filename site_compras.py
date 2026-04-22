import streamlit as st
from streamlit_webrtc import webrtc_streamer
import cv2
from pyzbar.pyzbar import decode
import numpy as np

st.title("Minha Registradora Digital 🛒")

# Simulação de banco de dados
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90}
}

# Função que processa a imagem da câmera
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Detectar códigos de barras
    codigos = decode(img)
    for obj in codigos:
        codigo_lido = obj.data.decode('utf-8')
        # Aqui você pode adicionar lógica para salvar o código lido
        # Mas atenção: esta função roda em uma "thread" separada
        print(f"Código detectado: {codigo_lido}")
        
    return frame

# Criar o componente de vídeo no site
webrtc_streamer(key="scanner", video_frame_callback=video_frame_callback)

st.write("Aproxime o código de barras da câmera para escanear.")
