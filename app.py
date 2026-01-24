import streamlit as st
import datetime
import urllib.parse
import re
import requests
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí | Suporte", page_icon="💻", layout="centered")

# Bloqueio contra erro de tradução (evita o erro 'removeChild')
st.markdown("<script>document.documentElement.lang = 'pt-br';</script>", unsafe_allow_html=True)

# =========================================================
# ⚙️ CONFIGURAÇÕES (JÁ COM SEUS DADOS)
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515996444208" 

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 15px !important; padding: 25px !important; border: 1px solid #3d4450 !important; }
    .stForm label p { color: #FF6B00 !important; font-weight: bold !important; font-size: 18px !important; }
    div.stButton > button { background-color: #FF6B00 !important; color: white !important; width: 100% !important; border-radius: 10px !important; font-weight: bold !important; font-size: 20px !important; height: 60px !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>INFOHELP</h2>", unsafe_allow_html=True)
    aba = st.radio("Ir para:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha_digitada = st.text_input("Senha Admin", type="password") if aba == "🔒 Área Técnica" else ""

# =========================================================
# 🏠 ÁREA DO CLIENTE
# =========================================================
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 style='text-align:center; color:#FF6B00;'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)

    with st.form("chamado_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap = st.text_input("WhatsApp (DDD + Número)")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca e Modelo")
            
        defeito = st.text_area("Descrição do Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            equip_completo = f"{tipo_equip} - {modelo}"
            
            # Envio via SheetDB (resolve o erro da imagem 1)
            payload = {
                "data": [{
                    "Protocolo": protocolo,
                    "Data": data_atual,
                    "Cliente": nome,
                    "WhatsApp": zap,
                    "Equipamento": equip_completo,
                    "Defeito": defeito
                }]
            }

            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code in [200, 201]:
                    st.success(f"Protocolo #{protocolo} gerado com sucesso!")
                    
                    # Mensagem WhatsApp (imagem 6)
                    msg = f"*NOVO CHAMADO INFOHELP*\n*Protocolo:* {protocolo}\n*Cliente:* {nome}\n*Defeito:* {defeito}"
                    link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA O WHATSAPP</div></a>', unsafe_allow_html=True)
                else:
                    st.error("Erro técnico. Verifique se o SheetDB está ativo.")
            except:
                st.error("Falha de conexão.")
        else:
            st.warning("⚠️ Preencha todos os campos!")

# =========================================================
# 📊 ÁREA TÉCNICA (ADMIN)
# =========================================================
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Painel de Chamados</h2>", unsafe_allow_html=True)
        try:
            resp = requests.get(API_URL)
            if resp.status_code == 200:
                df = pd.DataFrame(resp.json())
                if not df.empty:
                    # Exibe a tabela completa
                    st.dataframe(df, use_container_width=True)
                    
                    # Seleção para ler defeitos longos (que a tabela corta)
                    st.divider()
                    st.subheader("Visualizar Detalhes")
                    prot = st.selectbox("Escolha um Protocolo:", df["Protocolo"].tolist())
                    texto = df[df["Protocolo"] == prot]["Defeito"].values[0]
                    st.info(f"**Descrição do Defeito:** {texto}")
                else:
                    st.info("Nenhum dado encontrado.")
            else:
                st.error("Erro ao carregar planilha.")
        except Exception as e:
            st.error(f"Erro: {e}")
    elif senha_digitada != "":
        st.error("Senha incorreta!")