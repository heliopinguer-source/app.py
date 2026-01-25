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

# --- 2. ESTILO CSS (PADRÃO GRAFITE E LARANJA) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stForm { background-color: #1c1f26 !important; border-radius: 10px !important; border: 1px solid #3d4450 !important; padding: 20px; }
    label p { color: #FF6B00 !important; font-weight: bold; font-size: 16px; }
    h1, h2 { color: #FF6B00 !important; text-align: center; }
    
    /* ESCONDE ELEMENTOS NATIVOS */
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
        
        col_doc, col_zap = st.columns(2)
        with col_doc: doc = st.text_input("CPF / CNPJ")
        with col_zap: zap_cli = st.text_input("Seu WhatsApp")
        
        end = st.text_input("Endereço Completo")
        
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            tipo_equip = st.selectbox("Equipamento", ["Notebook", "Apple", "Desktop", "Monitor", "Placa de Vídeo", "Outro"])
        with col_eq2:
            modelo = st.text_input("Marca / Modelo")
            
        defe = st.text_area("Descrição do Defeito")
        
        # Área dos Botões Lado a Lado
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("GERAR PROTOCOLO")
            
        with col_btn2:
            placeholder_zap = st.empty()

        if submit:
            if nome and zap_cli and defe:
                prot = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
                equip_final = f"{tipo_equip} - {modelo}"
                
                # Dados para a Planilha
                payload = {"data": [{
                    "Protocolo": prot, 
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y"), 
                    "Cliente": nome, 
                    "Documento": doc, 
                    "WhatsApp": zap_cli, 
                    "Endereco": end, 
                    "Equipamento": equip_final, 
                    "Defeito": defe
                }]}
                
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code in [200, 201]:
                        st.write(f"✅ Protocolo **{prot}** registrado com sucesso!")
                        
                        # Mensagem do WhatsApp com a ficha completa
                        texto_zap = (f"*💻 NOVA OS INFOHELP*\n\n"
                                     f"*Protocolo:* {prot}\n"
                                     f"*Cliente:* {nome}\n"
                                     f"*CPF/CNPJ:* {doc}\n"
                                     f"*Endereço:* {end}\n"
                                     f"*WhatsApp Cli:* {zap_cli}\n"
                                     f"*Equipamento:* {equip_final}\n"
                                     f"*Defeito:* {defe}")
                        
                        link_direto = f"https://api.whatsapp.com/send?phone={WHATS_RECEPCAO}&text={urllib.parse.quote(texto_zap)}"
                        
                        # Aparece o botão verde ao lado do botão de gerar
                        with col_btn2:
                            st.markdown(f"""
                                <a href="{link_direto}" target="_blank" style="text-decoration:none;">
                                    <div style="background-color:#25D366; color:white; padding:12px; border-radius:5px; text-align:center; font-weight:bold; font-size:16px; height:50px; display:flex; align-items:center; justify-content:center; border: 1px solid white;">
                                        ENVIAR WHATSAPP AGORA 💬
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)
                        
                        st.warning("⚠️ **Atenção:** Clique no botão verde acima para concluir o envio!")
                    else:
                        st.error("Erro ao salvar os dados. Verifique a planilha.")
                except:
                    st.error("Erro de conexão com o servidor.")
            else:
                st.warning("⚠️ Por favor, preencha o Nome, WhatsApp e o Defeito.")

    # Acesso Técnico Discreto
    st.write("---")
    if st.button("🔧"):
        st.session_state.modo = 'login'
        st.rerun()

# --- 5. TELA DE LOGIN ---
elif st.session_state.modo == 'login':
    st.markdown("<h2>LOGIN TÉCNICO</h2>", unsafe_allow_html=True)
    senha = st.text_input("Senha de Acesso", type="password")
    if st.button("ACESSAR"):
        if senha == SENHA_ADMIN:
            st.session_state.modo = 'admin'
            st.rerun()
        else:
            st.error("Senha incorreta!")
    if st.button("CANCELAR"):
        st.session_state.modo = 'cliente'
        st.rerun()

# --- 6. TELA ADMIN (GERENCIAR CHAMADOS) ---
elif st.session_state.modo == 'admin':
    st.markdown("<h2>GERENCIAR CHAMADOS</h2>", unsafe_allow_html=True)
    if st.button("VOLTAR AO FORMULÁRIO"):
        st.session_state.modo = 'cliente'
        st.rerun()
        
    try:
        # Puxa dados da planilha
        r = requests.get(f"{API_URL}?_={time.time()}")
        df = pd.DataFrame(r.json())
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("🗑️ Finalizar Registro")
            lista_prot = df["Protocolo"].tolist()
            excluir = st.selectbox("Selecione o Protocolo para apagar:", lista_prot)
            
            if st.button("EXCLUIR DEFINITIVAMENTE"):
                del_res = requests.delete(f"{API_URL}/Protocolo/{excluir}")
                if del_res.status_code in [200, 204]:
                    st.success(f"Protocolo {excluir} removido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Erro ao excluir.")
        else:
            st.info("Nenhuma ordem de serviço encontrada.")
    except:
        st.error("Não foi possível carregar os dados da planilha.")