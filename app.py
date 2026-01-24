import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí", page_icon="💻", layout="centered", initial_sidebar_state="collapsed")

# Bloco contra erro de tradução
st.markdown("<script>document.documentElement.lang = 'pt-br';</script>", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

# --- MENU LATERAL ---
with st.sidebar:
    st.header("⚙️ ADMIN")
    aba = st.radio("Mudar para:", ["📝 Cliente", "🔒 Técnico"])
    senha = st.text_input("Senha", type="password") if aba == "🔒 Técnico" else ""

# =========================================================
# 🏠 ÁREA DO CLIENTE
# =========================================================
if aba == "📝 Cliente":
    st.markdown("<h1 style='text-align:center; color:#FF6B00;'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    with st.form("chamado", clear_on_submit=True):
        nome = st.text_input("Nome")
        zap = st.text_input("WhatsApp")
        col1, col2 = st.columns(2)
        with col1: tipo = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2: mod = st.text_input("Modelo")
        defet = st.text_area("Defeito")
        sub = st.form_submit_button("GERAR PROTOCOLO")

    if sub:
        if nome and zap and defet:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            payload = {"data": [{"Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": nome, "WhatsApp": zap, "Equipamento": f"{tipo} - {mod}", "Defeito": defet}]}
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    st.success(f"Protocolo {prot} salvo!")
                    txt = f"*NOVO CHAMADO*\n*Prot:* {prot}\n*Cliente:* {nome}\n*Defeito:* {defet}"
                    link = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(txt)}"
                    st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
                else: st.error(f"Erro ao salvar: {res.status_code}")
            except: st.error("Erro de conexão com o banco de dados.")

# =========================================================
# 📊 ÁREA TÉCNICA (ADMIN)
# =========================================================
elif aba == "🔒 Técnico":
    if senha == SENHA_ADMIN:
        st.subheader("📋 Chamados na Planilha")
        if st.button("🔄 RECARREGAR DADOS"): st.rerun()

        try:
            # O truque do 'timestamp' força o SheetDB a buscar dados novos agora
            url_refresh = f"{API_URL}?_={datetime.datetime.now().timestamp()}"
            r = requests.get(url_refresh, timeout=15)
            
            if r.status_code == 200:
                df = pd.DataFrame(r.json())
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    st.divider()
                    prot_del = st.selectbox("Concluir Protocolo:", df["Protocolo"].tolist())
                    if st.button("❌ APAGAR DEFINITIVAMENTE"):
                        if requests.delete(f"{API_URL}/Protocolo/{prot_del}").status_code in [200, 204]:
                            st.success("Excluído!"); st.rerun()
                else: st.info("Nenhum chamado encontrado na planilha.")
            else: st.error(f"O SheetDB respondeu com erro: {r.status_code}")
        except Exception as e:
            st.error(f"Não foi possível conectar: {e}")
    elif senha != "": st.error("Senha incorreta.")