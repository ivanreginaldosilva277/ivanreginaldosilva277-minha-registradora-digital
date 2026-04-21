import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Calculadora Ivan", page_icon="🛒", layout="centered")

def buscar_produto(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("status") == 1:
            return r.json()["product"].get("product_name", "Produto Desconhecido")
    except:
        return None
    return None

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

st.title("🛒 Calculadora de Mercado")

st.subheader("📟 Escanear Produto")
foto = st.camera_input("Aponte para o código de barras")

if foto:
    imagem = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.barcode.BarcodeDetector()
    resultado = detector.detectAndDecode(imagem)
    
    # AJUSTE AQUI: Limpeza do código lido
    if resultado and resultado[0]:
        # Pegamos apenas a primeira parte da resposta e removemos tudo que não for número
        codigo_sujo = str(resultado[0])
        codigo_limpo = re.sub(r'\D', '', codigo_sujo)
        
        if codigo_limpo:
            with st.spinner(f"Buscando código {codigo_limpo}..."):
                nome = buscar_produto(codigo_limpo)
                
                if not nome:
                    st.warning(f"Código {codigo_limpo} lido, mas não achei na internet.")
                    nome_manual = st.text_input("Nome do Produto:", key="n_man")
                    preco_manual = st.number_input("Preço R$:", min_value=0.0, key="p_man")
                    
                    if st.button("Salvar e Adicionar"):
                        if nome_manual:
                            st.session_state.carrinho[nome_manual] = {"preco": preco_manual, "qtd": 1}
                            st.success(f"✅ {nome_manual} adicionado!")
                            st.rerun()
                else:
                    if nome not in st.session_state.carrinho:
                        st.session_state.carrinho[nome] = {"preco": 0.0, "qtd": 1}
                    else:
                        st.session_state.carrinho[nome]["qtd"] += 1
                    st.success(f"✅ {nome} encontrado!")
                    st.rerun()
        else:
            st.error("Não consegui extrair um número válido do código.")
    else:
        st.error("Não consegui ler as barras. Tente focar melhor!")

st.write("---")
total = 0
if st.session_state.carrinho:
    for n in list(st.session_state.carrinho.keys()):
        i = st.session_state.carrinho[n]
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**{n}**")
        p = col2.number_input("R$", value=float(i['preco']), key=f"preco_{n}")
        st.session_state.carrinho[n]['preco'] = p
        col3.write(f"Qtd: {i['qtd']}")
        total += p * i['qtd']

    st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
    
    if st.button("🗑️ Limpar Carrinho"):
        st.session_state.carrinho = {}
        st.rerun()
else:
    st.info("Carrinho vazio. Use a câmera acima!")
