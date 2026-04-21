import streamlit as st
import cv2
import numpy as np
import requests
import re
import os
import json

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_PRODUTOS_CUSTOM = "banco_local.json"

st.set_page_config(page_title="Scanner Brasil", page_icon="🛒", layout="centered")

# --- FUNÇÕES DE MEMÓRIA ---
def carregar_banco_local():
    if os.path.exists(ARQUIVO_PRODUTOS_CUSTOM):
        with open(ARQUIVO_PRODUTOS_CUSTOM, "r") as f:
            return json.load(f)
    return {}

def salvar_no_banco_local(codigo, nome, preco):
    banco = carregar_banco_local()
    banco[codigo] = {"nome": nome, "preco": preco}
    with open(ARQUIVO_PRODUTOS_CUSTOM, "w") as f:
        json.dump(banco, f)

def buscar_produto_brasil(codigo):
    # Primeiro olha no seu banco que está crescendo
    banco_local = carregar_banco_local()
    if codigo in banco_local:
        return banco_local[codigo]["nome"], banco_local[codigo]["preco"]
    
    # Se não tem no local, busca na internet (Base Brasileira/Mundial)
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("status") == 1:
            prod = r.json()["product"]
            # Tenta pegar o nome em português, se não tiver, pega o genérico
            nome = prod.get("product_name_pt") or prod.get("product_name") or "Produto Desconhecido"
            return nome, 0.0
    except:
        return None, 0.0
    return None, 0.0

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

st.title("🛒 Scanner Inteligente Brasil")
st.caption("Localizando produtos em todo o território nacional")

# --- SCANNER ---
foto = st.camera_input("Aponte para o código de barras")

if foto:
    imagem = cv2.imdecode(np.frombuffer(foto.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    detector = cv2.barcode.BarcodeDetector()
    resultado = detector.detectAndDecode(imagem)
    
    if resultado and resultado:
        codigo_limpo = re.sub(r'\D', '', str(resultado))
        
        if codigo_limpo:
            with st.spinner(f"Identificando: {codigo_limpo}..."):
                nome, preco_sugerido = buscar_produto_brasil(codigo_limpo)
                
                if nome:
                    st.write(f"📦 **Produto:** {nome}")
                    p_venda = st.number_input("Preço no Mercado R$:", value=float(preco_sugerido), key=f"p_{codigo_limpo}")
                    
                    if st.button("Confirmar e Adicionar"):
                        # Salva para nunca mais esquecer
                        salvar_no_banco_local(codigo_limpo, nome, p_venda)
                        # Adiciona no carrinho
                        if nome in st.session_state.carrinho:
                            st.session_state.carrinho[nome]['qtd'] += 1
                        else:
                            st.session_state.carrinho[nome] = {"preco": p_venda, "qtd": 1}
                        st.success("Adicionado!")
                        st.rerun()
                else:
                    st.error("Produto não localizado na base nacional.")
                    n_man = st.text_input("Nome do Produto:", key="n_man")
                    p_man = st.number_input("Preço R$:", min_value=0.0, key="p_man")
                    if st.button("Cadastrar manualmente"):
                        salvar_no_banco_local(codigo_limpo, n_man, p_man)
                        st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                        st.rerun()

# --- CARRINHO ---
st.write("---")
total = 0
for n, i in st.session_state.carrinho.items():
    st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
    total += i['preco'] * i['qtd']

st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
