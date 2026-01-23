import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA (Menu agora começa oculto) ---
st.set_page_config(
    page_title="InfoHelp Tatuí - Suporte",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed"  # <--- ISSO FAZ O MENU COMECAR OCULTO
)

# =========================================================
# 🔐 CONFIGURAÇÕES PRINCIPAIS
# =========================================================
SENHA_ADMIN = "infohelp2026"        
NUMERO_WHATSAPP = "5515999999999"   # COLOQUE SEU NÚMERO AQUI
# =========================================================

SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* Estilização para o botão do WhatsApp ficar bem destacado */
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 18px;
        text-align: center;
        display: block;
        text-decoration: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (Agora fica escondida até clicar na seta) ---
with st.sidebar:
    st.title("Menu InfoHelp")
    aba = st.radio("Navegar para:", ["📋 Abrir Chamado", "🔐 Painel ADM"])
    st.write("---")
    
    senha_digitada = ""
    if aba == "🔐 Painel ADM":
        senha_digitada = st.text_input("Senha Admin", type="password")

# --- CONTEÚDO PRINCIPAL ---
if aba == "📋 Abrir Chamado":
    st.header("🏢 Portal de Atendimento - InfoHelp Tatuí")
    
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu Nome Completo")
            zap_cliente = st.text_input("Seu WhatsApp com DDD")
        with col2:
            aparelho = st.selectbox("Equipamento", ["Notebook", "Desktop / PC Gamer", "Monitor", "Impressora", "Outro"])
            modelo = st.text_input("Marca / Modelo")
        
        detalhes_defeito = st.text_area("O que está acontecendo? (Descreva o defeito)")
        btn_enviar = st.form_submit_button("GERAR PROTOCOLO")

    if btn_enviar:
        if nome and zap_cliente and detalhes_defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            
            # Salvar no sistema
            st.session_state.db_chamados.append({
                "ID": protocolo, "Cliente": nome, "WhatsApp": zap_cliente,
                "Equipamento": aparelho, "Relato": detalhes_defeito,
                "Data": datetime.datetime.now().strftime("%d/%m %H:%M")
            })
            
            # Mensagem WhatsApp
            texto_formatado = (
                f"*INFOHELP TATUÍ - NOVO CHAMADO*\n\n"
                f"*Protocolo:* {protocolo}\n"
                f"*Cliente:* {nome}\n"
                f"*Equipamento:* {aparelho}\n"
                f"*DEFEITO:* {detalhes_defeito}"
            )
            link_final = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(texto_formatado)}"
            
            st.success(f"✅ Protocolo #{protocolo} gerado!")
            st.markdown(f'<a href="{link_final}" target="_blank" class="whatsapp-btn">💬 ENVIAR VIA WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Preencha todos os campos.")

elif aba == "🔐 Painel ADM":
    if senha_digitada == SENHA_ADMIN:
        st.header("📊 Gestão de Chamados")
        if not st.session_state.db_chamados:
            st.info("Nenhum chamado recebido.")
        else:
            st.table(pd.DataFrame(st.session_state.db_chamados))
    elif senha_digitada != "":
        st.error("❌ Senha incorreta.")
    else:
        st.info("Digite a senha na barra lateral (clique na seta > no canto superior esquerdo).")