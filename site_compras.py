import streamlit as st
import re

st.set_page_config(page_title="Assistente Ivan", page_icon="🎙️")
st.title("🎙️ Assistente Ivan")

# 1. Inicialização da Memória (Carrinho e Campo de Texto)
if 'sacola' not in st.session_state:
    st.session_state.sacola = []
if 'input_comando' not in st.session_state:
    st.session_state.input_comando = ""

# 2. Função para Processar a Voz/Texto
def processar_entrada():
    texto = st.session_state.widget_input
    if texto:
        # Tenta encontrar um preço (número com vírgula ou ponto) no final da frase
        padrao_preco = re.findall(r"[-+]?\d*\b,?\d+", texto)
        
        if padrao_preco:
            valor_str = padrao_preco[-1].replace(',', '.')
            try:
                valor = float(valor_str)
                # O nome do produto é tudo antes do valor
                nome_produto = texto.replace(padrao_preco[-1], "").strip()
                if not nome_produto: nome_produto = "Produto"
                
                st.session_state.sacola.append({"nome": nome_produto, "preco": valor})
                st.toast(f"✅ {nome_produto} adicionado!")
            except:
                st.error("Não entendi o valor.")
        
        # O segredo para não dar erro: Limpar via widget, não via session_state direto
        st.session_state.widget_input = "" 

# 3. Interface Visual
total = sum(item['preco'] for item in st.session_state.sacola)
st.metric("TOTAL NA SACOLA", f"R$ {total:.2f}")

st.subheader("🎤 Adicionar por Voz ou Código")
st.info("Toque no microfone do teclado e diga: 'Nome do Produto Valor'")

# Usamos 'key' para o widget se auto-gerenciar e evitar o erro que você teve
st.text_input(
    "Digite ou Fale:", 
    key="widget_input", 
    on_change=processar_entrada,
    placeholder="Ex: Açúcar União 6.50"
)

# 4. Exibição da Lista
st.divider()
if st.session_state.sacola:
    for i, item in enumerate(st.session_state.sacola):
        col1, col2 = st.columns([3, 1])
        col1.write(f"{i+1}. {item['nome']}")
        col2.write(f"R$ {item['preco']:.2f}")
    
    if st.button("Limpar Sacola"):
        st.session_state.sacola = []
        st.rerun()
else:
    st.write("Sua sacola está vazia.")
