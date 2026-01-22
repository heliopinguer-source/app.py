import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí - Sistema de Atendimento",
    page_icon="💻",
    layout="wide"
)

# --- CONFIGURAÇÕES DO DONO (Mude aqui) ---
WHATSAPP_TECNICO = "5515999999999" # Coloque seu número com DDD
SENHA_ADMIN = "infohelp2024"       # Defina sua senha de acesso ao painel

# --- ESTILIZAÇÃO CSS ---
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .stButton>button {{ width: 100%; border-radius: 8px; background-color: #007BFF; color: white; font-weight: bold; }}
    .stMetric {{ background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    .status-badge {{ padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS EM MEMÓRIA ---
if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=80)
    st.title("InfoHelp Tatuí")
    st.write("---")
    # Menu de navegação
    aba = st.radio("Navegação:", ["📋 Abrir Chamado", "🔐 Painel Técnico (ADM)"])
    st.write("---")
    st.caption("Versão Profissional 1.0")

# --- CONTEÚDO PRINCIPAL ---

if aba == "📋 Abrir Chamado":
    st.header("🏢 Portal de Atendimento ao Cliente")
    st.write("Preencha os campos abaixo para iniciar seu suporte técnico.")
    
    with st.container():
        with st.form("form_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo")
                whatsapp_cli = st.text_input("Seu WhatsApp (com DDD)")
            with col2:
                aparelho = st.selectbox("Equipamento", ["Notebook", "Desktop / PC Gamer", "Monitor", "Rede / Wi-Fi", "Outro"])
                modelo = st.text_input("Marca / Modelo")
            
            detalhes = st.text_area("Descreva o problema detalhadamente")
            
            enviar = st.form_submit_button("GERAR ORDEM DE SERVIÇO")

        if enviar:
            if nome and whatsapp_cli and detalhes:
                # Gerar ID único
                protocolo = f"IH-{datetime.datetime.now().strftime('%d%H%M')}"
                
                # Inteligência de Triagem
                palavras_urgentes = ["parou", "urgente", "socorro", "empresa", "trabalho", "não liga", "quebrou", "azul"]
                nivel = "Alta" if any(p in detalhes.lower() for p in palavras_urgentes) else "Normal"
                
                # Salvar chamado
                novo_chamado = {
                    "ID": protocolo,
                    "Cliente": nome,
                    "Contato": whatsapp_cli,
                    "Equipamento": f"{aparelho} {modelo}",
                    "Problema": detalhes,
                    "Prioridade": nivel,
                    "Status": "Aguardando",
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.db_chamados.append(novo_chamado)
                
                # Mensagem para o WhatsApp do Técnico
                texto_zap = f"*INFOHELP TATUÍ - NOVO CHAMADO*\n\n*Protocolo:* {protocolo}\n*Cliente:* {nome}\n*Aparelho:* {aparelho}\n*Problema:* {detalhes}\n*Prioridade:* {nivel}"
                link_whatsapp = f"https://wa.me/{WHATSAPP_TECNICO}?text={urllib.parse.quote(texto_zap)}"
                
                st.success(f"✅ Protocolo #{protocolo} gerado com sucesso!")
                
                st.markdown(f"""
                    <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; border: 2px solid #25D366; text-align: center;">
                        <h3 style="color: #25D366;">Quase pronto!</h3>
                        <p>Para confirmar seu atendimento, clique no botão abaixo e envie a mensagem automática para o nosso técnico.</p>
                        <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 8px; font-weight: bold; font-size: 18px; cursor: pointer;">
                                💬 ENVIAR DADOS VIA WHATSAPP
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Por favor, preencha Nome, WhatsApp e Descrição.")

elif aba == "🔐 Painel Técnico (ADM)":
    st.header("Painel de Gerenciamento")
    
    # Sistema de Senha
    senha_digitada = st.sidebar.text_input("Senha de Acesso", type="password")
    
    if senha_digitada == SENHA_ADMIN:
        st.success("Bem-vindo, técnico da InfoHelp!")
        
        if not st.session_state.db_chamados:
            st.info("Nenhum chamado pendente no momento.")
        else:
            # Dashboard de Resumo
            df = pd.DataFrame(st.session_state.db_chamados)
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Chamados Totais", len(df))
            col_m2.metric("Urgentes (Alta)", len(df[df['Prioridade'] == 'Alta']))
            col_m3.metric("Última Atualização", datetime.datetime.now().strftime("%H:%M"))
            
            st.write("### Fila de Atendimento")
            for c in st.session_state.db_chamados:
                with st.expander(f"📦 #{c['ID']} - {c['Cliente']}"):
                    c_left, c_right = st.columns([3, 1])
                    with c_left:
                        st.write(f"**Aparelho:** {c['Equipamento']}")
                        st.write(f"**Relato:** {c['Problema']}")
                    with c_right:
                        cor = "#dc3545" if c['Prioridade'] == "Alta" else "#28a745"
                        st.markdown(f"<span class='status-badge' style='background-color:{cor}'>{c['Prioridade']}</span>", unsafe_allow_html=True)
                        st.write(f"**Contato:** {c['Contato']}")
                        st.caption(f"Data: {c['Data']}")
    
    elif senha_digitada == "":
        st.info("Por favor, digite a senha na barra lateral para visualizar os dados.")
    else:
        st.error("Senha incorreta. Acesso bloqueado.")