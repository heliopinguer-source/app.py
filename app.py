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
    h1, h2 { color: #FF6B00 !important; text-align: center; }
    
    /* ESCONDE SIDEBAR E ELEMENTOS NATIVOS */
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

# --- 4. JANELINHA DE SUCESSO (POP-UP) ---
@st.dialog("PRÓXIMO PASSO OBRIGATÓRIO")
def modal_whatsapp(prot, texto_zap):
    st.markdown(f"### ✅ Protocolo {prot} gerado!")
    st.write("Clique no botão abaixo para nos enviar os dados pelo WhatsApp e confirmar seu atendimento:")
    
    link = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
    
    st.markdown(f'''
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:20px; border-radius:10px; text-align:center; font-weight:bold; font-size:20px; border: 2px solid #ffffff;">
                💬 ENVIAR WHATSAPP AGORA
            </div>
        </a>
    ''', unsafe_allow_html=True)
    st.info("Entraremos em contato o mais rápido possível!")

# --- 5. TELA DO CLIENTE ---
if st.session_state.modo == 'cliente':
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo / Razão Social")
        
        col1, col2 = st.columns(2)
        with col1: doc = st.text_input("CPF / CNPJ")
        with col2: zap_cli = st.text_input("WhatsApp do Cliente")
        
        end = st.text_input("Endereço Completo")
        
        col3, col4 = st.columns(2)
        with col3:
            tipo_equip = st.selectbox("Tipo de Equipamento", ["Notebook", "Apple", "Desktop", "Monitor", "Placa de Vídeo", "Outro"])
        with col4:
            modelo = st.text_input("Marca / Modelo (Ex: Dell G15)")
            
        defe = st.text_area("Descrição do Defeito")
        
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cli and defe:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            equip_final = f"{tipo_equip} - {modelo}"
            
            payload = {"data": [{
                "Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                "Cliente": nome, "Documento": doc, "WhatsApp": zap_cli, 
                "Endereco": end, "Equipamento": equip_final, "Defeito": defe
            }]}
            
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    texto_zap = (f"*💻 INFOHELP - NOVA OS*\n\n*Protocolo:* {prot}\n*Cliente:* {nome}\n*WhatsApp:* {zap_cli}\n*Equipamento:* {equip_final}\n*Defeito:* {defe}")
                    modal_whatsapp(prot, texto_zap)
                else: st.error("Erro ao registrar.")
            except: st.error("Erro de conexão.")
        else: st.warning("⚠️ Preencha Nome, WhatsApp e Defeito.")

    st.write("---")
    if st.button("🔧"):
        st.session_state.modo = 'login'
        st.rerun()

# --- 6. TELA DE LOGIN ---
elif st.session_state.modo == 'login':
    st.markdown("<h2>LOGIN TÉCNICO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    if st.button("ACESSAR"):
        if senha == SENHA_ADMIN:
            st.session_state.modo = 'admin'
            st.rerun()
        else: st.error("Incorreta")
    if st.button("CANCELAR"):
        st.session_state.modo = 'cliente'
        st.rerun()

# --- 7. ÁREA TÉCNICA (COM BOTÃO DE EXCLUIR DE VOLTA) ---
elif st.session_state.modo == 'admin':
    st.markdown("<h2>GERENCIAR CHAMADOS</h2>", unsafe_allow_html=True)
    if st.button("VOLTAR AO FORMULÁRIO"):
        st.session_state.modo = 'cliente'
        st.rerun()
    
    try:
        # Puxa os dados atualizados
        r = requests.get(f"{API_URL}?_={time.time()}")
        if r.status_code == 200:
            dados = r.json()
            if dados:
                df = pd.DataFrame(dados)
                st.dataframe(df, use_container_width=True)
                
                st.divider()
                st.subheader("🗑️ Finalizar Atendimento")
                # Menu suspenso para escolher qual protocolo apagar
                lista_prot = df["Protocolo"].tolist()
                excluir = st.selectbox("Selecione o Protocolo para EXCLUIR:", lista_prot)
                
                if st.button("APAGAR REGISTRO DEFINITIVAMENTE"):
                    # Chamada DELETE para o SheetDB
                    del_res = requests.delete(f"{API_URL}/Protocolo/{excluir}")
                    if del_res.status_code in [200, 204]:
                        st.success(f"Protocolo {excluir} removido!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erro ao excluir do banco de dados.")
            else:
                st.info("Nenhum chamado registrado na planilha.")
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")