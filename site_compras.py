import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import re

st.set_page_config(page_title="Calculadora Inteligente", page_icon="🛒")

# Banco de dados simples para teste
produtos = {
    "7894900011517": {"nome": "Coca-Cola Lata", "preco": 4.50},
    "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
    "7891000100170": {"nome": "Chá Leão Hortelã", "preco": 3.50}
}

if "carrinho" not in st.session_state:
    st.session_state.carrinho = {}

st.title("🛒 Calculadora de Mercado")

# --- BOTÃO DO SCANNER ---
st.subheader("📟 Escanear Produto")
# Este comando aciona o leitor do próprio navegador/celular
codigo_lido = streamlit_js_eval(js_expressions='window.prompt("Aponte para o código de barras e digite ou cole o número:")')

if codigo_lido:
    cod = re.sub(r'\D', '', str(codigo_lido))
    if cod in produtos:
        item = produtos[cod]
        nome_p = item['nome']
        if nome_p in st.session_state.carrinho:
            st.session_state.carrinho[nome_p]['qtd'] += 1
        else:
            st.session_state.carrinho[nome_p] = {'preco': item['preco'], 'qtd': 1}
        st.success(f"✅ {nome_p} adicionado!")
    else:
        st.warning(f"Código {cod} não cadastrado.")

# --- EXIBIÇÃO ---
st.write("---")
total = 0
for n, i in st.session_state.carrinho.items():
    st.write(f"**{i['qtd']}x {n}** - R$ {i['preco']*i['qtd']:.2f}")
    total += i['preco'] * i['qtd']

st.metric("TOTAL", f"R$ {total:.2f}")
