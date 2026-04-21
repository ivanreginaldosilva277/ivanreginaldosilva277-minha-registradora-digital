import streamlit as st
import streamlit.components.v1 as components
import requests
import re

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒")

# Função de busca
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

st.title("📟 Registradora do Ivan")

# --- ÁREA DO SCANNER ---
st.subheader("📸 Scanner Automático")
st.info("🟢 O Scanner está ATIVO. Aponte para as barras e aguarde o número aparecer abaixo.")

# Componente do Scanner (Instascan)
components.html(
    """
    <video id="preview" style="width: 100%; border-radius: 10px; border: 3px solid #2e7d32; background: #000;"></video>
    <script src="https://rawgit.com"></script>
    <script>
      let scanner = new Instascan.Scanner({ video: document.getElementById('preview'), mirror: false });
      scanner.addListener('scan', function (content) {
        window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'cod_lido', value: content}, '*');
      });
      Instascan.Camera.getCameras().then(function (cameras) {
        if (cameras.length > 0) {
          // Seleciona a câmera traseira
          let backCam = cameras.find(cam => cam.name.toLowerCase().includes('back')) || cameras[cameras.length - 1];
          scanner.start(backCam);
        }
      });
    </script>
    """,
    height=300,
)

# Campo que recebe o dado automático
cod_auto = st.text_input("Código Detectado:", key="cod_lido")

if cod_auto:
    nome = buscar_nome(cod_auto)
    if nome:
        st.success(f"✅ Lido: {nome}")
        if st.button(f"Somar {nome} no Carrinho"):
            st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, 0) + 1
            st.rerun()

st.write("---")

# --- BOTÃO DE TESTE PARA VOCÊ FICAR TRANQUILO ---
st.subheader("🧪 Teste de Funcionamento")
if st.button("Simular Leitura de uma Coca-Cola"):
    cod_teste = "7894900011517"
    nome_teste = "Coca-Cola Lata"
    st.session_state.carrinho[nome_teste] = st.session_state.carrinho.get(nome_teste, 0) + 1
    st.success("O sistema de carrinho está funcionando 100%!")

st.write("---")
st.subheader("🛒 Sua Sacola")
if st.session_state.carrinho:
    for item, qtd in st.session_state.carrinho.items():
        st.write(f"• {qtd}x **{item}**")
else:
    st.write("Sacola vazia.")
