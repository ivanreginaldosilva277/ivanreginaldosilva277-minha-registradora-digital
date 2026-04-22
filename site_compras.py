import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import av

# Configuração da página
st.set_page_config(page_title="Scanner de Compras", layout="wide")
st.title("🛒 Minha Registradora Digital")

# 1. Memória do App (Carrinho)
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Banco de Dados Simples
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
    "7891000100103": {"nome": "Biscoito Recheado", "preco": 3.20}
}

# 3. Função para processar o vídeo
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Converte para cinza para facilitar a detecção das barras
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    codigos = decode(gray)
    
    for obj in codigos:
        codigo = obj.data.decode('utf-8')
        
        if codigo in mercado_db:
            # Desenha o quadrado verde na tela
            pts = np.array([obj.polygon], np.int32)
            cv2.polylines(img, [pts], True, (0, 255, 0), 3)
            
            # Adiciona ao carrinho se não for repetição imediata
            item = mercado_db[codigo]
            if not st.session_state.carrinho or st.session_state.carrinho[-1]['codigo'] != codigo:
                st.session_state.carrinho.append({"codigo": codigo, **item})
    
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# 4. Interface Gráfica
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Scanner")
    webrtc_streamer(
        key="scanner",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    st.caption("Dica: Se o item não aparecer, clique no botão 'Atualizar' ao lado.")

with col2:
    st.subheader("Seu Carrinho")
    
    # Botão de atualização é essencial no Streamlit para mostrar o que a câmera leu
    if st.button("🔄 ATUALIZAR LISTA", type="primary"):
        st.rerun()

    st.divider()
    total = 0.0
    if st.session_state.carrinho:
        for i, produto in enumerate(st.session_state.carrinho):
            col_nome, col_preco = st.columns([2, 1])
            col_nome.write(f"**{produto['nome']}**")
            col_preco.write(f"R$ {produto['preco']:.2f}")
            total += produto['preco']
        
        st.divider()
        st.write(f"### TOTAL: R$ {total:.2f}")
    else:
        st.info("Nenhum item detectado. Aponte a câmera para um código de barras.")

    if st.button("Limpar Tudo"):
        st.session_state.carrinho = []
        st.rerun()
