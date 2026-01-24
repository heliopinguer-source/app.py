import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# 1. RESET DE CACHE
st.cache_data.clear()

st.set_page_config(page_title="InfoHelp Tatuí", layout="wide", initial_sidebar_state="expanded")

# 2. ESTILO VISUAL (Mantendo o original das suas fotos)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1, h2 { color: #FF6B00 !important; text-align: center; }
    div.stButton > button { background-color: #ffffff !important; color: #000000 !important; font-weight: bold; width: 100%; height: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115" # Seu número configurado

# 3. MENU LATERAL
with st.sidebar:
    st.markdown("<h1>MENU</h1>", unsafe_allow_html=True)
    aba = st.radio("Selecione:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha = st.text_input("Senha", type="password") if aba == "🔒 Área Técnica" else ""

# 4. PÁGINA: ABRIR CHAMADO
if aba == "📝 Abrir Chamado":
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        
        col1, col2 = st.columns(2)
        with col1: doc = st.text_input("CPF / CNPJ")
        with col2: zap_cli = st.text_input("WhatsApp do Cliente")
        
        # NOVO CAMPO DE ENDEREÇO
        endereco = st.text_input("Endereço Completo")
        
        equi = st.text_input("Aparelho / Modelo")
        defe = st.text_area("Descrição do Defeito")
        
        if st.form_submit_button("GERAR PROTOCOLO"):
            if nome and zap_cli and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                payload = {"data": [{
                    "Protocolo": prot, 
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                    "Cliente": nome, 
                    "Documento": doc, 
                    "WhatsApp": zap_cli, 
                    "Endereco": endereco, # Enviando para a planilha
                    "Equipamento": equi, 
                    "Defeito": defe
                }]}
                
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code in [200, 201]:
                        st.success(f"OS #{prot} Gerada!")
                        
                        # MENSAGEM ATUALIZADA COM ENDEREÇO E WHATSAPP DO CLIENTE
                        texto = (f"*💻 INFOHELP - NOVA OS*\n\n"
                                 f"*Protocolo:* {prot}\n"
                                 f"*Cliente:* {nome}\n"
                                 f"*Documento:* {doc}\n"
                                 f"*WhatsApp Cliente:* {zap_cli}\n"
                                 f"*Endereço:* {endereco}\n"
                                 f"*Equipamento:* {equi}\n"
                                 f"*Defeito:* {defe}")
                        
                        link = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto)}"
                        st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
                    else:
                        st.error("Erro ao salvar. Verifique se a coluna 'Endereco' existe na planilha.")
                except:
                    st.error("Falha de conexão.")

# 5. PÁGINA: ÁREA TÉCNICA
elif aba == "🔒 Área Técnica":
    if senha == SENHA_ADMIN:
        st.markdown("<h1>Gerenciar Chamados</h1>", unsafe_allow_html=True)
        try:
            r = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            if r.status_code == 200:
                dados = r.json()
                if dados:
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
                    st.divider()
                    excluir = st.selectbox("Selecione o Protocolo para Excluir:", df["Protocolo"].tolist())
                    if st.button("EXCLUIR REGISTRO"):
                        requests.delete(f"{API_URL}/Protocolo/{excluir}")
                        st.rerun()
                else:
                    st.info("Nenhum chamado pendente.")
        except:
            st.error("Erro ao carregar dados.")