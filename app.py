import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí", page_icon="💻", layout="wide")

# =========================================================
# ⚠️ CONFIGURAÇÃO DE SEGURANÇA (Mude aqui!)
# =========================================================
SENHA_ADMIN_DEFINIDA = "infohelp123"  # <--- ESSA É A SUA SENHA
WHATSAPP_TECNICO = "5515999999999"    # Seu número com DDD
# =========================================================

# Inicialização do Banco de Dados temporário
if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🚀 InfoHelp Tatuí")
    aba = st.radio("Menu:", ["📋 Cliente: Abrir Chamado", "🔐 Técnico: Painel ADM"])
    st.divider()
    
    # Se a aba for ADM, mostra o campo de senha na lateral
    senha_digitada = ""
    if aba == "🔐 Técnico: Painel ADM":
        st.subheader("Área Restrita")
        senha_digitada = st.text_input("Digite a Senha ADM", type="password")

# --- CONTEÚDO PRINCIPAL ---

if aba == "📋 Cliente: Abrir Chamado":
    st.header("Portal de Atendimento")
    with st.form("form_cliente"):
        nome = st.text_input("Nome")
        zap = st.text_input("WhatsApp")
        problema = st.text_area("O que aconteceu?")
        enviar = st.form_submit_button("Gerar Chamado")
        
        if enviar and nome and zap:
            protocolo = datetime.datetime.now().strftime("%H%M%S")
            st.session_state.db_chamados.append({
                "ID": protocolo, "Cliente": nome, "Contato": zap, "Problema": problema, "Data": datetime.datetime.now().strftime("%d/%m %H:%M")
            })
            st.success(f"Protocolo #{protocolo} gerado!")
            # Link Zap
            msg = urllib.parse.quote(f"Novo Chamado: {nome} - Prot: {protocolo}")
            st.markdown(f"[💬 Enviar para WhatsApp](https://wa.me/{WHATSAPP_TECNICO}?text={msg})")

elif aba == "🔐 Técnico: Painel ADM":
    # VERIFICAÇÃO DE SENHA
    if senha_digitada == SENHA_ADMIN_DEFINIDA:
        st.header("📊 Painel de Controle (Logado)")
        if not st.session_state.db_chamados:
            st.info("Nenhum chamado salvo nesta sessão.")
        else:
            st.table(pd.DataFrame(st.session_state.db_chamados))
    elif senha_digitada == "":
        st.warning("Aguardando senha na barra lateral...")
    else:
        st.error("Senha Incorreta!")