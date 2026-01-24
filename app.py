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
    .stForm { 
        background-color: #1c1f26 !important; 
        border-radius: 15px !important; 
        padding: 25px !important; 
        border: 1px solid #3d4450 !important; 
    }
    .stForm label p { color: #FF6B00 !important; font-weight: bold; font-size: 18px; }
    div.stButton > button { 
        background-color: #FF6B00 !important; 
        color: white !important; 
        width: 100% !important; 
        border-radius: 10px !important; 
        font-weight: bold !important; 
        font-size: 20px !important;
        height: 60px !important; 
        border: none !important; 
    }
    .header-text { text-align: center; color: #FF6B00; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115"

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>MENU INFOHELP</h2>", unsafe_allow_html=True)
    aba = st.radio("Navegação:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha_digitada = st.text_input("Senha Admin", type="password") if aba == "🔒 Área Técnica" else ""

# =========================================================
# 📝 PÁGINA: CLIENTE
# =========================================================
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap_cliente = st.text_input("WhatsApp (DDD + Número)")
        col1, col2 = st.columns(2)
        with col1:
            tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca / Modelo")
        defeito = st.text_area("Descreva o Problema")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            payload = {
                "data": [{
                    "Protocolo": protocolo,
                    "Data": data_atual,
                    "Cliente": nome,
                    "WhatsApp": zap_cliente,
                    "Equipamento": f"{tipo_equip} - {modelo}",
                    "Defeito": defeito
                }]
            }
            
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    st.success(f"Protocolo #{protocolo} gerado com sucesso!")
                    msg = f"*💻 NOVO CHAMADO - INFOHELP*\n\n*🎫 Protocolo:* {protocolo}\n*👤 Cliente:* {nome}\n*🛠️ Defeito:* {defeito}"
                    link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA O WHATSAPP</div></a>', unsafe_allow_html=True)
                else:
                    st.error(f"Erro {res.status_code}: Verifique se o 'POST' está ativo no SheetDB.")
            except:
                st.error("Erro de conexão. Tente novamente.")
        else:
            st.warning("⚠️ Preencha todos os campos!")

# =========================================================
# 🔒 PÁGINA: TÉCNICO
# =========================================================
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Chamados Ativos</h2>", unsafe_allow_html=True)
        
        try:
            # Força o carregamento ignorando o cache
            resp = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            
            if resp.status_code == 200:
                dados = resp.json()
                if dados:
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
                    
                    st.divider()
                    col_sel, col_btn = st.columns([2, 1])
                    with col_sel:
                        prot_excluir = st.selectbox("Selecione para finalizar:", df["Protocolo"].tolist())
                    with col_btn:
                        st.write(" ")
                        if st.button("❌ EXCLUIR"):
                            if requests.delete(f"{API_URL}/Protocolo/{prot_excluir}").status_code in [200, 204]:
                                st.success("Chamado concluído!"); st.rerun()
                            else:
                                st.error("Erro ao apagar. Verifique a permissão 'DELETE'.")
                else:
                    st.info("A planilha está vazia.")
            else:
                st.error(f"Erro {resp.status_code}: A permissão de leitura (GET) está desativada no SheetDB.")
        except:
            st.error("Falha ao conectar com o banco de dados.")
    elif senha_digitada != "":
        st.error("Senha Incorreta!")