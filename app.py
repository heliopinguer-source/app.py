import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; }
    h1 { color: #FF6B00 !important; text-align: center; }
    
    /* ESCONDE SIDEBAR E ELEMENTOS NATIVOS */
    [data-testid="stSidebarNav"], [data-testid="collapsedControl"], #MainMenu, footer {display: none;}
    
    /* Botão Branco de Gerar Protocolo */
    div.stButton > button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold; 
        width: 100%; 
        height: 50px; 
        border: none; 
    }
    
    /* Alerta de Finalização */
    .alerta-final {
        text-align: center;
        background-color: #ff6b0022;
        border: 2px dashed #FF6B00;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURAÇÕES ---
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
WHATS_RECEPCAO = "5515991172115" 

if 'modo' not in st.session_state:
    st.session_state.modo = 'cliente'

# --- 4. TELA DO CLIENTE ---
if st.session_state.modo == 'cliente':
    st.markdown("<h1>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("novo_chamado", clear_on_submit=False):
        nome = st.text_input("Nome Completo / Razão Social")
        
        c1, c2 = st.columns(2)
        with c1: doc = st.text_input("CPF / CNPJ")
        with c2: zap_cli = st.text_input("Seu WhatsApp")
        
        end = st.text_input("Endereço Completo")
        
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            tipo_equip = st.selectbox("Equipamento", ["Notebook", "Apple", "Desktop", "Monitor", "Placa de Vídeo", "Outro"])
        with col_eq2:
            modelo = st.text_input("Marca / Modelo")
            
        defe = st.text_area("Descrição do Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cli and defe:
            prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            equip_final = f"{tipo_equip} - {modelo}"
            
            payload = {"data": [{
                "Protocolo": prot, "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                "Cliente": nome, "Documento": doc, "WhatsApp": zap_cli, 
                "Endereco": end, "Equipamento": equip_final, "Defeito": defe
            }]}
            
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code in [200, 201]:
                    # --- ANIMAÇÃO TEMA ELETRÔNICA ---
                    st.snow() # Efeito de partículas
                    st.toast('Processando reparo...', icon='📟')
                    
                    st.success(f"✅ Protocolo {prot} Registrado no Sistema!")
                    
                    texto_zap = (f"*💻 NOVA OS INFOHELP*\n\n"
                                 f"*Protocolo:* {prot}\n"
                                 f"*Cliente:* {nome}\n"
                                 f"*Equipamento:* {equip_final}\n"
                                 f"*Defeito:* {defe}")
                    
                    link_direto = f"https://api.whatsapp.com/send?phone={WHATS_RECEPCAO}&text={urllib.parse.quote(texto_zap)}"
                    
                    # --- QUADRO DE AVISO FINAL ---
                    st.markdown(f"""
                        <div class="alerta-final">
                            <h3 style="color: #FF6B00; margin-top: 0;">⚠️ ETAPA FINAL OBRIGATÓRIA</h3>
                            <p style="color: white; font-size: 18px;">
                                Para validar sua entrada na assistência, clique no botão verde abaixo e envie a mensagem.
                            </p>
                            <a href="{link_direto}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold; font-size:22px; border: 2px solid white;">
                                    💬 CONCLUIR NO WHATSAPP
                                </div>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Erro técnico ao salvar.")
            except:
                st.error("Erro de conexão.")
        else:
            st.warning("⚠️ Preencha os campos obrigatórios.")

    st.write("---")
    if st.button("🔧"):
        st.session_state.modo = 'login'
        st.rerun()

# --- 5. TELA DE LOGIN E ADMIN (Igual anterior) ---
elif st.session_state.modo == 'login':
    st.markdown("<h2>LOGIN TÉCNICO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha", type="password")
    if st.button("ACESSAR"):
        if senha == SENHA_ADMIN: st.session_state.modo = 'admin'; st.rerun()
        else: st.error("Incorreta")
    if st.button("CANCELAR"): st.session_state.modo = 'cliente'; st.rerun()

elif st.session_state.modo == 'admin':
    st.markdown("<h2>GERENCIAR CHAMADOS</h2>", unsafe_allow_html=True)
    if st.button("VOLTAR"): st.session_state.modo = 'cliente'; st.rerun()
    try:
        r = requests.get(f"{API_URL}?_={time.time()}")
        df = pd.DataFrame(r.json())
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            st.divider()
            excluir = st.selectbox("Finalizar OS:", df["Protocolo"].tolist())
            if st.button("EXCLUIR REGISTRO"):
                requests.delete(f"{API_URL}/Protocolo/{excluir}")
                st.rerun()
    except: st.error("Erro ao carregar dados.")