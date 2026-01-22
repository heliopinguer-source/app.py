import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí", page_icon="💻", layout="wide")

# =========================================================
# 🔐 CONFIGURAÇÃO DE SEGURANÇA (ALTERE AQUI)
# =========================================================
SENHA_MESTRE = "infohelp2026"  # <--- COLOQUE SUA SENHA AQUI
SEU_WHATSAPP = "5515999999999" # Seu número com DDD (Ex: 5515...)
# =========================================================

# Inicializa o banco de dados na memória do navegador
if "dados" not in st.session_state:
    st.session_state.dados = []

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🛠️ InfoHelp Tatuí")
    st.write("---")
    # O menu de navegação
    escolha = st.radio("Selecione:", ["Página do Cliente", "Área do Técnico (ADM)"])
    
    # Campo de senha que só aparece se escolher "Área do Técnico"
    senha_digitada = ""
    if escolha == "Área do Técnico (ADM)":
        st.write("---")
        st.subheader("Login Requerido")
        senha_digitada = st.text_input("Digite a Senha Administrador", type="password")

# --- LÓGICA DAS PÁGINAS ---

if escolha == "Página do Cliente":
    st.header("📋 Abertura de Chamado Técnico")
    st.info("Preencha os dados para que possamos analisar seu equipamento.")
    
    with st.form("form_cliente"):
        nome = st.text_input("Nome Completo")
        contato = st.text_input("Seu WhatsApp")
        equip = st.selectbox("Aparelho", ["Notebook", "PC Gamer", "Monitor", "Outro"])
        problema = st.text_area("O que está acontecendo?")
        
        btn = st.form_submit_button("Gerar Protocolo")
        
        if btn:
            if nome and contato and problema:
                protocolo = datetime.datetime.now().strftime("%H%M%S")
                # Salva no banco de dados
                st.session_state.dados.append({
                    "Prot": protocolo, "Cliente": nome, "Zap": contato, 
                    "Equip": equip, "Defeito": problema, 
                    "Hora": datetime.datetime.now().strftime("%H:%M")
                })
                
                st.success(f"✅ Chamado #{protocolo} aberto!")
                
                # Botão do WhatsApp
                msg = f"Olá InfoHelp! Novo chamado #{protocolo} - Cliente: {nome} ({equip})"
                link = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;text-align:center;border-radius:5px;font-weight:bold;">ENVIAR PARA O TÉCNICO VIA WHATSAPP</div></a>', unsafe_allow_html=True)
            else:
                st.error("Preencha todos os campos!")

elif escolha == "Área do Técnico (ADM)":
    # 🛡️ AQUI ACONTECE A VERIFICAÇÃO DA SENHA
    if senha_digitada == SENHA_MESTRE:
        st.header("📊 Painel de Controle Técnico")
        st.success("Acesso Autorizado!")
        
        if not st.session_state.dados:
            st.write("Nenhum chamado pendente.")
        else:
            df = pd.DataFrame(st.session_state.dados)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Limpar Todos os Chamados"):
                st.session_state.dados = []
                st.rerun()
    
    elif senha_digitada == "":
        st.warning("⚠️ Por favor, digite a senha na barra lateral esquerda para acessar os dados.")
    else:
        st.error("❌ Senha incorreta! O acesso aos dados dos clientes está bloqueado.")