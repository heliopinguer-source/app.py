import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA (Ajusta título e ícone na aba do navegador) ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte Online",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 🔐 CONFIGURAÇÕES PRINCIPAIS
# =========================================================
SENHA_ADMIN = "infohelp2026"
NUMERO_WHATSAPP = "5515999999999"  # <--- COLOQUE SEU NÚMERO AQUI
SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

# --- ESTILO CSS CUSTOMIZADO (Design Dark & Orange) ---
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp { background-color: #0E1117; }
    
    /* Container do Formulário */
    .stForm {
        background-color: #1c1f26 !important;
        border-radius: 15px !important;
        padding: 30px !important;
        border: 1px solid #3d4450 !important;
    }

    /* Rótulos dos campos em Laranja Vibrante */
    .stForm label p {
        color: #FF6B00 !important;
        font-weight: bold !important;
        font-size: 19px !important;
        margin-bottom: 5px !important;
    }

    /* Estilização do Botão Principal */
    div.stButton > button {
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
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #E65A00 !important;
        box-shadow: 0px 5px 15px rgba(255, 107, 0, 0.4);
    }

    /* Centralização do Cabeçalho */
    .header-container { text-align: center; padding: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro ao conectar com a Planilha. Verifique as 'Secrets' no Streamlit Cloud.")

# --- BARRA LATERAL (Acesso Técnico) ---
with st.sidebar:
    st.title("⚙️ Administração")
    aba = st.radio("Selecione a visualização:", ["Portal do Cliente", "Painel Gestor"])
    senha_digitada = st.text_input("Senha de Acesso", type="password") if aba == "Painel Gestor" else ""

# =========================================================
# 🏠 INTERFACE DO CLIENTE
# =========================================================
if aba == "Portal do Cliente":
    st.markdown("""
        <div class="header-container">
            <h1 style='color: #FF6B00; font-size: 3.2em; margin-bottom: 0;'>INFOHELP TATUÍ</h1>
            <p style='color: #ffffff; font-size: 1.1em; opacity: 0.8;'>Soluções Inteligentes em Tecnologia</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_chamado"):
        st.markdown("<h3 style='color:white; text-align:center;'>Abrir Novo Chamado</h3>", unsafe_allow_html=True)
        
        nome = st.text_input("Nome Completo")
        zap_cli = st.text_input("Seu WhatsApp (com DDD)")
        
        col1, col2 = st.columns(2)
        with col1:
            equip = st.selectbox("Tipo de Aparelho", ["Notebook", "PC Gamer", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca / Modelo")
            
        defeito = st.text_area("Descrição do Defeito")
        
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cli and defeito:
            # Gerar Protocolo único baseado na hora
            protocolo = f"IH-{datetime.datetime.now().strftime('%d%H%M%S')}"
            data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            try:
                # 1. Ler dados existentes
                df_existente = conn.read(ttl=0)
                
                # 2. Criar nova linha
                novo_dado = pd.DataFrame([{
                    "Protocolo": protocolo,
                    "Data": data_hora,
                    "Cliente": nome,
                    "WhatsApp": zap_cli,
                    "Equipamento": f"{equip} {modelo}",
                    "Defeito": defeito
                }])
                
                # 3. Concatenar e Atualizar Planilha
                df_final = pd.concat([df_existente, novo_dado], ignore_index=True)
                conn.update(data=df_final)

                # Sucesso Visual
                st.balloons()
                st.success(f"Protocolo #{protocolo} gerado e salvo com sucesso!")

                # Gerar link do WhatsApp para o cliente enviar
                texto_zap = f"*NOVO CHAMADO - INFOHELP*\n\n*Protocolo:* {protocolo}\n*Cliente:* {nome}\n*Equipamento:* {equip} {modelo}\n*Defeito:* {defeito}"
                link_whatsapp = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"

                st.markdown(f"""
                    <a href="{link_whatsapp}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#25D366; color:white; padding:20px; border-radius:12px; text-align:center; font-weight:bold; font-size:1.3em; margin-top:15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                            💬 CLIQUE AQUI PARA ENVIAR NO WHATSAPP
                        </div>
                    </a>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
        else:
            st.warning("⚠️ Por favor, preencha todos os campos para continuar.")

# =========================================================
# 📊 INTERFACE DO TÉCNICO (PAINEL GESTOR)
# =========================================================
elif aba == "Painel Gestor":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color: #FF6B00;'>Histórico de Atendimentos</h2>", unsafe_allow_html=True)
        
        try:
            df_view = conn.read(ttl=0)
            if not df_view.empty:
                st.dataframe(df_view.sort_index(ascending=False), use_container_width=True)
                
                # Botão de Exportação para Excel
                csv = df_view.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Planilha em CSV", csv, "backup_infohelp.csv", "text/csv")
            else:
                st.info("Nenhum chamado encontrado na planilha.")
        except:
            st.error("Não foi possível carregar os dados da Planilha Google.")
            
    elif senha_digitada != "":
        st.error("Senha incorreta. Acesso negado.")