import streamlit as st
import streamlit.components.v1 as components
import requests
import re

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

st.title("🛒 Scanner Profissional")

# --- SCANNER AUTOMÁTICO (HTML5) ---
st.subheader("📟 Aponte a Câmera")

# Janela do Scanner Vivo
components.html(
    """
    <div id="reader" style="width:100%;"></div>
    <script src="https://unpkg.com"></script>
    <script>
        function onScanSuccess(decodedText) {
            // Envia o código para o Streamlit
            const input = window.parent.document.querySelectorAll('input')[0];
            input.value = decodedText;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            // Para o scanner após ler
            html5QrcodeScanner.clear();
        }
        var html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """,
    height=450,
)

# Campo que recebe o código
cod_lido = st.text_input("Código Lido:", key="codigo_capturado")

if cod_lido:
    cod = re.sub(r'\D', '', str(cod_lido))
    with st.spinner(f"Buscando {cod}..."):
        nome = buscar_nome(cod)
        if nome:
            st.success(f"✅ {nome}")
            preco = st.number_input("Preço R$:", value=0.0, key=f"p_{cod}")
            if st.button("Adicionar"):
                st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()
