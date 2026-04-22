import streamlit as st
import re

st.set_page_config(page_title="Assistente Ivan", page_icon="🎙️")
st.title("🎙️ Assistente Ivan")

# 1. BANCO DE DADOS (Seus produtos cadastrados)
if 'mercado_db' not in st.session_state:
    st.session_state.mercado_db = {
        "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
        "7894900010015": {"nome": "Coca-Cola Pet 2L", "preco": 11.90},
        "7894900700046": {"nome": "Guaraná Antarctica 2L", "preco": 9.50},
        "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
        "7896000705023": {"nome": "Feijão Camil Carioca 1kg", "preco": 9.20},
        "7891080000018": {"nome": "Óleo de Soja Liza 900ml", "preco": 7.80},
        "7891150004125": {"nome": "Detergente Ypê Neutro", "preco": 2.60},
        "7891150022068": {"nome": "Sabão OMO Lavagem Perfeita", "preco": 26.90},
        "7891008121021": {"nome": "Café Pilão 500g", "preco": 24.90},
        "7891000021208": {"nome": "Leite Ninho Lata 400g", "preco": 19.50},
    }

# Inicialização da Sacola
if 'sacola' not in st.session_state:
    st.session_state.sacola = []

# 2. FUNÇÃO INTELIGENTE (Diferencia Código de Voz)
def processar_entrada():
    texto = st.session_state.widget_input.strip()
    if texto:
        # Tira espaços e vê se é apenas um número longo (Código de barras)
        apenas_numeros = re.sub(r'\D', '', texto)
        
        # LÓGICA A: CÓDIGO DE BARRAS
        if len(apenas_numeros) >= 8:
            if apenas_numeros in st.session_state.mercado_db:
                item = st.session_state.mercado_db[apenas_numeros]
                st.session_state.sacola.append({"nome": item['nome'], "preco": item['preco']})
                st.toast(f"✅ {item['nome']} (via código)")
            else:
                st.error(f"Código {apenas_numeros} não cadastrado.")
        
        # LÓGICA B: VOZ (PRODUTO + VALOR)
        else:
            padrao_preco = re.findall(r"[-+]?\d*\b,?\d+", texto)
            if padrao_preco:
                try:
                    valor_str = padrao_preco[-1].replace(',', '.')
                    valor = float(valor_str)
                    nome_produto = texto.replace(padrao_preco[-1], "").strip()
                    if not nome_produto: nome_produto = "Produto Avulso"
                    
                    st.session_state.sacola.append({"nome": nome_produto, "preco": valor})
                    st.toast(f"✅ {nome_produto} (R$ {valor:.2f})")
                except:
                    st.error("Não entendi o valor.")
            else:
                st.warning("Diga o nome e o valor (Ex: Leite 5.50)")
        
        # Limpa o campo
        st.session_state.widget_input = ""

# 3. INTERFACE VISUAL
total = sum(item['preco'] for item in st.session_state.sacola)
st.metric("TOTAL NA SACOLA", f"R$ {total:.2f}")

st.subheader("🎤 Adicionar por Voz ou Código")
st.info("Fale o código de barras OU 'Nome e Valor' (Ex: Arroz 30.00)")

st.text_input(
    "Digite ou Fale:", 
    key="widget_input", 
    on_change=processar_entrada,
    placeholder="Toque no microfone e fale..."
)

# 4. EXIBIÇÃO DA LISTA
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
