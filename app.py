import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="InfoHelp Tatuí", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 15px !important; padding: 25px !important; border: 1px solid #3d4450 !important; }
    .stForm label p { color: #FF6B00 !important; font-weight: bold; font-size: 18px; }
    div.stButton > button { background-color: #FF6B00 !important; color: white !important; width: 100% !important; border-radius: 10px !important; font-weight: bold; height: 60px !important; border: none !important; }
    .header-text { text-align: center; color: #FF6B00; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>PAINEL INFOHELP</h2>", unsafe_allow_html=True)
    aba = st.radio("Navegação:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha_digitada = st.text_input("Senha Admin", type="password") if aba == "🔒 Área Técnica" else ""

# --- CLIENTE ---
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap_cliente = st.text_input("WhatsApp com DDD")
        col1, col2 = st.columns(2)
        with col1: tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2: modelo = st.text_input("Marca / Modelo")
        defeito = st.text_area("Descrição do Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            payload = {"data": [{"Protocolo": protocolo, "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": nome, "WhatsApp": zap_cliente, "Equipamento": f"{tipo_equip} - {modelo}", "Defeito": defeito}]}
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    st.success(f"Protocolo #{protocolo} gerado!")
                    msg = f"*💻 NOVO CHAMADO*\n\n*🎫 Protocolo:* {protocolo}\n*👤 Cliente:* {nome}\n*🛠️ Defeito:* {defeito}"
                    st.markdown(f'<a href="https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(msg)}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
                else: st.error(f"Erro ao salvar: Ative o POST no SheetDB")
            except: st.error("Erro de conexão.")

# --- TÉCNICO ---
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Chamados Ativos</h2>", unsafe_allow_html=True)
        try:
            resp = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    st.divider()
                    prot_excluir = st.selectbox("Finalizar Chamado:", df["Protocolo"].tolist())
                    if st.button("❌ APAGAR"):
                        if requests.delete(f"{API_URL}/Protocolo/{prot_excluir}").status_code in [200, 204]:
                            st.success("Excluído!"); st.rerun()
                else: st.info("Planilha vazia.")
            else: st.error("Erro de Permissão (403). Ative o GET no SheetDB.")
        except: st.error("Falha ao conectar.")