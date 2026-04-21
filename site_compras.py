import streamlit as st
import streamlit.components.v1 as components
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"

def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒")

# --- ESTADO ---
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

st.title("📟 Registradora com Scanner")

# --- O SCANNER DE BARRA / QR CODE ---
st.subheader("📸 Leitor em Tempo Real")
st.info("Aponte a câmera traseira para o código de barras")

# Este componente abre o Scanner Profissional (Instascan)
components.html(
    """
    <video id="preview" style="width: 100%; border-radius: 10px; border: 3px solid #2e7d32;"></video>
    <script src="https://rawgit.com"></script>
    <script>
      let scanner = new Instascan.Scanner({ video: document.getElementById('preview'), mirror: false });
      scanner.addListener('scan', function (content) {
        // Envia o código para o Streamlit
        window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'cod_lido', value: content}, '*');
      });
      Instascan.Camera.getCameras().then(function (cameras) {
        if (cameras.length > 0) {
          // Tenta pegar a câmera traseira (geralmente a última da lista)
          scanner.start(cameras[cameras.length - 1]);
        } else {
          console.error('Nenhuma câmera encontrada.');
        }
      }).catch(function (e) {
        console.error(e);
      });
    </script>
    """,
    height=300,
)

# Campo que recebe o código lido automaticamente
codigo_detectado = st.text_input("Código Lido:", key="cod_lido")

if codigo_detectado:
    st.success(f"✅ Código identificado: {codigo_detectado}")
    nome = buscar_nome(codigo_detectado)
    if nome:
        st.write(f"**Produto:** {nome}")
        if st.button("Adicionar ao Carrinho"):
            st.session_state.carrinho[nome] = st.session_state.carrinho.get(nome, 0) + 1
            st.rerun()
    else:
        st.warning("Produto não achado. Digite o nome manualmente.")

st.write("---")
st.subheader("🛒 Sua Sacola")
for item, qtd in st.session_state.carrinho.items():
    st.write(f"• {qtd}x {item}")
