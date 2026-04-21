import streamlit as st
import re

st.set_page_config(page_title="Registradora Ivan", page_icon="📟")

# --- ESTILO ---
st.markdown("<style>.stButton>button { width:100%; height:4em; font-weight:bold; background:#2e7d32; color:white; border-radius:15px; }</style>", unsafe_allow_html=True)

st.title("📟 Registradora Inteligente")

# --- O PULO DO GATO ---
st.subheader("Bipar Produto")
st.info("Clique abaixo para abrir o scanner do seu celular:")

# Este campo recebe o que o seu celular ler
codigo = st.text_input("Resultado do Scanner:", key="campo_bip")

# Instrução visual para o usuário
st.markdown("""
    **Como escanear rápido:**
    1. Toque na caixa acima.
    2. No seu teclado Samsung, toque no ícone de **[Scan]** ou nos **[...]** e escolha **Escanear código**.
    3. Aponte a câmera traseira e o número aparecerá sozinho!
""")

if codigo:
    st.success(f"✅ Código {codigo} detectado! Somando no carrinho...")
    # Aqui ele já pode somar direto no seu total
