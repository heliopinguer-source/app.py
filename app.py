import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Sistema de Suporte",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 🔐 CONFIGURAÇÕES PRINCIPAIS (COLOQUE SEUS DADOS AQUI)
# =========================================================
SENHA_ADMIN = "infohelp2026"
# Substitua pelo seu número real (exatamente 13 dígitos)
NUMERO_WHATSAPP = "5515991172115" 
# Link da sua Logomarca (PNG transparente de preferência)
LOGO_URL = "https://infohelptatui.com.br/wp-content/uploads/2023/06/cropped-logo-infohelp.png" 
# =========================================================

SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- DESIGN CUSTOMIZADO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; color: #ffffff; }}
    
    /* Card do Formulário */
    .stForm {{
        background-color: #1c1f26 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        border: 1px solid #3d4450 !important;
    }}
    
    /* Inputs */
    input, textarea, select {{
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #3d4450 !important;
    }}

    /* Botão Principal Laranja */
    div.stButton > button:first-child {{
        background-color: #FF6B00;
        color: white;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        padding: 18px;
        border: none;
    }}
    
    div.stButton > button:hover {{
        background-color: #E65A00;
        color: white;
    }}

    .header-container {{
        text-align: center;
        padding: 40px 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.title("🛡️ Admin")
    aba = st.radio("Selecione:", ["Página do Cliente", "Painel Gestor"])
    st.divider()
    senha_digitada = ""
    if aba == "Painel Gestor":
        senha_digitada = st.text_input("Senha", type="password")

# --- CONTEÚDO ---
if aba == "Página do Cliente":
    # Cabeçalho com sua Logo
    st.markdown(f"""
        <div class="header-container">
            <img src="{LOGO_URL}" width="220">
            <h1 style='color: #FF6B00; margin-top: 15px;'>Portal de Atendimento</h1>
            <p style='color: #888;'>Suporte Técnico Especializado em Tatuí e Região</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_suporte"):
        st.subheader("📝 Detalhes do Chamado")
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome Completo")
            zap_cli = st.text_input("Seu WhatsApp")
        with c2:
            aparelho = st.selectbox("Aparelho", ["Notebook", "PC Gamer", "Monitor", "Impressora", "Software/Rede"])
            modelo = st.text_input("Marca/Modelo")
        
        defeito = st.text_area("O que está acontecendo com o equipamento?")
        
        btn = st.form_submit_button("GERAR PROTOCOLO E FINALIZAR")

    if btn:
        if nome and zap_cli and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            
            # Salva na lista
            st.session_state.db_chamados.append({
                "ID": protocolo, "Cliente": nome, "Equip": f"{aparelho} {modelo}", 
                "Problema": defeito, "Data": datetime.datetime.now().strftime("%d/%m %H:%M")
            })

            # Texto do Zap
            msg = (
                f"*NOVO CHAMADO - INFOHELP*\n"
                f"*Protocolo:* {protocolo}\n"
                f"*Cliente:* {nome}\n"
                f"*Aparelho:* {aparelho} {modelo}\n"
                f"*Defeito:* {defeito}"
            )
            link = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
            
            st.success(f"Protocolo #{protocolo} gerado!")
            st.markdown(f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:20px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.2em;">
                        💬 CLIQUE AQUI PARA ENVIAR NO WHATSAPP
                    </div>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.error("Por favor, preencha todos os campos!")

elif aba == "Painel Gestor":
    if senha_digitada == SENHA_ADMIN:
        st.header("📊 Chamados do Dia")
        if st.session_state.db_chamados:
            st.table(pd.DataFrame(st.session_state.db_chamados))
            if st.button("Limpar Banco de Dados"):
                st.session_state.db_chamados = []
                st.rerun()
        else:
            st.info("Nenhum chamado pendente.")
    elif senha_digitada != "":
        st.error("Senha incorreta.")