import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="InfoHelp Tatuí", page_icon="💻", layout="wide")

# =========================================================
# 🔐 CONFIGURAÇÃO (Mude apenas o que está entre as aspas)
# =========================================================
SENHA_MESTRE = "infohelp2026"  
# ABAIXO: Coloque seu número. Ex: "5515999999999"
NUMERO_BRUTO = "5515991172115" 
# =========================================================

# Limpeza automática do número (remove espaços, parênteses e traços)
SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_BRUTO)

if "dados" not in st.session_state:
    st.session_state.dados = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🛠️ InfoHelp Tatuí")
    st.write("---")
    escolha = st.radio("Selecione:", ["Página do Cliente", "Área do Técnico (ADM)"])
    
    senha_digitada = ""
    if escolha == "Área do Técnico (ADM)":
        st.write("---")
        st.subheader("Acesso Restrito")
        senha_digitada = st.text_input("Senha Admin", type="password")

# --- LÓGICA ---
if escolha == "Página do Cliente":
    st.header("📋 Abertura de Chamado")
    
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        contato = st.text_input("Seu WhatsApp")
        equip = st.selectbox("Aparelho", ["Notebook", "PC Gamer", "Monitor", "Outro"])
        problema = st.text_area("O que está acontecendo?")
        btn = st.form_submit_button("Gerar Protocolo")
        
        if btn:
            if nome and contato and problema:
                protocolo = datetime.datetime.now().strftime("%H%M%S")
                st.session_state.dados.append({
                    "Prot": protocolo, "Cliente": nome, "Zap": contato, 
                    "Equip": equip, "Defeito": problema, 
                    "Hora": datetime.datetime.now().strftime("%H:%M")
                })
                
                st.success(f"✅ Chamado #{protocolo} aberto!")
                
                # MENSAGEM FORMATADA PARA WHATSAPP
                msg_texto = (
                    f"*INFOHELP TATUÍ - NOVO CHAMADO*\n\n"
                    f"*Protocolo:* {protocolo}\n"
                    f"*Cliente:* {nome}\n"
                    f"*Equipamento:* {equip}\n"
                    f"*Problema:* {problema}"
                )
                
                # Link seguro com wa.me
                link_whatsapp = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(msg_texto)}"
                
                st.markdown(f"""
                    <div style="text-align:center; margin-top: 20px;">
                        <p><strong>Clique no botão abaixo para finalizar:</strong></p>
                        <a href="{link_whatsapp}" target="_blank" style="text-decoration:none;">
                            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; font-weight:bold; font-size:18px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                                💬 ENVIAR PARA O WHATSAPP DA INFOHELP
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Preencha todos os campos.")

elif escolha == "Área do Técnico (ADM)":
    if senha_digitada == SENHA_MESTRE:
        st.header("📊 Painel Técnico")
        if not st.session_state.dados:
            st.info("Nenhum chamado pendente.")
        else:
            df = pd.DataFrame(st.session_state.dados)
            st.dataframe(df, use_container_width=True)
            if st.button("Limpar Lista"):
                st.session_state.dados = []
                st.rerun()
    elif senha_digitada != "":
        st.error("❌ Senha incorreta.")