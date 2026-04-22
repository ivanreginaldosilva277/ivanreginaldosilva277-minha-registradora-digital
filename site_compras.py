import streamlit as st
from streamlit_camera_input_live import camera_input_live
import cv2
from pyzbar.pyzbar import decode
import numpy as np

st.title("🛒 Minha Registradora Digital")

# 1. BANCO DE DADOS (Adicione aqui o código que você tem aí!)
# DICA: Olhe o número embaixo das barrinhas do seu produto e troque aqui
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
}

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. SCANNER VIA CÂMERA
st.subheader("Aponte para o código de barras")
imagem = camera_input_live()

if imagem:
    # Converter imagem para formato que o Python entende
    bytes_data = imagem.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Tenta ler o código de barras na foto
    detectado = decode(cv2_img)
    
    if detectado:
        codigo = detectado[0].data.decode('utf-8')
        st.info(f"Código lido: {codigo}")
        
        if codigo in mercado_db:
            item = mercado_db[codigo]
            # Adiciona ao carrinho
            st.session_state.carrinho.append(item)
            st.success(f"✅ {item['nome']} adicionado!")
        else:
            st.error(f"Produto {codigo} não cadastrado!")
            # Botão para você cadastrar na hora se quiser
            if st.button(f"Cadastrar {codigo}?"):
                st.write("Função de cadastro em breve...")
    else:
        st.warning("Nenhum código de barras visível na imagem.")

# 3. EXIBIÇÃO DO CARRINHO
st.divider()
total = sum(p['preco'] for p in st.session_state.carrinho)
for p in st.session_state.carrinho:
    st.write(f"🔹 {p['nome']} - R$ {p['preco']:.2f}")

st.write(f"### TOTAL: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
