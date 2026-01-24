import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. TRUQUE CSS PARA OCULTAR O MENU LATERAL ---
st.markdown("""
    <style>
    /* Esconde o botão de abrir a barra lateral (setinha) */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Estilos Gerais */
    .stApp { background-color: #0E1117; }
    .stForm { 
        background-color: #1c1f26 !important; 
        border-radius: 15px !important; 
        padding: 25px !important; 
        border: 1px solid #3d4450 !important; 
    }
    .stForm label p { 
        color: #FF6B00 !important; 
        font-weight: bold !important; 
        font-size: 18px !important; 
    }
    div.stButton > button { 
        background-color: #FF6B00 !important; 
        color: white !important; 
        width: 100% !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        font-size: 20px !important; 
        height: 60px !important; 
        border: none !important; 
    }
    .header-text { text-align: center; color: #FF6B00; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ⚙️ 3. CONFIGURAÇÕES
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115" 

# --- 4. SISTEMA DE LOGIN SIMPLES (SEM MENU LATERAL) ---
# Como o menu está oculto, criei um seletor discreto no final da página 
# que só você saberá usar para acessar a Área Técnica.

st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)

# Criamos abas transparentes ou um seletor no topo
aba = st.selectbox("Navegação", ["📝 Abrir Chamado", "🔒 Área Técnica"], label_visibility="collapsed")

# =========================================================
# 🏠 5. PÁGINA: ABRIR CHAMADO (CLIENTE)
# =========================================================
if aba == "📝 Abrir Chamado":
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap_cliente = st.text_input("WhatsApp (com DDD)")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca / Modelo")
            
        defeito = st.text_area("O que está acontecendo?")
        
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            equip_completo = f"{tipo_equip} - {modelo}"
            
            payload = {"data": [{"Protocolo": protocolo, "Data": data_atual, "Cliente": nome, "WhatsApp": zap_cliente, "Equipamento": equip_completo, "Defeito": defeito}]}

            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code in [200, 201]:
                    st.success(f"Protocolo #{protocolo} gerado!")
                    texto_zap = f"*💻 NOVO CHAMADO - INFOHELP*\n\n*🎫 Protocolo:* {protocolo}\n*👤 Cliente:* {nome}\n*⚙️ Equipamento:* {equip_completo}\n*🛠️ Defeito:* {defeito}"
                    link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
                    st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
            except:
                st.error("Erro ao salvar.")
        else:
            st.warning("Preencha tudo!")

# =========================================================
# 📊 6. PÁGINA: ÁREA TÉCNICA (ADMIN)
# =========================================================
elif aba == "🔒 Área Técnica":
    senha = st.text_input("Senha de Acesso", type="password")
    if senha == SENHA_ADMIN:
        try:
            resp = requests.get(API_URL)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                st.dataframe(df, use_container_width=True)
                st.divider()
                selecao = st.selectbox("Ver defeito do protocolo:", df["Protocolo"].tolist())
                st.info(f"**Relato:** {df[df['Protocolo'] == selecao]['Defeito'].values[0]}")
        except:
            st.error("Erro ao carregar dados.")
    elif senha != "":
        st.error("Senha Incorreta!")