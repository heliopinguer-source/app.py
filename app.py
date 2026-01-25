import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA (SIDEBAR BLOQUEADA) ---
st.set_page_config(
    page_title="InfoHelp Tatuí", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILO CSS (IGUAL AO SEU PRINT) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1 { color: #FF6B00 !important; text-align: center; font-size: 32px !important; }
    
    /* ESCONDE TUDO DO MENU LATERAL PARA O CLIENTE */
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botão Branco de Gerar Protocolo */
    div.stButton > button { background-color: #ffffff !important; color: #000000 !important; font-weight: bold; width: 100%; height: 50px; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

if 'modo' not in st.session_state:
    st.session_state.modo = 'cliente'

# --- 4. TELA DO CLIENTE ---
if st.session_state.modo == 'cliente':
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        
        c1, c2 = st.columns(2)
        with c1: doc = st.text_input("CPF / CNPJ")
        with c2: zap_cli = st.text_input("WhatsApp do Cliente")
        
        end = st.text_input("Endereço Completo")
        
        # --- NOVO MENU SUSPENSO DE EQUIPAMENTOS ---
        col_eq1, col_eq2 = st.columns([1, 1])
        with col_eq1:
            tipo_equip = st.selectbox(
                "Tipo de Equipamento", 
                ["Notebook", "Apple", "Desktop", "Monitor", "Placa de Vídeo", "Outro"]
            )
        with col_eq2:
            modelo_detalhe = st.text_input("Marca / Modelo (Ex: Dell G15)")
            
        defe = st.text_area("Descrição do Defeito")
        
        if st.form_submit_button("GERAR PROTOCOLO"):
            if nome and zap_cli and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                equip_final = f"{tipo_equip} - {modelo_detalhe}"
                
                payload = {"data": [{
                    "Protocolo": prot, 
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                    "Cliente": nome, 
                    "Documento": doc, 
                    "WhatsApp": zap_cli, 
                    "Endereco": end, 
                    "Equipamento": equip_final, 
                    "Defeito": defe
                }]}
                
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code in [200, 201]:
                        st.success(f"OS #{prot} Gerada!")
                        texto = (f"*💻 INFOHELP - NOVA OS*\n\n"
                                 f"*Protocolo:* {prot}\n"
                                 f"*Cliente:* {nome}\n"
                                 f"*WhatsApp:* {zap_cli}\n"
                                 f"*Endereço:* {end}\n"
                                 f"*Equipamento:* {equip_final}\n"
                                 f"*Defeito:* {defe}")
                        st.markdown(f'<a href="https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto)}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
                except: st.error("Erro de conexão.")

    # BOTÃO DISCRETO PARA LOGIN ADM (🔧)
    st.write("---")
    col_secret, _ = st.columns([1, 10])
    with col_secret:
        if st.button("🔧"):
            st.session_state.modo = 'login'
            st.rerun()

# --- 5. TELA DE LOGIN ---
elif st.session_state.modo == 'login':
    st.markdown("<h2>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Admin", type="password")
    if st.button("ENTRAR"):
        if senha == SENHA_ADMIN:
            st.session_state.modo = 'admin'
            st.rerun()
        else: st.error("Senha Incorreta")
    if st.button("VOLTAR"):
        st.session_state.modo = 'cliente'
        st.rerun()

# --- 6. ÁREA TÉCNICA (ADMIN) ---
elif st.session_state.modo == 'admin':
    st.markdown("<h2>GERENCIAR CHAMADOS</h2>", unsafe_allow_html=True)
    if st.button("VOLTAR AO INÍCIO"):
        st.session_state.modo = 'cliente'
        st.rerun()
        
    try:
        r = requests.get(f"{API_URL}?_={time.time()}")
        df = pd.DataFrame(r.json())
        st.dataframe(df, use_container_width=True)
        st.divider()
        if not df.empty:
            excluir = st.selectbox("Protocolo para Excluir:", df["Protocolo"].tolist())
            if st.button("APAGAR REGISTRO"):
                requests.delete(f"{API_URL}/Protocolo/{excluir}")
                st.rerun()
    except: st.error("Erro ao carregar dados.")