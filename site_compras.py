            if resultado and resultado[0]:
                # Pega apenas o primeiro código de barras da lista e limpa espaços
                cod = str(resultado[0]).strip()
                
                if cod in produtos:
                    n = produtos[cod]['nome']
                    if n in st.session_state.carrinho:
                        st.session_state.carrinho[n]['qtd'] += 1
                    else:
                        st.session_state.carrinho[nome_p] = {'preco': produtos[cod]['preco'], 'qtd': 1}
                    st.success(f"✅ {n} lido!")
                    st.rerun()
                else:
                    st.warning(f"Produto com código {cod} não encontrado no seu cadastro.")
            else:
                st.warning("Não consegui ler as barras. Tente deixar o código bem reto e nítido!")
