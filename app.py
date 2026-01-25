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

# --- 2. ESTILO CSS (Ocultando elementos nativos do Streamlit) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1, h2 { color: #FF6B00 !important; text-align: center; }
    div.stButton > button { background-color: #ffffff !important; color: #000000 !important; font-weight: bold; width: 100%; height: 50px; }
    
    #MainMenu {visibility: hidden;} /* Esconde o menu de 3 risquinhos do Streamlit */
    footer {visibility: hidden;}    /* Esconde o rodapé */
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
CHAVE_MESTRE = "admhelp" # Digite isso no campo secreto para ver o menu técnico
MEU_WHATSAPP = "5515991172115"

# --- 4. MENU LATERAL INTELIGENTE ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 20px;'>INFOHELP</h1>", unsafe_allow_html=True)
    
    # Campo "invisível" para o técnico liberar o menu
    acesso = st.text_input("Acesso Interno", type="password", help="Apenas para funcionários")
    
    if acesso == CHAVE_MESTRE:
        st.success("Modo Técnico Ativo")
        aba = st.radio("Navegação:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    else:
        aba = "📝 Abrir Chamado" # Força o cliente a ficar aqui
        if acesso != "":
            st.error("Chave incorreta")

# --- 5. PÁGINA: ABRIR CHAMADO (O QUE O CLIENTE VÊ) ---
if aba == "📝 Abrir Chamado":
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        col1, col2 = st.columns(2)
        with col1: doc = st.text_input("CPF / CNPJ")
        with col2: zap_cli = st.text_input("WhatsApp do Cliente")
        end = st.text_input("Endereço Completo")
        equi = st.text_input("Aparelho / Modelo")
        defe = st.text_area("Descrição do Defeito")
        
        if st.form_submit_button("GERAR PROTOCOLO"):
            if nome and zap_cli and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                payload = {"data": [{
                    "Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                    "Cliente": nome, "Documento": doc, "WhatsApp": zap_cli, 
                    "Endereco": end, "Equipamento": equi, "Defeito": defe
                }]}
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code in [200, 201]:
                        st.success(f"OS #{prot} Gerada!")
                        texto = (f"*💻 INFOHELP - NOVA OS*\n\n*Protocolo:* {prot}\n*Cliente:* {nome}\n*WhatsApp:* {zap_cli}\n*Endereço:* {end}\n*Equipamento:* {equi}\n*Defeito:* {defe}")
                        st.markdown(f'<a href="https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto)}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
                except: st.error("Erro de conexão.")

# --- 6. PÁGINA: ÁREA TÉCNICA (SÓ APARECE COM A CHAVE MESTRE) ---
elif aba == "🔒 Área Técnica" and acesso == CHAVE_MESTRE:
    # Segunda camada de segurança: a senha que você já usava
    senha_final = st.text_input("Senha de Gerência", type="password")
    if senha_final == SENHA_ADMIN:
        st.markdown("<h1>Painel de Controle</h1>", unsafe_allow_html=True)
        try:
            r = requests.get(f"{API_URL}?_={time.time()}")
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                st.dataframe(df, use_container_width=True)
                st.divider()
                excluir = st.selectbox("Protocolo para remover:", df["Protocolo"].tolist())
                if st.button("EXCLUIR REGISTRO"):
                    requests.delete(f"{API_URL}/Protocolo/{excluir}")
                    st.rerun()
        except: st.error("Erro ao carregar dados.")