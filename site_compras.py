        foto = st.camera_input("Tire foto do código de barras")
        if foto:
            # Converter imagem
            bytes_data = foto.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Novo Leitor (OpenCV Wechat) - O mais forte para celular
            detector = cv2.wechat_qrcode_WeChatQRCode()
            codigos, pontos = detector.detectAndDecode(img)

            if codigos:
                codigo_lido = codigos[0]
                if codigo_lido in produtos:
                    item = produtos[codigo_lido]
                    nome_p = item['nome']
                    if nome_p in st.session_state.carrinho:
                        st.session_state.carrinho[nome_p]['qtd'] += 1
                    else:
                        st.session_state.carrinho[nome_p] = {'preco': item['preco'], 'qtd': 1}
                    st.success(f"✅ {nome_p} lido!")
                    st.rerun()
                else:
                    st.warning(f"Código {codigo_lido} não cadastrado.")
            else:
                st.warning("Não consegui ler. Tente focar melhor!")
