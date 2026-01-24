import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte",
    page_icon="💻",
    layout="centered"
)

# Bloqueio contra erro de tradução do Google (evita o erro 'removeChild')
st.markdown("<script>document.documentElement.lang = 'pt-br';</script>", unsafe_allow_html=True)

# =========================================================
# ⚙️ 2. CONFIGURAÇÕES (JÁ COM SEUS DADOS)
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115" 

# --- 3. ESTILO VISUAL (CSS) ---
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

# --- 4. MENU LATERAL (NAVEGAÇÃO) ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>INFOHELP TATUÍ</h2>", unsafe_allow_html=True)
    st.write("Sistema de Gerenciamento")
    aba = st.radio("Selecione a página:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    
    if aba == "🔒 Área Técnica":
        senha_digitada = st.text_input("Senha Administrativa", type="password")

# =========================================================
# 🏠 5. PÁGINA: ABRIR CHAMADO (CLIENTE)
# =========================================================
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 class='header-text'>SOLICITAR SUPORTE</h1>", unsafe_allow_html=True)

    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap_cliente = st.text_input("WhatsApp (com DDD)")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca / Modelo")
            
        defeito = st.text_area("O que está acontecendo? (Descrição do Defeito)")
        
        submit = st.form_submit_button("GERAR MEU PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            # Gerar dados do chamado
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            equip_completo = f"{tipo_equip} - {modelo}"
            
            # Enviar para a Planilha via SheetDB
            payload = {
                "data": [{
                    "Protocolo": protocolo,
                    "Data": data_atual,
                    "Cliente": nome,
                    "WhatsApp": zap_cliente,
                    "Equipamento": equip_completo,
                    "Defeito": defeito
                }]
            }

            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code in [200, 201]:
                    st.success(f"Protocolo #{protocolo} gerado com sucesso!")
                    
                    # Montar Mensagem do WhatsApp Completa
                    texto_zap = (
                        f"*💻 NOVO CHAMADO - INFOHELP*\n\n"
                        f"*🎫 Protocolo:* {protocolo}\n"
                        f"*👤 Cliente:* {nome}\n"
                        f"*⚙️ Equipamento:* {equip_completo}\n"
                        f"*🛠️ Defeito:* {defeito}"
                    )
                    
                    link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
                    
                    # Botão Grande para WhatsApp
                    st.markdown(f"""
                        <a href="{link_zap}" target="_blank" style="text-decoration:none;">
                            <div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.1em; margin-top:10px;">
                                💬 ENVIAR CHAMADO VIA WHATSAPP
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("Erro ao salvar na planilha. Verifique a API.")
            except:
                st.error("Erro de conexão. Tente novamente.")
        else:
            st.warning("⚠️ Por favor, preencha todos os campos para continuar.")

# =========================================================
# 📊 6. PÁGINA: ÁREA TÉCNICA (ADMIN)
# =========================================================
elif aba == "🔒 Área Técnica":
    if 'senha_digitada' in locals() and senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>📋 Chamados Recebidos</h2>", unsafe_allow_html=True)
        
        try:
            # Puxar dados da planilha
            resp = requests.get(API_URL)
            if resp.status_code == 200:
                dados = resp.json()
                if dados:
                    df = pd.DataFrame(dados)
                    # Mostrar Tabela
                    st.dataframe(df, use_container_width=True)
                    
                    # Visualizador de Detalhes
                    st.divider()
                    st.subheader("🔍 Detalhes do Problema")
                    selecao = st.selectbox("Selecione um Protocolo para ler:", df["Protocolo"].tolist())
                    texto_defeito = df[df["Protocolo"] == selecao]["Defeito"].values[0]
                    st.warning(f"**Relato do Cliente:** {texto_defeito}")
                else:
                    st.info("Ainda não há chamados registrados na planilha.")
            else:
                st.error("Não foi possível acessar os dados da planilha.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            
    elif 'senha_digitada' in locals() and senha_digitada != "":
        st.error("Senha Administrativa Incorreta!")
    else:
        st.info("Digite a senha no menu lateral para acessar os dados.")