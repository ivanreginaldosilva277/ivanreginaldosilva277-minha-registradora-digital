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

st.title("🛒 Scanner Profissional Ivan")

# --- LEITOR DE CÓDIGO DE BARRAS VIVO ---
st.subheader("📟 Aponte e Bipe")

# Este bloco de código cria o leitor automático que você quer
components.html(
    """
    <script src="https://unpkg.com"></script>
    <div id="reader" style="width: 100%;"></div>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Envia o código lido para o campo de texto do Streamlit
            window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'codigo_qr', value: decodedText}, '*');
            html5QrcodeScanner.clear();
        }
        let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """,
    height=400,
)

# Campo invisível que recebe o dado do scanner
codigo_lido = st.text_input("Código capturado:", key="codigo_qr")

if codigo_lido:
    cod = re.sub(r'\D', '', str(codigo_lido))
    with st.spinner(f"Identificando {cod}..."):
        nome = buscar_nome(cod)
        if nome:
            st.success(f"✅ {nome}")
            preco = st.number_input("Preço R$:", value=0.0, key=f"p_{cod}")
            if st.button(f"Adicionar {nome}"):
                if nome not in st.session_state.carrinho:
                    st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                else:
                    st.session_state.carrinho[nome]['qtd'] += 1
                st.rerun()
