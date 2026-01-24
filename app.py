import streamlit as st
import datetime
import urllib.parse
import re
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte",
    page_icon="💻",
    layout="centered"
)

# =========================================================
# ⚙️ CONFIGURAÇÕES (JÁ COM SEU LINK DO SHEETDB)
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
MEU_WHATSAPP = "5515999999999" # <-- Coloque o seu número real aqui
# =========================================================

# --- ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { 
        background-color: #1c1f26 !important; 
        border-radius: 15px !important; 
        padding: 25px !important; 
        border: 1px solid #3d4450 !important; 
    }
    .stForm label p { 
        color: #FF6B00 !important; 
        font-weight: bold !important; 
        font-size: 18px !important; 
    }
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

st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)

# --- FORMULÁRIO ---
with st.form("chamado_form", clear_on_submit=True):
    nome = st.text_input("Nome Completo")
    zap = st.text_input("WhatsApp (DDD + Número)")
    equip = st.text_input("Aparelho (Marca e Modelo)")
    defeito = st.text_area("Descrição do Defeito")
    
    submit = st.form_submit_button("GERAR PROTOCOLO")

if submit:
    if nome and zap and defeito:
        # Gerar dados para salvar
        protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Formato exato que o SheetDB espera
        payload = {
            "data": [{
                "Protocolo": protocolo,
                "Data": data_atual,
                "Cliente": nome,
                "WhatsApp": zap,
                "Equipamento": equip,
                "Defeito": defeito
            }]
        }

        try:
            # Envia os dados para o SheetDB
            response = requests.post(API_URL, json=payload)
            
            # 201 ou 200 significa que o Google Sheets aceitou o dado
            if response.status_code in [200, 201]:
                st.success(f"Protocolo #{protocolo} gerado com sucesso!")
                
                # Link WhatsApp para o cliente
                msg = f"*NOVO CHAMADO INFOHELP*\n*Protocolo:* {protocolo}\n*Cliente:* {nome}\n*Equipamento:* {equip}\n*Defeito:* {defeito}"
                link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
                
                st.markdown(f"""
                    <a href="{link_zap}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.1em; margin-top: 10px;">
                            💬 ENVIAR PARA O WHATSAPP
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Erro ao salvar na planilha. Código: {response.status_code}")
        except Exception as e:
            st.error(f"Falha de conexão: {e}")
    else:
        st.warning("⚠️ Por favor, preencha todos os campos obrigatórios.")