import streamlit as st
import re
import json
import os
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- FUNÇÃO PARA BUSCAR NOME NA INTERNET ---
def buscar_nome_internet(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            if dados.get("status") == 1:
                return dados["product"].get("product_name", "Produto Desconhecido")
    except:
        return None
    return None

# --- CARREGAR DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}, "produtos_novos": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

# Produtos iniciais (Exemplos)
produtos_base = {
    "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
    "7891000100170": {"nome": "Chá Leão Hortelã", "preco": 3.50}
}

if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- TELA DE LOGIN E APP ---
# (Mantendo a lógica de login que você já tem...)
# [Omitido para focar na função de busca abaixo]

# --- LÓGICA DO SCANNER DENTRO DA ABA1 ---
# Substitua a parte do 'if resultado' por esta:

            if resultado:
                cod = str(resultado).strip()
                cod = re.sub(r'\W+', '', cod)
                
                # 1. Tenta achar na sua lista ou na internet
                dados_globais = carregar_dados()
                nome_encontrado = None
                preco_sugerido = 0.0

                if cod in produtos_base:
                    nome_encontrado = produtos_base[cod]['nome']
                    preco_sugerido = produtos_base[cod]['preco']
                elif cod in dados_globais["produtos_novos"]:
                    nome_encontrado = dados_globais["produtos_novos"][cod]['nome']
                    preco_sugerido = dados_globais["produtos_novos"][cod]['preco']
                else:
                    with st.spinner("Buscando nome na internet..."):
                        nome_encontrado = buscar_nome_internet(cod)
                
                if nome_encontrado:
                    st.write(f"🔎 **Produto:** {nome_encontrado}")
                    # Pergunta o preço se for novo ou permite confirmar o atual
                    p_mercado = st.number_input(f"Preço no mercado (R$):", value=preco_sugerido, key=f"p_input_{cod}")
                    
                    if st.button(f"Confirmar e Adicionar {nome_encontrado}", key=f"btn_{cod}"):
                        # Salva para o sistema "aprender"
                        dados_globais["produtos_novos"][cod] = {"nome": nome_encontrado, "preco": p_mercado}
                        salvar_dados(dados_globais)
                        
                        # Adiciona no carrinho
                        if nome_encontrado in st.session_state.carrinho:
                            st.session_state.carrinho[nome_encontrado]['qtd'] += 1
                        else:
                            st.session_state.carrinho[nome_encontrado] = {'preco': p_mercado, 'qtd': 1}
                        st.success("Adicionado!")
                        st.rerun()
                else:
                    st.warning(f"Código {cod} não encontrado nem na internet. Digite o nome manualmente.")
