import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1 { color: #FF6B00 !important; text-align: center; font-size: 32px !important; }
    
    /* ESCONDE SIDEBAR E SETA */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botão Branco de Gerar Protocolo */
    div.stButton > button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold; 
        width: 100%; 
        height: 50px; 
        border: none; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

if 'modo' not in st.session_state:
    st.session_state.modo = 'cliente'

# --- 4. FUNÇÃO DA JANELINHA (POP-UP) ---
@st.dialog("PRÓXIMO PASSO OBRIGATÓRIO")
def modal_whatsapp(prot, texto_zap):
    st.markdown(f"### ✅ Protocolo {prot} gerado!")
    st.write("Para concluir seu atendimento, você precisa enviar os dados para nosso WhatsApp abaixo:")
    
    link = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
    
    st.markdown(f'''
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:20px; border-radius:10px; text-align:center; font-weight:bold; font-size:20px; border: 2px solid #ffffff;">
                💬 CLIQUE AQUI PARA ENVIAR
            </div>
        </a>
    ''', unsafe_allow_html=True)
    st.warning("Entraremos em contato o mais rápido possível após o envio!")

# --- 5. TELA DO CLIENTE ---
if st.session_state.modo == 'cliente':
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        c1, c2 = st.columns(2)
        with c1: doc = st.text_input("CPF / CNPJ")
        with c2: zap_cli = st.text_input("WhatsApp do Cliente")
        end = st.text_input("Endereço Completo")
        
        col_eq1, col_eq2 = st.columns([1, 1])
        with col_eq1:
            tipo_equip = st.selectbox("Tipo", ["Notebook", "Apple", "Desktop", "Monitor", "Placa de Vídeo", "Outro"])
        with col_eq2:
            modelo = st.text_input("Marca / Modelo")
            
        defe = st.text_area("Descrição do Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cli and defe:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            payload = {"data": [{
                "Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                "Cliente": nome, "Documento": doc, "WhatsApp": zap_cli, 
                "Endereco": end, "Equipamento": f"{tipo_equip} - {modelo}", "Defeito": defe
            }]}
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    texto_zap = (f"*💻 INFOHELP - NOVA OS*\n\n*Protocolo:* {prot}\n*Cliente:* {nome}\n*Equipamento:* {tipo_equip} {modelo}\n*Defeito:* {defe}")
                    # ABRE A JANELINHA
                    modal_whatsapp(prot, texto_zap)
            except: st.error("Erro de conexão.")
        else:
            st.warning("Preencha todos os campos!")

    # ACESSO ADM DISCRETO
    st.write("---")
    if st.button("🔧"):
        st.session_state.modo = 'login'
        st.rerun()

# --- 6. TELA DE LOGIN E ADMIN ---
elif st.session_state.modo == 'login':
    senha = st.text_input("Senha", type="password")
    if st.button("ENTRAR"):
        if senha == SENHA_ADMIN:
            st.session_state.modo = 'admin'
            st.rerun()
elif st.session_state.modo == 'admin':
    if st.button("VOLTAR"):
        st.session_state.modo = 'cliente'
        st.rerun()
    r = requests.get(f"{API_URL}?_={time.time()}")
    st.dataframe(pd.DataFrame(r.json()), use_container_width=True)