import streamlit as st

st.set_page_config(page_title="Minha Registradora", layout="centered")
st.title("🛒 Minha Registradora Digital")

# 1. Banco de Dados
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7894900011517": {"nome": "Coca-Cola 2L", "preco": 9.50},
}

# 2. Inicializar Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 3. Entrada de Dados (Simulando o Scanner)
# No celular, ao clicar aqui, muitos teclados mostram um ícone de câmera/código de barras
codigo_lido = st.text_input("Aponte o scanner ou digite o código:", key="input_codigo")

if codigo_lido:
    if codigo_lido in mercado_db:
        item = mercado_db[codigo_lido]
        st.session_state.carrinho.append(item)
        st.success(f"Adicionado: {item['nome']}")
        # Limpa o campo para a próxima leitura
    else:
        st.error("Produto não cadastrado!")

# 4. Exibição
st.divider()
total = sum(p['preco'] for p in st.session_state.carrinho)

for i, p in enumerate(st.session_state.carrinho):
    st.write(f"{i+1}. {p['nome']} - R$ {p['preco']:.2f}")

st.write(f"## Total: R$ {total:.2f}")

if st.button("Limpar Carrinho"):
    st.session_state.carrinho = []
    st.rerun()
