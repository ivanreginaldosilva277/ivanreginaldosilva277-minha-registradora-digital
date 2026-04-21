import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
import re

st.set_page_config(page_title="Scanner Profissional", page_icon="🛒")

# Função que busca em várias bases brasileiras
def buscar_produto_brasil(codigo):
    urls = [
        f"https://openfoodfacts.org{codigo}.json",
        f"https://openfoodfacts.org{codigo}.json"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200 and r.json().get("status") == 1:
                p = r.json()["product"]
                return p.get("product_name_pt") or p.get("product_name")
        except: continue
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("🛒 Scanner de Mercado ZL")

# --- O BOTÃO QUE ABRE O SCANNER AUTOMÁTICO ---
st.subheader("📟 Escanear Produto")
st.write("Clique no botão e aponte a câmera traseira para o código:")

# Esse comando aciona o leitor nativo do celular (com foco automático)
codigo_lido = streamlit_js_eval(js_expressions='window.prompt("Scanner Ativo: Aponte a câmera e aguarde o número aparecer (ou digite o código):")')

if codigo_lido:
    cod = re.sub(r'\D', '', str(codigo_lido))
    if cod:
        with st.spinner(f"Identificando {cod}..."):
            nome = buscar_produto_brasil(cod)
            if nome:
                st.success(f"✅ {nome}")
                preco = st.number_input(f"Preço de hoje para {nome}:", min_value=0.0, key=f"p_{cod}")
                if st.button(f"Adicionar {nome}"):
                    if nome not in st.session_state.carrinho:
                        st.session_state.carrinho[nome] = {"preco": preco, "qtd": 1}
                    else:
                        st.session_state.carrinho[nome]["qtd"] += 1
                    st.rerun()
            else:
                st.warning("Produto novo! Digite o nome:")
                n_man = st.text_input("Nome:", key="n_man")
                p_man = st.number_input("Preço:", key="p_man")
                if st.button("Salvar Manualmente"):
                    st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                    st.rerun()

# --- EXIBIÇÃO DO TOTAL ---
st.write("---")
total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho.values())
st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
