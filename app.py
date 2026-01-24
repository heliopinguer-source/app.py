import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re
import requests
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí | Suporte", page_icon="💻")

# =========================================================
# 🔐 CONFIGURAÇÕES (AJUSTE AQUI)
# =========================================================
SENHA_ADMIN = "infohelp2026"
NUMERO_WHATSAPP = "5515999999999" # Seu número com DDD
SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

# COLE AQUI O LINK QUE VOCÊ COPIOU DO APPS SCRIPT DO GOOGLE
URL_GOOGLE_SCRIPT = "COLE_AQUI_O_LINK_DO_WEB_APP" 

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 15px !important; padding: 30px !important; border: 1px solid #3d4450 !important; }
    .stForm label p { color: #FF6B00 !important; font-weight: bold !important; font-size: 19px !important; }
    div.stButton > button { 
        background-color: #FF6B00 !important; color: white !important; width: 100% !important; 
        border-radius: 10px !important; font-weight: bold !important; font-size: 22px !important; 
        padding: 20px !important; border: none !important; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.markdown("<div style='text-align:center'><h1 style='color:#FF6B00;'>INFOHELP TATUÍ</h1><p style='color:white;'>Portal de Suporte Online</p></div>", unsafe_allow_html=True)

with st.form("form_suporte"):
    nome = st.text_input("Nome Completo")
    zap_cli = st.text_input("WhatsApp (com DDD)")
    col1, col2 = st.columns(2)
    with col1:
        equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
    with col2:
        modelo = st.text_input("Marca/Modelo")
    defeito = st.text_area("O que está acontecendo?")
    
    submit = st.form_submit_button("GERAR PROTOCOLO")

if submit:
    if nome and zap_cli and defeito:
        protocolo = f"IH-{datetime.datetime.now().strftime('%d%H%M%S')}"
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Dados para enviar ao Google
        dados = {
            "Protocolo": protocolo,
            "Data": data_atual,
            "Cliente": nome,
            "WhatsApp": zap_cli,
            "Equipamento": f"{equip} {modelo}",
            "Defeito": defeito
        }

        try:
            # Envia para a Planilha via Web App
            requests.post(URL_GOOGLE_SCRIPT, data=json.dumps(dados))
            
            st.success(f"Protocolo #{protocolo} gerado com sucesso!")
            
            # Link do WhatsApp
            msg = f"*NOVO CHAMADO INFOHELP*\n*Protocolo:* {protocolo}\n*Cliente:* {nome}\n*Defeito:* {defeito}"
            link_zap = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg)}"
            
            st.markdown(f"""
                <a href="{link_zap}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.2em;">
                        💬 ENVIAR PARA O WHATSAPP DA INFOHELP
                    </div>
                </a>
            """, unsafe_allow_html=True)
        except:
            st.error("Erro ao salvar dados. Verifique a URL do Google Script.")
    else:
        st.warning("Preencha todos os campos!")