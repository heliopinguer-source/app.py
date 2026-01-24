import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="InfoHelp Tatuí", layout="centered")

# IMPORTANTE: Substitua o ID abaixo pelo NOVO que você gerou agora
API_URL = "https://sheetdb.io/api/v1/COLE_SEU_NOVO_ID_AQUI" 
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

# --- ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div.stButton > button { background-color: #FF6B00 !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- MENU ---
with st.sidebar:
    aba = st.radio("Menu:", ["📝 Cliente", "🔒 Técnico"])
    senha = st.text_input("Senha", type="password") if aba == "🔒 Técnico" else ""

# --- ÁREA CLIENTE ---
if aba == "📝 Cliente":
    st.header("INFOHELP TATUÍ")
    with st.form("chamado"):
        nome = st.text_input("Nome")
        zap = st.text_input("WhatsApp")
        defeito = st.text_area("Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap and defeito:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            payload = {"data": [{"Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": nome, "WhatsApp": zap, "Defeito": defeito}]}
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    st.success(f"Salvo! Prot: {prot}")
                    msg = f"Novo Chamado: {prot}\nCliente: {nome}\nDefeito: {defeito}"
                    st.markdown(f'<a href="https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(msg)}" target="_blank">ENVIAR WHATSAPP</a>', unsafe_allow_html=True)
                else: st.error(f"Erro {res.status_code}: {res.text}")
            except: st.error("Erro de conexão.")

# --- ÁREA TÉCNICA ---
elif aba == "🔒 Técnico":
    if senha == SENHA_ADMIN:
        st.subheader("Lista de Chamados")
        try:
            # Força o carregamento ignorando cache
            r = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                if not df.empty:
                    st.dataframe(df)
                    st.divider()
                    prot_del = st.selectbox("Excluir Protocolo:", df["Protocolo"].tolist())
                    if st.button("EXCLUIR"):
                        if requests.delete(f"{API_URL}/Protocolo/{prot_del}").status_code in [200, 204]:
                            st.success("Excluído!"); st.rerun()
                else: st.info("Planilha vazia.")
            else: st.error(f"Erro {r.status_code}")
        except: st.error("Erro ao conectar.")
    elif senha: st.error("Senha incorreta.")