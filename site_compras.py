import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode

st.set_page_config(page_title="Minha Registradora", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Banco de Dados (Adicione os códigos reais dos seus produtos aqui)
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
    "7891000100103": {"nome": "Biscoito", "preco": 3.50}
}

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Câmera Nativa do Streamlit
st.subheader("Tire uma foto do código de barras")
foto = st.camera_input("Scanner")

if foto:
    # Converter a foto para um formato que o Python entende
    imagem_bytes = np.frombuffer(foto.getvalue(), np.uint8)
    imagem = cv2.imdecode(imagem_bytes, cv2.IMREAD_COLOR)
    
    # Converter para cinza para melhorar a leitura
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    # Tenta decodificar o código de barras
    objetos_detectados = decode(cinza)
    
    if objetos_detectados:
        # Pega o número e remove espaços em branco (resolve o erro de "não encontrado")
        codigo = objetos_detectados[0].data.decode('utf-8').strip()
        st.write(f"**Código detectado:** {codigo}")
        
        if codigo in mercado_db:
            produto = mercado_db[codigo]
            st.session_state.carrinho.append(produto)
            st.success(f"✅ {produto['nome']} adicionado ao carrinho!")
        else:
            st.error(f"Produto {codigo} não cadastrado!")
    else:
        st.warning("Não consegui ler o código. Tente aproximar mais ou melhorar a luz.")

# 3. Exibição do Carrinho
st.divider()
st.subheader("Seu Carrinho")
total = sum(item['preco'] for item in st.session_state.carrinho)

for p in st.session_state.carrinho:
    st.write(f"🔹 {p['nome']} - R$ {p['preco']:.2f}")

st.write(f"## Total: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
