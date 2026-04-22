import streamlit as st
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assistente de Compra Ivan", page_icon="🎙️", layout="centered")

# --- ESTILO VISUAL PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: white; }
    .card-total {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 20px; border-radius: 20px; border-left: 8px solid #00ff88;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    .item-sacola {
        background: #1e1e1e; padding: 15px; border-radius: 15px;
        margin-bottom: 10px; border: 1px solid #333;
    }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if "sacola" not in st.session_state: st.session_state.sacola = {}
if "limite" not in st.session_state: st.session_state.limite = 100.0

# --- TELA PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #00ff88;'>🎙️ Assistente Ivan</h1>", unsafe_allow_html=True)

# 1. VISOR DE GASTOS
total_atual = sum(v['preco'] * v['qtd'] for v in st.session_state.sacola.values())
porcentagem = min(total_atual / st.session_state.limite, 1.0) if st.session_state.limite > 0 else 0

st.markdown(f"""
    <div class="card-total">
        <small style="color: #888;">TOTAL NA SACOLA</small>
        <h1 style="margin: 0; font-size: 40px; color: #00ff88;">R$ {total_atual:.2f}</h1>
    </div>
""", unsafe_allow_html=True)
st.progress(porcentagem)

# 2. ENTRADA POR VOZ OU CÓDIGO
st.write("---")
st.subheader("🎤 Adicionar por Voz ou Código")
instrucao = "Toque no microfone do teclado e diga: 'Produto e Valor'"
entrada = st.text_input(instrucao, key="input_comando", placeholder="Ex: Arroz 30.50")

if entrada:
    # Lógica simples para separar nome de preço (ex: Arroz 25.90)
    partes = entrada.rsplit(' ', 1)
    nome_p = partes[0].strip().capitalize()
    try:
        preco_p = float(partes[1].replace(',', '.'))
    except:
        preco_p = 0.0
    
    if nome_p not in st.session_state.sacola:
        st.session_state.sacola[nome_p] = {'preco': preco_p, 'qtd': 1}
    else:
        st.session_state.sacola[nome_p]['qtd'] += 1
    
    st.session_state.input_comando = "" # Limpa campo
    st.rerun()

# 3. LISTA DA SACOLA COM AJUSTE MANUAL
st.write("### 🛒 Itens Selecionados")
if not st.session_state.sacola:
    st.info("Sua sacola está vazia. Fale ou digite algo acima!")
else:
    for nome in list(st.session_state.sacola.keys()):
        item = st.session_state.sacola[nome]
        with st.container():
            st.markdown(f"<div class='item-sacola'><b>{nome}</b> - R$ {item['preco']:.2f}</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            
            # Botão de Diminuir
            if c1.button("➖", key=f"min_{nome}"):
                if item['qtd'] > 1: st.session_state.sacola[nome]['qtd'] -= 1
                else: del st.session_state.sacola[nome]
                st.rerun()
            
            # Mostra Quantidade
            c2.markdown(f"<h4 style='text-align: center;'>{item['qtd']}</h4>", unsafe_allow_html=True)
            
            # Botão de Aumentar
            if c3.button("➕", key=f"plus_{nome}"):
                st.session_state.sacola[nome]['qtd'] += 1
                st.rerun()
            
            # Botão de Excluir
            if c4.button("🗑️", key=f"del_{nome}"):
                del st.session_state.sacola[nome]
                st.rerun()

# 4. CONFIGURAÇÕES NO RODAPÉ
with st.sidebar:
    st.title("⚙️ Ajustes")
    st.session_state.limite = st.number_input("Meu limite (R$):", value=st.session_state.limite)
    if st.button("Limpar Sacola"):
        st.session_state.sacola = {}
        st.rerun()
