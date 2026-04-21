import streamlit as st
import requests
import re

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Scanner ZL", page_icon="🛒")

def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=4)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: return None
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("🛒 Scanner Ultra Rápido")

# --- O CAMPO QUE ACIONA O SCANNER ---
st.subheader("📟 Bipar Produto")
st.write("Toque no campo abaixo. No seu Samsung, escolha o ícone de **Câmera/Scanner** que aparece em cima do teclado.")

# Este campo de texto é o "gatilho" para o scanner do seu celular
cod_lido = st.text_input("Toque aqui para escanear", key="input_scan", placeholder="Aponte a câmera...")

if cod_lido:
    cod = re.sub(r'\D', '', cod_lido) # Limpa para deixar só números
    if cod:
        with st.spinner("Buscando produto..."):
            nome = buscar_nome(cod)
            if nome:
                st.success(f"✅ {nome}")
                preco = st.number_input("Preço R$:", value=0.0, key=f"p_{cod}")
                if st.button(f"Confirmar e Somar {nome}"):
                    if nome not in st.session_state.carrinho:
                        st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                    else:
                        st.session_state.carrinho[nome]['qtd'] += 1
                    st.session_state.input_scan = "" # Limpa para o próximo
                    st.rerun()
            else:
                st.warning("Não achei na internet. Digite o nome:")
                n_man = st.text_input("Nome:")
                p_man = st.number_input("Preço:", key="p_man")
                if st.button("Adicionar Manual"):
                    st.session_state.carrinho[n_man] = {"preco": p_man, "qtd": 1}
                    st.rerun()

# --- TOTAL ---
st.write("---")
total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho.values())
st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
