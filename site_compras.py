import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="Controle de Compra Premium", page_icon="💰", layout="centered")

# --- ESTILO CSS (MODO ESCURO E ELEGANTE) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: white; }
    .card-total {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 25px;
        border-radius: 20px;
        border-left: 8px solid #00ff88;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #00ff88 0%, #00bd6b 100%);
        color: #0e1117;
        border: none;
    }
    .item-row {
        background: #1e1e1e;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if "carrinho" not in st.session_state: st.session_state.carrinho = []
if "limite" not in st.session_state: st.session_state.limite = 0.0

# --- TELA PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #00ff88;'>📊 Central de Compras Ivan</h1>", unsafe_allow_html=True)

# 1. DEFINIÇÃO DE LIMITE
with st.expander("⚙️ Configurar Limite de Gastos", expanded=st.session_state.limite == 0):
    st.session_state.limite = st.number_input("Quanto você pode gastar hoje? (R$)", value=st.session_state.limite, step=10.0)

# 2. VISOR DE IMPACTO
total_atual = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho)
porcentagem = min(total_atual / st.session_state.limite, 1.0) if st.session_state.limite > 0 else 0

st.markdown(f"""
    <div class="card-total">
        <small style="color: #888;">TOTAL ACUMULADO</small>
        <h1 style="margin: 0; font-size: 45px; color: #00ff88;">R$ {total_atual:.2f}</h1>
    </div>
""", unsafe_allow_html=True)

# Barra de progresso visual
if st.session_state.limite > 0:
    cor_barra = "green" if porcentagem < 0.8 else "orange" if porcentagem < 1.0 else "red"
    st.progress(porcentagem)
    restante = st.session_state.limite - total_atual
    if restante >= 0:
        st.markdown(f"<p style='text-align: right; color: #888;'>Você ainda tem <b>R$ {restante:.2f}</b> livres</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='text-align: right; color: #ff4b4b;'>⚠️ Limite excedido em <b>R$ {abs(restante):.2f}</b></p>", unsafe_allow_html=True)

# 3. ADICIONAR PRODUTO (RÁPIDO)
st.write("---")
with st.form("add_item", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    nome = col1.text_input("📦 Produto:", placeholder="Ex: Arroz")
    preco = col2.number_input("💰 Preço:", min_value=0.0, step=0.01, format="%.2f")
    qtd = col3.number_input("🔢 Qtd:", min_value=1, value=1)
    
    if st.form_submit_button("➕ ADICIONAR À LISTA"):
        if nome and preco > 0:
            st.session_state.carrinho.append({"nome": nome, "preco": preco, "qtd": qtd})
            st.rerun()

# 4. LISTA DE CONFERÊNCIA
st.write("### 🛒 Sua Sacola")
if not st.session_state.carrinho:
    st.info("Sua lista está vazia. Adicione o primeiro item acima!")
else:
    for i, item in enumerate(reversed(st.session_state.carrinho)):
        idx = len(st.session_state.carrinho) - 1 - i
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 0.5])
            subtotal = item['preco'] * item['qtd']
            c1.markdown(f"**{item['nome']}**<br><small>{item['qtd']}x R$ {item['preco']:.2f}</small>", unsafe_allow_html=True)
            c2.markdown(f"<p style='margin-top: 10px;'>R$ {subtotal:.2f}</p>", unsafe_allow_html=True)
            if c3.button("❌", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
    
    if st.button("🗑️ LIMPAR TUDO", use_container_width=True):
        st.session_state.carrinho = []
        st.rerun()

# 5. RODAPÉ DE AJUDA
st.write("---")
st.markdown(f"""
    <a href="https://wa.me" style="text-decoration: none;">
        <div style="background: #25d366; color: white; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold;">
            💬 Dúvidas ou Suporte? Fale com o Ivan
        </div>
    </a>
""", unsafe_allow_html=True)
