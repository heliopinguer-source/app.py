import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configurações de Identidade Visual
COR_PRIMARIA = "#007BFF"  # Azul Profissional

st.set_page_config(
    page_title="InfoHelp Tatuí - Atendimento",
    page_icon="💻",
    layout="wide"
)

# Estilização CSS para deixar com cara de App Profissional
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .stButton>button {{ width: 100%; border-radius: 5px; height: 3em; background-color: {COR_PRIMARIA}; color: white; font-weight: bold; }}
    .stMetric {{ background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    .status-badge {{ padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; color: white; }}
    div[data-testid="stExpander"] {{ background-color: white; border-radius: 10px; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# Inicialização do Banco de Dados Temporário
if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- CABEÇALHO ---
st.title("🤖 Assistente Virtual InfoHelp")
st.write("Suporte técnico especializado em Tatuí e região.")
st.divider()

# --- MENU LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=100) # Ícone Genérico de Suporte
    st.title("Menu Principal")
    aba = st.radio("Selecione uma opção:", ["📋 Abrir Chamado", "🛠️ Painel Técnico (ADM)"])
    st.info("InfoHelp Tatuí - v1.0")

if aba == "📋 Abrir Chamado":
    st.subheader("Olá! Conte-nos o que aconteceu com seu equipamento.")
    
    with st.container():
        with st.form("form_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Seu Nome Completo")
                whatsapp = st.text_input("WhatsApp com DDD (Ex: 15999999999)")
            with col2:
                aparelho = st.selectbox("O que precisa de conserto?", ["Notebook", "PC Gamer / Desktop", "Monitor", "Impressora", "Rede / Wi-Fi", "Outros"])
                modelo = st.text_input("Marca ou Modelo (Opcional)")
            
            detalhes = st.text_area("Descreva o defeito ou o serviço que você precisa")
            
            enviar = st.form_submit_button("GERAR PROTOCOLO DE ATENDIMENTO")

        if enviar:
            if nome and whatsapp and detalhes:
                # Gerar Protocolo baseado na hora atual
                protocolo = f"IH-{datetime.datetime.now().strftime('%d%H%M')}"
                
                # Triagem Automática em Português
                palavras_urgentes = ["parou", "urgente", "socorro", "empresa", "trabalho", "não liga", "quebrou"]
                nivel = "Alta" if any(p in detalhes.lower() for p in palavras_urgentes) else "Normal"
                
                # Salvar no Estado da Sessão
                novo_chamado = {
                    "Protocolo": protocolo,
                    "Cliente": nome,
                    "WhatsApp": whatsapp,
                    "Aparelho": f"{aparelho} {modelo}",
                    "Relato": detalhes,
                    "Prioridade": nivel,
                    "Status": "Novo",
                    "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                st.session_state.db_chamados.append(novo_chamado)
                
                # Link para o seu WhatsApp (Troque pelo seu número real)
                SEU_NUMERO = "5515999999999" # <--- COLOQUE SEU NÚMERO AQUI
                texto_zap = f"*INFOHELP TATUÍ - NOVO CHAMADO*\n\n*Prot:* {protocolo}\n*Cliente:* {nome}\n*Aparelho:* {aparelho}\n*Defeito:* {detalhes}\n*Prioridade:* {nivel}"
                link_final = f"https://wa.me/{SEU_NUMERO}?text={urllib.parse.quote(texto_zap)}"
                
                st.success(f"✅ Protocolo #{protocolo} gerado com sucesso!")
                
                # Botão Estilizado para o WhatsApp
                st.markdown(f"""
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border: 1px solid #90caf9; text-align: center;">
                        <h4 style="color: #0d47a1;">Ação Necessária:</h4>
                        <p>Para acelerar seu atendimento, envie os dados para o nosso técnico agora:</p>
                        <a href="{link_final}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 8px; font-weight: bold; font-size: 18px;">
                                💬 ENVIAR VIA WHATSAPP
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ Por favor, preencha o Nome, WhatsApp e a Descrição.")

elif aba == "🛠️ Painel Técnico (ADM)":
    st.subheader("Painel de Gestão - InfoHelp")
    
    if not st.session_state.db_chamados:
        st.info("Aguardando novos chamados de clientes...")
    else:
        # Dashboard de Resumo
        df = pd.DataFrame(st.session_state.db_chamados)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Hoje", len(df))
        m2.metric("Urgentes", len(df[df['Prioridade'] == 'Alta']))
        m3.metric("Concluídos", "0") # Aqui você pode adicionar lógica de conclusão
        
        st.write("---")
        # Lista de Cards
        for c in st.session_state.db_chamados:
            with st.expander(f"📦 {c['Protocolo']} - {c['Cliente']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Aparelho:** {c['Aparelho']}")
                    st.write(f"**Relato:** {c['Relato']}")
                with c2:
                    cor_prio = "#dc3545" if c['Prioridade'] == "Alta" else "#28a745"
                    st.markdown(f"Prioridade: <span class='status-badge' style='background-color:{cor_prio}'>{c['Prioridade']}</span>", unsafe_allow_html=True)
                    st.write(f"**Zap:** {c['WhatsApp']}")
                    st.caption(f"Recebido em: {c['Data']}")