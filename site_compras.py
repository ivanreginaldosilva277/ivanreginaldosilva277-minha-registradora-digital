import streamlit as st
import re

st.set_page_config(page_title="Assistente Ivan", page_icon="🎙️")
st.title("🎙️ Assistente Ivan")

# 1. BANCO DE DADOS REAL (Produtos comuns em SP)
if 'mercado_db' not in st.session_state:
    st.session_state.mercado_db = {
        "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
        "7896000705023": {"nome": "Feijão Camil Carioca 1kg", "preco": 9.20},
        "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
        "7891000054307": {"nome": "Leite Ninho Integral", "preco": 6.20},
        "7891008121021": {"nome": "Café Pilão 500g", "preco": 24.90},
        "7891150004125": {"nome": "Detergente Ypê Neutro", "preco": 2.60},
        "7891150022068": {"nome": "Sabão OMO Lavagem Perfeita", "preco": 26.90},
        "7891321001221": {"nome": "Açúcar União 1kg", "preco": 4.80},
    }

if 'sacola' not in st.session_state:
    st.session_state.sacola = []

# 2. FUNÇÃO DE PROCESSAMENTO MELHORADA
def processar_entrada():
    texto = st.session_state.widget_input.strip()
    if texto:
        # Tira tudo que não é número para testar se é Código de Barras
        apenas_numeros = re.sub(r'\D', '', texto)
        
        # Se detectou um número longo (Código de Barras)
        if len(apenas_numeros) >= 8:
            if apenas_numeros in st.session_state.mercado_db:
                item = st.session_state.mercado_db[apenas_numeros]
                st.session_state.sacola.append({"nome": item['nome'], "preco": item['preco']})
                st.toast(f"✅ Adicionado: {item['nome']} - R$ {item['preco']:.2f}")
            else:
                st.error(f"❌ Código '{apenas_numeros}' não encontrado no banco de dados.")
        
        # Se for Nome + Valor (Voz)
        else:
            padrao_preco = re.findall(r"[-+]?\d*\b,?\d+", texto)
            if padrao_preco:
                try:
                    valor_str = padrao_preco[-1].replace(',', '.')
                    valor = float(valor_str)
                    nome_produto = texto.replace(padrao_preco[-1], "").strip()
                    if not nome_produto: nome_produto = "Produto Avulso"
                    
                    st.session_state.sacola.append({"nome": nome_produto, "preco": valor})
                    st.toast(f"✅ Adicionado: {nome_produto} - R$ {valor:.2f}")
                except:
                    st.error("⚠️ Não entendi o preço. Diga ex: 'Leite 5.50'")
            else:
                st.warning("🎤 Diga o nome e o valor. Ex: 'Bolacha 3.50'")
        
        st.session_state.widget_input = ""

# 3. INTERFACE
total = sum(item['preco'] for item in st.session_state.sacola)
st.metric("TOTAL NA SACOLA", f"R$ {total:.2f}")

st.text_input("🎤 Fale ou digite aqui:", key="widget_input", on_change=processar_entrada)

st.divider()
st.subheader("📋 Itens na Sacola")

if st.session_state.sacola:
    for i, item in enumerate(st.session_state.sacola):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{i+1}. {item['nome']}**")
        col2.write(f"R$ {item['preco']:.2f}")
    
    if st.button("Limpar Sacola"):
        st.session_state.sacola = []
        st.rerun()
else:
    st.info("A sacola está vazia. Fale o nome e o preço ou use um código cadastrado.")
