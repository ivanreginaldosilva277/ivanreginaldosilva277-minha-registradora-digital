from streamlit_quagga2 import st_quagga2

with aba1:
    st.subheader("📟 Scanner de Barras Ativo")
    st.write("Aponte a câmera para o código e aguarde o reconhecimento automático.")
    
    # Este comando abre o scanner "VIVO"
    codigo_scanner = st_quagga2(key='scanner_vivo')

    if codigo_scanner:
        cod = str(codigo_scanner).strip()
        st.success(f"Lido: {cod}")
        
        with st.spinner("Buscando produto..."):
            nome_p = buscar_nome_internet(cod)
            if nome_p:
                if nome_p not in st.session_state.carrinho:
                    st.session_state.carrinho[nome_p] = {'preco': 0.0, 'qtd': 0}
                st.session_state.carrinho[nome_p]['qtd'] += 1
                st.toast(f"✅ {nome_p} adicionado!")
                st.rerun()
