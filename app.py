import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- ESTILO INFOHELP ---
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

# --- NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>MENU</h2>", unsafe_allow_html=True)
    aba = st.radio("Ir para:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha_digitada = st.text_input("Senha Admin", type="password") if aba == "🔒 Área Técnica" else ""

# --- PÁGINA CLIENTE ---
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap = st.text_input("WhatsApp")
        equi = st.text_input("Aparelho / Modelo")
        defe = st.text_area("Descrição do Defeito")
        if st.form_submit_button("GERAR PROTOCOLO"):
            if nome and zap and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                payload = {"data": [{"Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y"), "Cliente": nome, "WhatsApp": zap, "Equipamento": equi, "Defeito": defe}]}
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    st.success(f"Protocolo {prot} criado!")
                    msg = urllib.parse.quote(f"*NOVO CHAMADO*\n*Prot:* {prot}\n*Cliente:* {nome}\n*Defeito:* {defe}")
                    st.markdown(f'<a href="https://wa.me/{MEU_WHATSAPP}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
                else: st.error("Erro ao salvar: Verifique permissão POST no SheetDB.")

# --- PÁGINA TÉCNICO ---
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Chamados Ativos</h2>", unsafe_allow_html=True)
        try:
            # Força a leitura atualizada
            r = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            if r.status_code == 200:
                dados = r.json()
                if dados:
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
                    st.divider()
                    excluir = st.selectbox("Escolha um chamado para finalizar:", df["Protocolo"].tolist())
                    if st.button("❌ EXCLUIR REGISTRO"):
                        if requests.delete(f"{API_URL}/Protocolo/{excluir}").status_code in [200, 204]:
                            st.success("Removido!"); st.rerun()
                else: st.info("Planilha vazia.")
            else: st.error(f"Erro {r.status_code}: Ative o GET no SheetDB.")
        except: st.error("Erro de conexão.")
    elif senha_digitada: st.error("Senha Incorreta!")