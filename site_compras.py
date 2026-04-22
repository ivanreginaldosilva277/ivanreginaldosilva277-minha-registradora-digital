import streamlit as st
import streamlit.components.v1 as components
import requests
import re

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒", layout="centered")

# Função de busca na internet
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.markdown("<h2 style='text-align:center;'>📟 SCANNER PROFISSIONAL</h2>", unsafe_allow_html=True)

# --- O SCANNER DE TELA CHEIA ---
st.info("Aponte a câmera traseira para as barras:")

# Este componente abre o leitor automático em tamanho grande
components.html(
    """
    <script src="https://unpkg.com"></script>
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden;"></div>
    <script>
        function onScanSuccess(decodedText) {
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                key: 'cod_lido',
                value: decodedText
            }, '*');
        }
        let config = { fps: 10, qrbox: {width: 300, height: 150}, aspectRatio: 1.0 };
        let html5QrcodeScanner = new Html5QrcodeScanner("reader", config, false);
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """,
    height=450,
)

# Campo que recebe o código sozinho após o bipe
codigo_final = st.text_input("Código Identificado:", key="cod_lido")

if codigo_final:
    cod_limpo = re.sub(r'\D', '', codigo_final)
    nome = buscar_nome(cod_limpo)
    if nome:
        st.success(f"✅ {nome}")
        preco = st.number_input("Preço R$:", min_value=0.0, step=0.01, key=f"p_{cod_limpo}")
        if st.button("➕ ADICIONAR AO CARRINHO"):
            st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, 0) + 1
            st.rerun()
    else:
        st.warning("Produto não achado. Digite o nome:")
        n_man = st.text_input("Nome do produto:")
        if st.button("Salvar Manual"):
            st.session_state.carrinho[n_man] = st.session_state.carrinho.get(n_man, 0) + 1
            st.rerun()

st.write("---")
st.subheader("🛒 Sua Lista:")
for item, qtd in st.session_state.carrinho.items():
    st.write(f"• {qtd}x {item}")
