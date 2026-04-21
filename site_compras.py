import streamlit as st
import streamlit.components.v1 as components
import requests
import re
import json
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_DADOS = "banco_usuarios_final.json"
ARQUIVO_MEMORIA = "produtos_aprendidos.json"

st.set_page_config(page_title="Registradora Ivan", page_icon="📟")

# --- FUNÇÕES DE BUSCA ---
def buscar_produto(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

# --- ESTILO REGISTRADORA ---
st.markdown("<style>.visor { background:#000; color:#0f0; padding:20px; border-radius:10px; text-align:right; font-family:monospace; border:3px solid #444; }</style>", unsafe_allow_html=True)

if "logado" not in st.session_state: st.session_state.logado = False
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# (O código de LOGIN e CADASTRO que você já tem deve continuar aqui...)

if st.session_state.logado:
    st.markdown("<div class='visor'><small>SCANNER ATIVO</small><h1>AGUARDANDO...</h1></div>", unsafe_allow_html=True)
    
    st.subheader("📟 LEITOR DE CÓDIGO (VIVO)")
    
    # ESTE É O SCANNER QUE NÃO PRECISA BATER FOTO
    # Ele usa a biblioteca ZXing que é a melhor do mundo para isso
    components.html(
        """
        <script src="https://unpkg.com"></script>
        <div style="text-align:center;">
            <video id="video" style="width: 100%; max-width: 400px; border: 2px solid #2e7d32; border-radius:10px;"></video>
            <p id="resultado" style="font-weight:bold; color:#2e7d32;"></p>
        </div>
        <script>
            const codeReader = new ZXing.BrowserMultiFormatReader();
            codeReader.decodeFromVideoDevice(null, 'video', (result, err) => {
                if (result) {
                    document.getElementById('resultado').textContent = "LIDO: " + result.text;
                    // Envia o código para o campo de texto do Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        key: 'cod_bipado',
                        value: result.text
                    }, '*');
                }
            });
        </script>
        """,
        height=350,
    )

    # O código aparece aqui sozinho após o "BIP"
    cod_final = st.text_input("Código capturado pelo scanner:", key="cod_bipado")

    if cod_final:
        cod_limpo = re.sub(r'\D', '', cod_final)
        nome = buscar_produto(cod_limpo)
        if nome:
            st.success(f"📦 {nome}")
            preco = st.number_input("Preço R$:", key=f"p_{cod_limpo}")
            if st.button("REGISTRAR ITEM"):
                st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()
        else:
            st.warning("Produto não achado. Digite o nome:")
            n_m = st.text_input("Nome:")
            p_m = st.number_input("Preço:")
            if st.button("SALVAR"):
                st.session_state.carrinho[n_m] = {'preco': p_m, 'qtd': 1}
                st.rerun()
