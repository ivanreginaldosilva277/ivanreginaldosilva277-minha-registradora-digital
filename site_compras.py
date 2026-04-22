import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import cv2
from pyzbar.pyzbar import decode
import numpy as np

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

# 3. Função para processar o frame e retornar o código encontrado
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Tenta decodificar o código de barras
    codigos = decode(img)
    for obj in codigos:
        codigo = obj.data.decode('utf-8')
        
        # Se o código estiver no nosso banco, desenha um retângulo no vídeo
        if codigo in mercado_db:
            pts = np.array([obj.polygon], np.int32)
            cv2.polylines(img, [pts], True, (0, 255, 0), 3)
            # Para evitar que o Streamlit trave, usamos o log para conferir
            print(f"Detectado: {codigo}")
            
            # Adiciona ao carrinho (usamos um truque aqui: salvar no estado)
            if not st.session_state.carrinho or st.session_state.carrinho[-1]['codigo'] != codigo:
                st.session_state.carrinho.append({"codigo": codigo, **mercado_db[codigo]})
    
    import av
    return av.VideoFrame.from_ndarray(img, format="bgr24")

# 4. Interface Gráfica
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Scanner")
    # Versão mais robusta do streamer
    webrtc_streamer(
        key="scanner",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=video_frame_callback,
        rtc_configuration={"iceServers": [{"urls": ["stun:://google.com"]}]},
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.subheader("Seu Carrinho")
    total = 0.0
    
    if st.session_state.carrinho:
        for i, produto in enumerate(st.session_state.carrinho):
            st.write(f"**{i+1}. {produto['nome']}**")
            st.write(f"R$ {produto['preco']:.2f}")
            total += produto['preco']
            st.divider()
    else:
        st.info("Nenhum item escaneado ainda.")
    
    st.write(f"### TOTAL: R$ {total:.2f}")

    if st.button("Limpar Tudo"):
        st.session_state.carrinho = []
        st.rerun()

# Botão de atualização manual (caso o item demore a aparecer na lista)
if st.button("Atualizar Carrinho"):
    st.rerun()
