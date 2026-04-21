        st.subheader("📸 Escanear por Foto")
        foto = st.camera_input("Tire foto do código de barras")
        
        if foto:
            # 1. Converter imagem
            bytes_data = foto.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # 2. Leitor OpenCV (Ajustado para não dar erro de desempacotamento)
            detector = cv2.barcode.BarcodeDetector()
            resultado = detector.detectAndDecode(img)
            
            if resultado and resultado[0]:
                # Pega o código detectado
                cod = resultado[0] if isinstance(resultado[0], (list, np.ndarray)) else resultado[0]
                
                if cod in produtos:
                    n = produtos[cod]['nome']
                    if n in st.session_state.carrinho:
                        st.session_state.carrinho[n]['qtd'] += 1
                    else:
                        st.session_state.carrinho[n] = {'preco': produtos[cod]['preco'], 'qtd': 1}
                    st.success(f"✅ {n} lido!")
                    st.rerun()
                else:
                    st.warning(f"Código {cod} não cadastrado.")
            else:
                st.warning("Não consegui ler as barras. Tente focar melhor ou limpar a lente!")
