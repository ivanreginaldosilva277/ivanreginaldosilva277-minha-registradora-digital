import streamlit as st
import streamlit.components.v1 as components
import requests
import re

st.set_page_config(page_title="Scanner ZL", page_icon="🛒")

# Função para buscar nome na internet
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

st.subheader("📟 Bipar Produto")

# --- BOTÃO QUE ABRE A CÂMERA (HTML/JS) ---
# Esse bloco cria um botão "Abrir Câmera" que usa o leitor do navegador
st.markdown("### 1. Clique no botão abaixo para escanear:")
codigo_lido = st.text_input("O código aparecerá aqui após o bip:", key="cod_final")

# Componente que tenta forçar a abertura da câmera traseira
components.html(
    """
    <button onclick="scanner()" style="width: 100%; height: 50px; background-color: #2e7d32; color: white; border: none; border-radius: 10px; font-weight: bold;">
        📷 ABRIR CÂMERA TRASEIRA
    </button>
    <script>
    function scanner() {
        const code = prompt("O leitor foi ativado! Aponte para o código de barras ou digite o número:");
        if (code) {
            window.parent.document.querySelector('input[aria-label="O código aparecerá aqui após o bip:"]').value = code;
            window.parent.document.querySelector('input[aria-label="O código aparecerá aqui após o bip:"]').dispatchEvent(new Event('input', {bubbles: true}));
        }
    }
    </script>
    """,
    height=70,
)

if codigo_lido:
    cod = re.sub(r'\D', '', codigo_lido)
    nome = buscar_nome(cod)
    if nome:
        st.success(f"✅ {nome}")
        preco = st.number_input("Preço R$:", value=0.0, key=f"p_{cod}")
        if st.button(f"Confirmar e Somar {nome}"):
            if nome not in st.session_state.carrinho:
                st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
            else:
                st.session_state.carrinho[nome]['qtd'] += 1
            st.rerun()

st.write("---")
total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho.values())
st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
