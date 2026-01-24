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
    initial_sidebar_state="collapsed"
)

# Bloqueio contra erro de tradução do navegador
st.markdown("<script>document.documentElement.lang = 'pt-br';</script>", unsafe_allow_html=True)

# =========================================================
# ⚙️ 2. CONFIGURAÇÕES
# =========================================================
API_URL = "https://sheetdb.io/api/v1/1soffxez5h6tb"
SENHA_ADMIN = "infohelp2026"
MEU_WHATSAPP = "5515991172115" 

# --- 3. ESTILO CSS ---
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
        defeito = st.text_area("O que está acontecendo?")
        submit = st.form_submit_button("GERAR PROTOCOLO")

    if submit:
        if nome and zap_cliente and defeito:
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            equip_completo = f"{tipo_equip} - {modelo}"
            
            payload = {"data": [{"Protocolo": protocolo, "Data": data_atual, "Cliente": nome, "WhatsApp": zap_cliente, "Equipamento": equip_completo, "Defeito": defeito}]}
            
            try:
                requests.post(API_URL, json=payload)
                st.success(f"Protocolo #{protocolo} gerado!")
                
                texto_zap = (
                    f"*💻 NOVO CHAMADO*\n\n"
                    f"*🎫 Protocolo:* {protocolo}\n"
                    f"*👤 Cliente:* {nome}\n"
                    f"*⚙️ Equipamento:* {equip_completo}\n"
                    f"*🛠️ Defeito:* {defeito}"
                )
                link_zap = f"https://wa.me/{MEU_WHATSAPP}?text={urllib.parse.quote(texto_zap)}"
                st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:18px; border-radius:10px; text-align:center; font-weight:bold;">💬 ENVIAR PARA WHATSAPP</div></a>', unsafe_allow_html=True)
            except:
                st.error("Erro ao salvar dados.")
        else:
            st.warning("Preencha todos os campos!")

# =========================================================
# 📊 6. PÁGINA: ÁREA TÉCNICA (ADMIN + EXCLUSÃO + FIX DE DADOS)
# =========================================================
elif aba == "🔒 Área Técnica":
    if senha_digitada == SENHA_ADMIN:
        st.markdown("<h2 style='color:#FF6B00;'>Gerenciar Chamados</h2>", unsafe_allow_html=True)
        
        # Botão para atualizar (limpa cache)
        if st.button("🔄 ATUALIZAR LISTA"):
            st.rerun()

        try:
            # Puxa os dados com um parâmetro aleatório para evitar cache do SheetDB
            resp = requests.get(f"{API_URL}?_={datetime.datetime.now().timestamp()}")
            
            if resp.status_code == 200:
                dados = resp.json()
                
                if isinstance(dados, list) and len(dados) > 0:
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
                    
                    st.divider()
                    st.subheader("🗑️ Finalizar e Excluir Chamado")
                    
                    col_sel, col_btn = st.columns([2, 1])
                    with col_sel:
                        if "Protocolo" in df.columns:
                            lista_prot = df["Protocolo"].tolist()
                            prot_excluir = st.selectbox("Escolha o protocolo para APAGAR:", lista_prot)
                        else:
                            st.error("Coluna 'Protocolo' não encontrada na planilha!")
                            prot_excluir = None
                    
                    with col_btn:
                        st.write(" ") 
                        if prot_excluir and st.button("❌ APAGAR AGORA"):
                            # URL de exclusão específica do SheetDB
                            url_delete = f"{API_URL}/Protocolo/{prot_excluir}"
                            res_del = requests.delete(url_delete)
                            
                            if res_del.status_code in [200, 201, 204]:
                                st.success(f"Chamado {prot_excluir} removido!")
                                st.rerun()
                            else:
                                st.error("Erro ao apagar. Verifique se o DELETE está ativo no site SheetDB.")
                else:
                    st.info("A planilha parece estar vazia ou os dados ainda não carregaram.")
            else:
                st.error("Falha na conexão com a planilha.")
        except Exception as e:
            st.error(f"Erro de carregamento: {e}")
            
    elif senha_digitada != "":
        st.error("Senha Administrativa Incorreta!")