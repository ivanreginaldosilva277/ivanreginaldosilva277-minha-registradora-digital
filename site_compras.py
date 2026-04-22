import streamlit as st
import streamlit.components.v1 as components
import requests
import re

st.set_page_config(page_title="Registradora Inteligente", page_icon="🛒", layout="centered")

# Busca o nome na internet (Brasil)
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

# --- VISOR ESTILO CAIXA ---
total_atual = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
st.markdown(f"""
    <div style="background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444;">
        <small style="color:#aaa;">TOTAL DA COMPRA</small>
        <h1 style="margin:0; font-size:50px;">R$ {total_atual:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# --- SCANNER DE ALTA VELOCIDADE ---
st.subheader("📸 Aponte e Bipa")
components.html(
    """
    <div id="interactive" class="viewport" style="width:100%; height:250px; border-radius:10px; overflow:hidden; border:2px solid #2e7d32;"></div>
    <script src="https://cloudflare.com"></script>
    <script>
        Quagga.init({
            inputStream: { name: "Live", type: "LiveStream", target: document.querySelector('#interactive'), constraints: { facingMode: "environment" } },
            decoder: { readers: ["ean_reader", "ean_8_reader"] }
        }, function(err) {
            if (err) { console.log(err); return }
            Quagga.start();
        });
        Quagga.onDetected(function(result) {
            window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'cod_bip', value: result.codeResult.code}, '*');
        });
    </script>
    """,
    height=260,
)

# Recebe o código do "Bipe"
cod_bip = st.text_input("Código lido:", key="cod_bip")

if cod_bip:
    nome = buscar_nome(cod_bip)
    if nome:
        if nome not in st.session_state.carrinho:
            st.session_state.carrinho[nome] = {'preco': 0.0, 'qtd': 1}
        st.success(f"✅ {nome} no carrinho!")
    else:
        st.warning("Produto não achado. Digite o nome uma vez:")
        n_man = st.text_input("Nome do item:")
        if st.button("Salvar"):
            st.session_state.carrinho[n_man] = {'preco': 0.0, 'qtd': 1}

# --- LISTA DE CONFERÊNCIA (O CARRINHO) ---
st.write("---")
st.subheader("📋 Itens na Sacola")

for n in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[n]
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 0.5])
        c1.write(f"**{n}**")
        # Preço ajustável na hora
        item['preco'] = c2.number_input("Preço R$", value=float(item['preco']), key=f"p_{n}", step=0.01)
        # Quantidade com + e -
        item['qtd'] = c3.number_input("Qtd", value=int(item['qtd']), key=f"q_{n}", min_value=1)
        if c4.button("X", key=f"d_{n}"):
            del st.session_state.carrinho[n]
            st.rerun()
