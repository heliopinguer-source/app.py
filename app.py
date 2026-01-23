import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 🔐 CONFIGURAÇÕES
# =========================================================
SENHA_ADMIN = "infohelp2026"
NUMERO_WHATSAPP = "5515999999999" 
# =========================================================

SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- ESTILO CSS PERSONALIZADO ---
st.markdown(f"""
    <style>
    /* Fundo Principal Escuro */
    .stApp {{ background-color: #0E1117; }}
    
    /* Estilo do Card do Formulário */
    .stForm {{
        background-color: #1c1f26 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        border: 1px solid #3d4450 !important;
    }}

    /* TÍTULOS DOS CAMPOS EM LARANJA */
    .stForm label p {{
        color: #FF6B00 !important;
        font-weight: bold !important;
        font-size: 19px !important;
    }}

    /* BOTÃO GERAR PROTOCOLO - LARANJA DESTACADO */
    div.stButton > button {{
        background-color: #FF6B00 !important;
        color: white !important;
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 22px !important;
        padding: 20px !important;
        border: none !important;
        text-transform: uppercase;
        margin-top: 15px;
    }}
    
    div.stButton > button:hover {{
        background-color: #E65A00 !important;
        border: none !important;
    }}

    .header-container {{ text-align: center; padding: 30px 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
with st.sidebar:
    aba = st.radio("Menu:", ["Cliente", "Técnico"])
    senha = st.text_input("Senha Admin", type="password") if aba == "Técnico" else ""

# --- PÁGINA DO CLIENTE ---
if aba == "Cliente":
    st.markdown(f"""
        <div class="header-container">
            <h1 style='color: #FF6B00; font-size: 3em; margin-bottom: 0;'>INFOHELP TATUÍ</h1>
            <p style='color: #ffffff; font-size: 1.2em;'>Portal de Suporte Técnico</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_infohelp"):
        nome = st.text_input("Nome Completo")
        zap_cli = st.text_input("WhatsApp (DDD + Número)")
        
        col1, col2 = st.columns(2)
        with col1:
            equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca e Modelo")
            
        defeito = st.text_area("O que está acontecendo?")
        
        btn_gerar = st.form_submit_button("GERAR PROTOCOLO")

    if btn_gerar:
        if nome and zap_cli and defeito:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            st.session_state.db_chamados.append({
                "ID": prot, "Cliente": nome, "Aparelho": f"{equip} {modelo}", 
                "Defeito": defeito, "Data": datetime.datetime.now().strftime("%d/%m %H:%M")
            })
            
            msg = f"*NOVO CHAMADO INFOHELP*\n*Protocolo:* {prot}\n*Cliente:* {nome}\n*Defeito:* {defeito}"
            link = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
            
            st.success(f"Protocolo #{prot} gerado!")
            st.markdown(f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold; font-size: 1.1em;">
                        💬 ENVIAR PARA O WHATSAPP DA INFOHELP
                    </div>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Por favor, preencha todos os campos.")

# --- PAINEL TÉCNICO ---
elif aba == "Técnico":
    if senha == SENHA_ADMIN:
        st.header("📋 Chamados Pendentes")
        if st.session_state.db_chamados:
            st.dataframe(pd.DataFrame(st.session_state.db_chamados), use_container_width=True)
            if st.button("Limpar Histórico"):
                st.session_state.db_chamados = []
                st.rerun()
        else:
            st.info("Nenhum chamado registrado.")