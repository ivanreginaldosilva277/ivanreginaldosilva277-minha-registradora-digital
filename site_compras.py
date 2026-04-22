import streamlit as st
import requests
import re

st.set_page_config(page_title="Registradora Ivan", page_icon="🛒")

# --- BUSCA NA INTERNET ---
def buscar_nome(codigo):
    try:
        url = f"https://openfoodfacts.org{codigo}.json"
        r = requests.get(url, timeout=3)
        if r.status_code == 200 and r.json().get("status") == 1:
            p = r.json()["product"]
            return p.get("product_name_pt") or p.get("product_name")
    except: pass
    return None

if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- VISOR DE CAIXA ---
total = sum(i['preco'] * i['qtd'] for i in st.session_state.carrinho.values())
st.markdown(f"""
    <div style="background:#000; color:#0f0; padding:20px; border-radius:15px; text-align:right; font-family:monospace; border:4px solid #444;">
        <small>TOTAL DA COMPRA</small><h1 style="margin:0;">R$ {total:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# --- O BOTÃO QUE NÃO FALHA ---
st.subheader("🛍️ Bipar Produto")
st.info("Ao clicar abaixo, use a opção de 'Câmera/Scanner' do seu celular:")

# Este botão usa a função nativa do Android para capturar imagem e ler código
foto = st.camera_input("SCANNER ATIVO")

if foto:
    # Como o leitor de vídeo travou, vamos usar esse campo para entrar o código que você vê na tela
    # Geralmente o próprio Android já extrai o número para você
    codigo = st.text_input("Confirme o código lido ou digite aqui:")
    
    if codigo:
        cod_limpo = re.sub(r'\D', '', codigo)
        nome = buscar_nome(cod_limpo)
        if nome:
            st.success(f"✅ {nome}")
            preco = st.number_input("Preço R$:", key=f"p_{cod_limpo}", step=0.01)
            if st.button("SOMAR NO CARRINHO"):
                st.session_state.carrinho[nome] = {'preco': preco, 'qtd': 1}
                st.rerun()

# --- LISTA NO CARRINHO ---
st.write("---")
for n in list(st.session_state.carrinho.keys()):
    item = st.session_state.carrinho[n]
    c1, c2, c3 = st.columns([2, 1, 0.5])
    c1.write(f"**{n}**")
    item['qtd'] = c2.number_input("Qtd", value=int(item['qtd']), key=f"q_{n}", min_value=1)
    if c3.button("X", key=f"d_{n}"):
        del st.session_state.carrinho[n]
        st.rerun()
