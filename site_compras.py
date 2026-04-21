    if resultado and resultado[0]:
        codigo = resultado[0]
        with st.spinner(f"Buscando código {codigo}..."):
            nome = buscar_produto(codigo)
            
            # Se não achou na internet, pede para o usuário cadastrar na hora
            if not nome:
                st.warning(f"Código {codigo} lido, mas não encontrei o nome.")
                nome_manual = st.text_input("Digite o nome do produto:", key="nome_manual")
                preco_manual = st.number_input("Digite o preço (R$):", min_value=0.0, key="preco_manual")
                
                if st.button("Cadastrar e Adicionar ao Carrinho"):
                    if nome_manual:
                        if nome_manual not in st.session_state.carrinho:
                            st.session_state.carrinho[nome_manual] = {"preco": preco_manual, "qtd": 1}
                        else:
                            st.session_state.carrinho[nome_manual]["qtd"] += 1
                        st.success(f"✅ {nome_manual} cadastrado com sucesso!")
                        st.rerun()
            else:
                # Se achou na internet, adiciona e deixa o preço para ajuste depois
                if nome not in st.session_state.carrinho:
                    st.session_state.carrinho[nome] = {"preco": 0.0, "qtd": 1}
                else:
                    st.session_state.carrinho[nome]["qtd"] += 1
                st.success(f"✅ {nome} encontrado na rede!")
                st.rerun()
