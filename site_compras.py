import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="Scanner de Compras", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Memória do App
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Banco de Dados
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
}

# 3. Scanner
st.subheader("Aponte a câmera para o código")
# Este componente abre a câmera direto na página
codigo = qrcode_scanner(key='scanner')

# 4. Processamento
if codigo:
    # Verificamos se o código lido está no banco
    if codigo in mercado_db:
        item = mercado_db[codigo]
        # Evita duplicar se ler o mesmo código várias vezes seguidas
        if not st.session_state.carrinho or st.session_state.carrinho[-1]['codigo'] != codigo:
            st.session_state.carrinho.append({"codigo": codigo, **item})
            st.toast(f"✅ {item['nome']} adicionado!")
    else:
        st.warning(f"Código {codigo} não encontrado.")

# 5. Carrinho
st.divider()
total = 0.0
if st.session_state.carrinho:
    for produto in st.session_state.carrinho:
        st.write(f"🔹 {produto['nome']} - R$ {produto['preco']:.2f}")
        total += produto['preco']
    
    st.write(f"### TOTAL: R$ {total:.2f}")
    
    if st.button("Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("O carrinho aparecerá aqui após o primeiro item.")
