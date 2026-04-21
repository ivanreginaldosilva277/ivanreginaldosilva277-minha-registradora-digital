import streamlit as st
import re
import cv2
import numpy as np
from pyzbar.pyzbar import decode

# ... (Mantenha suas configurações de WHATSAPP e PRODUTOS iguais)

# --- NOVO CÓDIGO DA CÂMERA (NA ABA COMPRA) ---
foto = st.camera_input("Aponte para o código de barras")

if foto:
    # 1. Converter a foto
    bytes_data = foto.getvalue()
    img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # 2. ESCANEAR (Usando pyzbar que é muito mais forte)
    objetos_lidos = decode(img)
    
    if objetos_lidos:
        for obj in objetos_lidos:
            codigo_extraido = obj.data.decode('utf-8')
            st.success(f"Código lido: {codigo_extraido}")
            
            if codigo_extraido in produtos:
                item = produtos[codigo_extraido]
                nome_p = item['nome']
                if nome_p in st.session_state.carrinho:
                    st.session_state.carrinho[nome_p]['qtd'] += 1
                else:
                    st.session_state.carrinho[nome_p] = {'preco': item['preco'], 'qtd': 1}
                st.toast(f"✅ {nome_p} adicionado!")
                st.rerun()
            else:
                st.warning(f"Produto {codigo_extraido} não cadastrado.")
    else:
        st.error("Não consegui ler. Tente focar melhor nas barrinhas!")
