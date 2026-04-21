import streamlit as st
import re
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES DO IVAN ---
WHATSAPP_CONTATO = "5511917519746"
ARQUIVO_DADOS = "banco_mercado_final.json"

st.set_page_config(page_title="Minha Compra Segura", page_icon="🛒", layout="centered")

# --- BANCO DE DADOS (EXPANDIDO) ---
produtos = {
    # BEBIDAS
    "7894900011517": {"nome": "Coca-Cola Lata 350ml", "preco": 4.50},
    "7894900010015": {"nome": "Coca-Cola Pet 2L", "preco": 11.90},
    "7894900700046": {"nome": "Guaraná Antarctica 2L", "preco": 9.50},
    "7894900019810": {"nome": "Fanta Laranja 2L", "preco": 8.90},
    "7894900530001": {"nome": "Água Crystal 500ml", "preco": 2.50},
    "7891991000854": {"nome": "Cerveja Skol Lata 350ml", "preco": 3.90},
    "7891991010389": {"nome": "Cerveja Brahma Duplo Malte 350ml", "preco": 4.20},
    "7891991015339": {"nome": "Cerveja Heineken Long Neck", "preco": 7.50},
    "7896001000103": {"nome": "Leite Itambé Integral 1L", "preco": 5.80},
    "7896001000110": {"nome": "Leite Itambé Desnatado 1L", "preco": 5.90},
    "7891000061327": {"nome": "Suco Maguary Uva 1L", "preco": 6.80},
    "7896062800162": {"nome": "Suco Del Valle Uva 1L", "preco": 7.50},

    # --- MERCEARIA SALGADA (ITENS DE PESO) ---
    "7896005818063": {"nome": "Arroz Tio João 1kg", "preco": 6.90},
    "7896005818018": {"nome": "Arroz Tio João 5kg", "preco": 32.50},
    "7896005818124": {"nome": "Arroz Tio João Integral 1kg", "preco": 7.80},
    "7896000705023": {"nome": "Feijão Camil Carioca 1kg", "preco": 9.20},
    "7896000705146": {"nome": "Feijão Camil Preto 1kg", "preco": 9.50},
    "7891080000018": {"nome": "Óleo de Soja Liza 900ml", "preco": 7.80},
    "7891080000049": {"nome": "Óleo de Milho Liza 900ml", "preco": 12.50},
    "7896013410112": {"nome": "Sal Lebre Refinado 1kg", "preco": 2.50},
    "7896022201015": {"nome": "Macarrão Adria Espaguete", "preco": 4.80},
    "7896022201039": {"nome": "Macarrão Adria Parafuso", "preco": 4.80},
    "7891021000213": {"nome": "Maionese Hellmann's 500g", "preco": 9.90},
    "7891021003443": {"nome": "Ketchup Hellmann's 380g", "preco": 10.50},
    "7896013303681": {"nome": "Molho de Tomate Pomarola 300g", "preco": 3.80},

    # --- MATINAIS E DOCES ---
    "7891000053506": {"nome": "Leite Moça Condensado 395g", "preco": 8.50},
    "7891000100101": {"nome": "Nescau 400g", "preco": 10.90},
    "7891000021208": {"nome": "Leite Ninho Lata 400g", "preco": 19.50},
    "7896003701220": {"nome": "Açúcar União 1kg", "preco": 4.90},
    "7891008121021": {"nome": "Café Pilão 500g", "preco": 24.90},
    "7891008221028": {"nome": "Café Pilão Almofada 250g", "preco": 13.50},
    "7891000454709": {"nome": "Cereal Matinal Sucrilhos Kellogg's", "preco": 14.90},
    "7891000078103": {"nome": "Biscoito Passatempo Recheado", "preco": 3.50},
    "7891000026609": {"nome": "Biscoito Negresco", "preco": 3.80},
    "7891000001202": {"nome": "Biscoito Bono Chocolate", "preco": 3.80},
    "7896007231457": {"nome": "Torrada Bauducco 142g", "preco": 5.50},

    # --- SNACKS E SALGADINHOS ---
    "7892840813083": {"nome": "Batata Lay's Clássica 80g", "preco": 8.50},
    "7892840222120": {"nome": "Doritos Queijo Nacho 140g", "preco": 13.90},
    "7892840800045": {"nome": "Salgadinho Cheetos 140g", "preco": 9.50},
    "7892840813137": {"nome": "Batata Ruffles Original 167g", "preco": 14.50},

    # --- HIGIENE E LIMPEZA ---
    "7891150004125": {"nome": "Detergente Ypê Neutro 500ml", "preco": 2.60},
    "7891150022068": {"nome": "Sabão OMO Lavagem Perfeita 1.6kg", "preco": 26.90},
    "7891150022075": {"nome": "Sabão OMO Lavagem Perfeita 800g", "preco": 14.50},
    "7891150025212": {"nome": "Amaciante Ypê Aconchego 2L", "preco": 15.90},
    "7891150014025": {"nome": "Desinfetante Pinho Sol 500ml", "preco": 6.50},
    "7891024132058": {"nome": "Sabonete Dove Original 90g", "preco": 4.50},
    "7891095012303": {"nome": "Creme Dental Colgate 90g", "preco": 6.80},
    "7896007545110": {"nome": "Papel Higiênico Neve 12un", "preco": 24.00},
    "7891010041531": {"nome": "Shampoo Pantene 400ml", "preco": 19.90},
}

# --- ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 10px; background-color: #2e7d32; color: white; height: 3em; font-weight: bold; }}
    .whatsapp-btn {{ background-color: #25d366; color: white; padding: 15px; border-radius: 15px; text-align: center; text-decoration: none; display: block; font-weight: bold; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f: return json.load(f)
    return {"usuarios": {}, "historico": {}}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f: json.dump(dados, f)

# --- LÓGICA DE NAVEGAÇÃO ---
if "tela" not in st.session_state: st.session_state.tela = "login"
if "carrinho" not in st.session_state: st.session_state.carrinho = {}

# --- FUNÇÃO PARA PROCESSAR CÓDIGO ---
def processar_codigo():
    input_usuario = st.session_state.input_scan
    cod_limpo = re.sub(r'\D', '', input_usuario)
    
    if cod_limpo in produtos:
        prod = produtos[cod_limpo]
        nome_p = prod['nome']
        if nome_p in st.session_state.carrinho:
            st.session_state.carrinho[nome_p]['qtd'] += 1
        else:
            st.session_state.carrinho[nome_p] = {'preco': prod['preco'], 'qtd': 1}
        st.toast(f"✅ {nome_p} adicionado!")
    elif cod_limpo != "":
        st.error(f"Produto {cod_limpo} não encontrado!")
    
    st.session_state.input_scan = "" # Limpa o campo após processar

# --- TELA DE LOGIN ---
if st.session_state.tela == "login":
    st.markdown("<h1 style='text-align: center;'>🛒 Calculadora de Mercado</h1>", unsafe_allow_html=True)
    st.markdown(f'<a href="https://wa.me{WHATSAPP_CONTATO}" class="whatsapp-btn">💬 Fale com o Ivan</a>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        u_log = st.text_input("Login (CPF ou Nome):").strip().lower()
        u_sen = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR 🚀"):
            dados = carregar_dados()
            if u_log in dados["usuarios"] and dados["usuarios"][u_log]["senha"] == u_sen:
                st.session_state.usuario_logado = u_log
                st.session_state.tela = "app"
                st.rerun()
            else: st.error("Dados incorretos.")
    
    if st.button("Não tem conta? Cadastre-se aqui 📝"):
        st.session_state.tela = "cadastro"
        st.rerun()

# --- TELA DE CADASTRO ---
elif st.session_state.tela == "cadastro":
    st.title("📝 Cadastro Novo")
    with st.form("c_form"):
        n_c = st.text_input("Nome:")
        c_c = st.text_input("CPF (Login):")
        s_c = st.text_input("Senha:", type="password")
        if st.form_submit_button("CADASTRAR ✅"):
            login_id = re.sub(r'\D', '', c_c)
            if n_c and login_id and s_c:
                d = carregar_dados()
                exp = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                d["usuarios"][login_id] = {"nome": n_c, "senha": s_c, "exp": exp, "pago": False}
                d["historico"][login_id] = {}
                salvar_dados(d)
                st.success("Cadastrado com sucesso! Volte ao login.")
            else: st.error("Preencha todos os campos.")
    if st.button("⬅️ Voltar"):
        st.session_state.tela = "login"
        st.rerun()

# --- TELA DO APLICATIVO ---
elif st.session_state.tela == "app":
    st.title(f"👋 Olá, {st.session_state.usuario_logado.capitalize()}")
    
    if st.sidebar.button("⬅️ Sair / Início"):
        st.session_state.tela = "login"
        st.rerun()

    aba1, aba2 = st.tabs(["🛒 Compra Atual", "📂 Histórico"])

    with aba1:
        st.subheader("Registrar Produto")
        # Usamos o on_change para disparar a função assim que der Enter
        st.text_input("Digite/Fale o código e dê Enter:", key="input_scan", on_change=processar_codigo)
        
        st.write("---")
        total = 0
        for n in list(st.session_state.carrinho.keys()):
            item = st.session_state.carrinho[n]
            sub = item['preco'] * item['qtd']
            total += sub
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(f"**{n}**")
            with col2:
                q = st.number_input("Qtd", 0, 100, int(item['qtd']), key=f"q_{n}")
                if q != item['qtd']:
                    if q == 0: del st.session_state.carrinho[n]
                    else: st.session_state.carrinho[n]['qtd'] = q
                    st.rerun()
            col3.write(f"R${sub:.2f}")
        
        st.metric("TOTAL DA COMPRA", f"R$ {total:.2f}")
        
        if st.button("💾 Salvar esta Compra"):
            dados = carregar_dados()
            dados["historico"][st.session_state.usuario_logado] = st.session_state.carrinho
            salvar_dados(dados)
            st.success("Lista salva com sucesso!")

    with aba2:
        dados = carregar_dados()
        hist = dados["historico"].get(st.session_state.usuario_logado, {})
        if hist:
            st.write("Última lista salva:")
            for n, i in hist.items(): st.text(f"• {i['qtd']}x {n}")
            if st.button("🔄 Recuperar esta lista para o carrinho"):
                st.session_state.carrinho = hist
                st.rerun()
        else: st.info("Nada salvo ainda.")
