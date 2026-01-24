import streamlit as st
import datetime
import urllib.parse
import requests
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí | Suporte",
    page_icon="💻",
    layout="centered",
    initial_sidebar_state="collapsed" # Menu começa recolhido para não atrapalhar
)

# Bloqueio contra erro de tradução (NotFoundError)
st.markdown("<script>document.documentElement.lang = 'pt-br';</script>", unsafe_allow_html=True)

# =========================================================
# ⚙️ 2. CONFIGURAÇÕES
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115" 

# --- 3. ESTILO CSS (Fixando o visual) ---
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
        background-color: #FF6B00 !important; color: white !important; width: 100% !important; 
        border-radius: 10px !important; font-weight: bold !important; font-size: 20px !important; 
        height: 60px !important; border: none !important; 
    }
    .header-text { text-align: center; color: #FF6B00; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MENU LATERAL ---
with st.sidebar:
    st.markdown("<h2 style='color:#FF6B00;'>INFOHELP ADMIN</h2>", unsafe_allow_html=True)
    aba = st.radio("Navegação:", ["📝 Abrir Chamado", "🔒 Área Técnica"])
    st.divider()
    senha_digitada = ""
    if aba == "🔒 Área Técnica":
        senha_digitada = st.text_input("Senha de Acesso", type="password")

# =========================================================
# 🏠 5. PÁGINA: ABRIR CHAMADO
# =========================================================
if aba == "📝 Abrir Chamado":
    st.markdown("<h1 class='header-text'>INFOHELP TATUÍ</h1>", unsafe_allow_html=True)
    
    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        zap_cliente = st.text_input("WhatsApp (com DDD)")
        col1, col2 = st.columns(2)
        with col1:
            tipo_equip = st.selectbox("Aparelho", ["Notebook", "Desktop", "Monitor", "Impressora", "Outro"])
        with col2:
            modelo = st.text_input("Marca / Modelo")
        defeito = st.text_area("Descrição do Defeito")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            equip_completo = f"{tipo_equip} - {modelo}"
            
            payload = {"data": [{"Protocolo": protocolo, "Data": data_atual, "Cliente": nome, "WhatsApp": zap_cliente, "Equipamento": equip_completo, "Defeito": defeito}]}
            
            try:
                # Envia para SheetDB
                requests.post(API_URL, json=payload)
                st.success(f"Protocolo #{protocolo} gerado com sucesso!")
                
                # Mensagem completa para o WhatsApp
                texto_zap = f"*💻 NOVO CHAMADO*\n*🎫 Protocolo:* {protocolo}\n*👤 Cliente:* {nome}\n*⚙️ Equip:* {equip_completo}\n*🛠️ Defeito:* {defeito}"
                link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
                
                st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
            except:
                st.error("Erro ao salvar os dados na planilha.")
        else:
            st.warning("⚠️ Por favor, preencha todos os campos!")

# =========================================================
# 📊 6. PÁGINA: ÁREA TÉCNICA (ADMIN + EXCLUSÃO)
# =========================================================
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Gerenciar Chamados</h2>", unsafe_allow_html=True)
        
        # Função para carregar dados
        def carregar_dados():
            try:
                resp = requests.get(API_URL)
                if resp.status_code == 200:
                    return resp.json()
                return []
            except:
                return []

        dados = carregar_dados()
        
        if dados:
            df = pd.DataFrame(dados)
            # Mostra a tabela de chamados
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("🗑️ Finalizar Chamado")
            
            col_sel, col_btn = st.columns([2, 1])
            with col_sel:
                lista_protocolos = df["Protocolo"].tolist()
                prot_excluir = st.selectbox("Escolha o chamado concluído:", lista_protocolos)
            
            with col_btn:
                st.write(" ") # Ajuste de altura
                if st.button("EXCLUIR REGISTRO"):
                    # Deletar no SheetDB
                    url_delete = f"{API_URL}/Protocolo/{prot_excluir}"
                    try:
                        res = requests.delete(url_delete)
                        if res.status_code in [200, 204]:
                            st.success(f"Chamado {prot_excluir} removido!")
                            st.rerun() # Força a atualização da lista
                        else:
                            st.error("Erro ao apagar na planilha.")
                    except:
                        st.error("Erro de conexão ao excluir.")
        else:
            st.info("Não há chamados registrados no momento.")
            
    elif senha_digitada != "":
        st.error("Senha Administrativa Incorreta!")