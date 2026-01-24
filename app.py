import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# 1. LIMPEZA DE CACHE PARA GARANTIR ATUALIZAÇÃO
st.cache_data.clear()

st.set_page_config(page_title="InfoHelp Tatuí", layout="wide", initial_sidebar_state="expanded")

# 2. ESTILO VISUAL INFOHELP
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 25px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1, h2 { color: #FF6B00 !important; text-align: center; margin-bottom: 20px; }
    div.stButton > button { background-color: #ffffff !important; color: #000000 !important; font-weight: bold; width: 100%; height: 55px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# CONFIGURAÇÕES
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

# 3. MENU LATERAL
with st.sidebar:
    st.markdown("<h1 style='font-size: 24px;'>MENU</h1>", unsafe_allow_html=True)
    aba = st.radio("Selecione:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha = st.text_input("Senha Admin", type="password") if aba == "🔒 Área Técnica" else ""

# 4. PÁGINA: ABRIR CHAMADO
if aba == "📝 Abrir Chamado":
    st.markdown("<h1>INFOHELP TATUÍ - CADASTRO O.S</h1>", unsafe_allow_html=True)
    with st.form("novo_chamado", clear_on_submit=True):
        nome = st.text_input("Nome Completo / Razão Social")
        
        c1, c2 = st.columns(2)
        with c1: doc = st.text_input("CPF ou CNPJ")
        with c2: zap_cli = st.text_input("WhatsApp do Cliente")
        
        c3, c4 = st.columns(2)
        with c3: email = st.text_input("E-mail")
        with c4: end = st.text_input("Endereço Completo")
        
        c5, c6 = st.columns(2)
        with c5: equi = st.text_input("Equipamento / Modelo")
        with c6: data_fixa = st.text_input("Data de Entrada", datetime.datetime.now().strftime("%d/%m/%Y"), disabled=True)
        
        defe = st.text_area("Descrição Detalhada do Defeito")
        
        if st.form_submit_button("REGISTRAR CHAMADO"):
            if nome and zap_cli and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                payload = {"data": [{
                    "Protocolo": prot, "Data": data_fixa, "Cliente": nome, 
                    "Documento": doc, "WhatsApp": zap_cli, "Email": email, 
                    "Endereco": end, "Equipamento": equi, "Defeito": defe
                }]}
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code in [200, 201]:
                        st.success(f"Ordem de Serviço #{prot} criada!")
                        texto = (f"*💻 INFOHELP - NOVA OS*\n\n"
                                 f"*Protocolo:* {prot}\n"
                                 f"*Cliente:* {nome}\n"
                                 f"*Documento:* {doc}\n"
                                 f"*Equipamento:* {equi}\n"
                                 f"*Defeito:* {defe}")
                        link = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto)}"
                        st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
                    else: st.error("Erro ao gravar. Verifique se as colunas na planilha estão corretas.")
                except: st.error("Erro de conexão com o servidor.")

# 5. PÁGINA: ÁREA TÉCNICA
elif aba == "🔒 Área Técnica":
    if senha == SENHA_ADMIN:
        st.markdown("<h1>Gerenciamento de Chamados</h1>", unsafe_allow_html=True)
        try:
            r = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    st.divider()
                    excluir = st.selectbox("Selecione o Protocolo para Finalizar:", df["Protocolo"].tolist())
                    if st.button("❌ APAGAR REGISTRO"):
                        requests.delete(f"{API_URL}/Protocolo/{excluir}")
                        st.success("Chamado finalizado!"); st.rerun()
                else: st.info("Nenhum chamado pendente.")
            else: st.error("Erro ao ler dados. Verifique o GET no SheetDB.")
        except: st.error("Falha ao carregar a lista.")