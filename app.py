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
# 🔐 CONFIGURAÇÕES (MUDE AQUI)
# =========================================================
SENHA_ADMIN = "infohelp2026"
NUMERO_WHATSAPP = "5515999999999" # Coloque seu número real aqui
# Link da sua logo (certifique-se de que o link termina em .png ou .jpg)
LOGO_URL = "https://infohelptatui.com.br/wp-content/uploads/2023/06/cropped-logo-infohelp.png"
# =========================================================

SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- ESTILO CSS PARA O BOTÃO LARANJA ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0E1117; }}
    
    .stForm {{
        background-color: #1c1f26 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        border: 1px solid #3d4450 !important;
    }}

    /* BOTÃO GERAR PROTOCOLO - LARANJA E VISÍVEL */
    div.stButton > button {{
        background-color: #FF6B00 !important;
        color: white !important;
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 20px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(255, 107, 0, 0.3) !important;
        text-transform: uppercase;
    }}
    
    div.stButton > button:hover {{
        background-color: #E65A00 !important;
        box-shadow: 0px 6px 20px rgba(255, 107, 0, 0.5) !important;
    }}

    .header-container {{ text-align: center; padding: 20px 0; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO LATERAL ---
with st.sidebar:
    aba = st.radio("Navegar:", ["Cliente", "Técnico"])
    senha_digitada = st.text_input("Senha", type="password") if aba == "Técnico" else ""

# --- PÁGINA DO CLIENTE ---
if aba == "Cliente":
    st.markdown(f"""
        <div class="header-container">
            <img src="{LOGO_URL}" width="200">
            <h1 style='color: #FF6B00;'>Portal de Atendimento</h1>
        </div>
    """, unsafe_allow_html=True)

    with st.form("chamado_suporte"):
        nome = st.text_input("Nome Completo")
        zap_cli = st.text_input("WhatsApp (DDD + Número)")
        
        col1, col2 = st.columns(2)
        with col1:
            equip = st.selectbox("Aparelho", ["Notebook", "PC Gamer", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca/Modelo")
            
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
            
            st.success(f"Protocolo #{prot} gerado com sucesso!")
            st.markdown(f"""
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:10px;">
                        💬 CLIQUE AQUI PARA ENVIAR NO WHATSAPP
                    </div>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.error("Preencha todos os campos obrigatórios!")

# --- PAINEL DO TÉCNICO ---
elif aba == "Técnico":
    if senha_digitada == SENHA_ADMIN:
        st.header("📋 Chamados Recebidos")
        if st.session_state.db_chamados:
            st.dataframe(pd.DataFrame(st.session_state.db_chamados), use_container_width=True)
            if st.button("Limpar Lista"):
                st.session_state.db_chamados = []
                st.rerun()
        else:
            st.info("Nenhum chamado pendente.")