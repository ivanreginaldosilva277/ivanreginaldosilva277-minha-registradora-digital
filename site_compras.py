import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode

st.set_page_config(page_title="Minha Registradora", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Banco de Dados Inicial
# DICA: Os itens cadastrados aqui são fixos. Os que você cadastrar pelo app valem até você atualizar a página.
if 'mercado_db' not in st.session_state:
    st.session_state.mercado_db = {
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
    imagem_bytes = np.frombuffer(foto.getvalue(), np.uint8)
    imagem = cv2.imdecode(imagem_bytes, cv2.IMREAD_COLOR)
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    objetos_detectados = decode(cinza)
    
    if objetos_detectados:
        codigo = objetos_detectados[0].data.decode('utf-8').strip()
        st.write(f"**Código detectado:** `{codigo}`")
        
        # Verifica se o código já existe no nosso banco
        if codigo in st.session_state.mercado_db:
            produto = st.session_state.mercado_db[codigo]
            st.session_state.carrinho.append(produto)
            st.success(f"✅ {produto['nome']} adicionado ao carrinho!")
        else:
            st.error(f"Produto {codigo} não cadastrado!")
            
            # --- ÁREA DE CADASTRO RÁPIDO ---
            st.info("Cadastre este produto abaixo para testar agora:")
            with st.form("cadastro_rapido"):
                nome_novo = st.text_input("Nome do Produto:")
                preco_novo = st.number_input("Preço (R$):", min_value=0.0, step=0.10)
                btn_salvar = st.form_submit_button("Salvar e Adicionar")
                
                if btn_salvar and nome_novo:
                    # Adiciona ao banco da memória
                    st.session_state.mercado_db[codigo] = {"nome": nome_novo, "preco": preco_novo}
                    # Adiciona ao carrinho
                    st.session_state.carrinho.append({"nome": nome_novo, "preco": preco_novo})
                    st.success("Salvo com sucesso!")
                    st.rerun()
    else:
        st.warning("Não consegui ler o código. Tente centralizar bem as barras e evitar reflexos.")

# 3. Exibição do Carrinho
st.divider()
st.subheader("📋 Seu Carrinho")
total = sum(item['preco'] for item in st.session_state.carrinho)

if st.session_state.carrinho:
    for p in st.session_state.carrinho:
        st.write(f"🔹 {p['nome']} — **R$ {p['preco']:.2f}**")
    
    st.write(f"### 💰 Total: R$ {total:.2f}")
    
    if st.button("Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.write("O carrinho está vazio.")
