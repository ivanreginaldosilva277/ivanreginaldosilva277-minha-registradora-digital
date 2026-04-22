import streamlit as st
from streamlit_barcode_scanner import st_barcode_scanner

st.set_page_config(page_title="Scanner de Compras", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Memória do App (Carrinho)
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. Banco de Dados Simples
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
}

# 3. Scanner Nativo
st.subheader("Aperte no botão abaixo para escanear")
# Esse componente abre a interface nativa do celular
barcode = st_barcode_scanner()

# 4. Lógica de Processamento
if barcode:
    codigo = barcode
    if codigo in mercado_db:
        item = mercado_db[codigo]
        # Evita duplicar se o scanner ler duas vezes rápido
        if not st.session_state.carrinho or st.session_state.carrinho[-1]['codigo'] != codigo:
            st.session_state.carrinho.append({"codigo": codigo, **item})
            st.success(f"Adicionado: {item['nome']}")
    else:
        st.warning(f"Código {codigo} não cadastrado no sistema.")

# 5. Exibição do Carrinho
st.divider()
st.subheader("Seu Carrinho")
total = 0.0

if st.session_state.carrinho:
    for i, produto in enumerate(st.session_state.carrinho):
        st.write(f"{i+1}. **{produto['nome']}** - R$ {produto['preco']:.2f}")
        total += produto['preco']
    
    st.write(f"### TOTAL: R$ {total:.2f}")
    
    if st.button("Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
else:
    st.info("Carrinho vazio. Use o scanner acima!")
