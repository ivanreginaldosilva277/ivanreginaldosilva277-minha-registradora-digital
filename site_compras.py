import streamlit as st
import streamlit.components.v1 as components
import requests
import re

st.set_page_config(page_title="Scanner Ivan", page_icon="🛒")

# --- FUNÇÃO DE BUSCA ---
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

st.title("🛒 Scanner Profissional")

# --- O SCANNER DE VÍDEO (SEM BOTÃO DE FOTO) ---
st.subheader("Aponte a câmera traseira para o código")

# Este bloco cria um leitor de vídeo que bipa sozinho
components.html(
    """
    <script src="https://unpkg.com"></script>
    <div style="text-align:center;">
        <video id="video" style="width: 100%; border-radius:10px; border:3px solid #2e7d32;"></video>
    </div>
    <script>
        const codeReader = new ZXing.BrowserMultiFormatReader();
        codeReader.decodeFromVideoDevice(null, 'video', (result, err) => {
            if (result) {
                // Quando lê o código, envia direto para o campo do Streamlit
                const input = window.parent.document.querySelectorAll('input')[0];
                input.value = result.text;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    </script>
    """,
    height=300,
)

# O número aparece aqui sozinho quando a câmera "bipa"
codigo_lido = st.text_input("Código detectado:", key="cod_final")

if codigo_lido:
    cod = re.sub(r'\D', '', codigo_lido)
    nome = buscar_nome(cod)
    if nome:
        st.success(f"✅ {nome}")
        preco = st.number_input("Preço R$:", key=f"p_{cod}")
        if st.button("ADICIONAR AO CARRINHO"):
            st.write(f"Item {nome} somado!")
    else:
        st.warning("Produto novo! Digite o nome:")
        st.text_input("Nome do produto:")
        st.button("Salvar")
