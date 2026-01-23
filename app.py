import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte Profissional",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 🔐 CONFIGURAÇÕES PRINCIPAIS
# =========================================================
SENHA_ADMIN = "infohelp2026"        
NUMERO_WHATSAPP = "5515991172115"  # Substitua pelo seu número real
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2906/2906274.png" # Substitua pelo link da sua logo real
# =========================================================

SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- DESIGN PERSONALIZADO (CSS) ---
st.markdown(f"""
    <style>
    /* Fundo e Geral */
    .stApp {{
        background-color: #121212;
        color: #ffffff;
    }}
    
    /* Card do Formulário */
    .stForm {{
        background-color: #ffffff !important;
        border-radius: 15px !important;
        padding: 30px !important;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.5) !important;
        border: none !important;
    }}
    
    /* Textos dentro do Form (Preto para leitura) */
    .stForm label, .stForm p, .stForm h3 {{
        color: #121212 !important;
    }}

    /* Botão de Enviar (Laranja) */
    div.stButton > button:first-child {{
        background-color: #FF6B00;
        color: white;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        transition: 0.3s;
    }}
    
    div.stButton > button:hover {{
        background-color: #E65A00;
        border: none;
        color: white;
    }}

    /* Estilo do Botão WhatsApp Final */
    .whatsapp-link {{
        background-color: #25D366;
        color: white !important;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        text-decoration: none;
        display: block;
        font-weight: bold;
        font-size: 20px;
        margin-top: 20px;
        box-shadow: 0px 4px 15px rgba(37, 211, 102, 0.4);
    }}

    /* Cabeçalho */
    .header-box {{
        text-align: center;
        padding: 20px 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (ADM) ---
with st.sidebar:
    st.title("⚙️ Administração")
    aba = st.radio("Navegar:", ["📋 Área do Cliente", "🔐 Painel ADM"])
    st.divider()
    senha_digitada = ""
    if aba == "🔐 Painel ADM":
        senha_digitada = st.text_input("Senha de Acesso", type="password")

# --- CONTEÚDO PRINCIPAL ---

if aba == "📋 Área do Cliente":
    # Cabeçalho Profissional
    st.markdown(f"""
        <div class="header-box">
            <img src="{LOGO_URL}" width="100">
            <h1 style='color: #FF6B00; margin-bottom: 5px;'>INFOHELP TATUÍ</h1>
            <p style='color: #bbbbbb; font-size: 1.1em;'>Assistência Técnica Renomada em Hardware e Software</p>
        </div>
    """, unsafe_allow_html=True)

    # Formulário em Card Branco
    with st.form("chamado_form", clear_on_submit=True):
        st.markdown("### 📋 Abertura de Chamado")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo ou Empresa")
            zap_cli = st.text_input("WhatsApp para Contato")
        with col2:
            equip = st.selectbox("Tipo de Equipamento", ["Notebook", "PC Gamer", "Desktop Office", "Monitor", "Impressora", "Outro"])
            modelo = st.text_input("Marca / Modelo (Ex: Dell Inspiron)")
        
        defeito = st.text_area("Descreva o problema detalhadamente")
        
        submit = st.form_submit_button("GERAR PROTOCOLO DE ATENDIMENTO")

    if submit:
        if nome and zap_cli and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%d%H%M')}"
            
            # Salva na Memória
            st.session_state.db_chamados.append({
                "ID": protocolo, "Cliente": nome, "Zap": zap_cli, 
                "Equip": f"{equip} {modelo}", "Relato": defeito, 
                "Data": datetime.datetime.now().strftime("%d/%m - %H:%M")
            })

            # Prepara Mensagem WhatsApp
            msg_texto = (
                f"*NOVO CHAMADO - INFOHELP TATUÍ*\n"
                f"----------------------------------\n"
                f"*Protocolo:* {protocolo}\n"
                f"*Cliente:* {nome}\n"
                f"*Aparelho:* {equip} {modelo}\n"
                f"*Defeito:* {defeito}\n"
                f"----------------------------------"
            )
            link_whatsapp = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg_texto)}"
            
            st.balloons()
            st.markdown(f"""
                <div style="background: #1e1e1e; padding: 25px; border-radius: 15px; border-left: 5px solid #FF6B00; margin-top: 20px;">
                    <h3 style="color: #FF6B00; margin-top:0;">✅ Quase lá, {nome}!</h3>
                    <p style="color: #ffffff;">O protocolo <strong>#{protocolo}</strong> foi gerado. Clique no botão abaixo para nos enviar os detalhes via WhatsApp e confirmar seu atendimento.</p>
                    <a href="{link_whatsapp}" target="_blank" class="whatsapp-link">
                        💬 FINALIZAR NO WHATSAPP
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")

elif aba == "🔐 Painel ADM":
    if senha_digitada == SENHA_ADMIN:
        st.header("📊 Painel de Controle Técnico")
        if not st.session_state.db_chamados:
            st.info("Nenhum chamado registrado até o momento.")
        else:
            df = pd.DataFrame(st.session_state.db_chamados)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Limpar Todos os Dados"):
                st.session_state.db_chamados = []
                st.rerun()
    elif senha_digitada != "":
        st.error("Senha incorreta.")