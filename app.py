import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="InfoHelp Tatuí - Suporte",
    page_icon="💻",
    layout="wide"
)

# =========================================================
# 🔐 CONFIGURAÇÕES PRINCIPAIS (Mude aqui)
# =========================================================
SENHA_ADMIN = "infohelp2026"        # Senha para acessar o painel
NUMERO_WHATSAPP = "5515991172115"   # COLOQUE SEU NÚMERO AQUI (55 + DDD + Numero)
# =========================================================

# Limpeza do número para evitar erros de link
SEU_WHATSAPP = re.sub(r'\D', '', NUMERO_WHATSAPP)

# Inicializa o banco de dados na memória
if "db_chamados" not in st.session_state:
    st.session_state.db_chamados = []

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .status-alta { background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .status-normal { background-color: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=70)
    st.title("Menu InfoHelp")
    aba = st.radio("Navegar para:", ["📋 Abrir Chamado", "🔐 Painel ADM"])
    st.write("---")
    
    senha_digitada = ""
    if aba == "🔐 Painel ADM":
        st.subheader("Acesso Restrito")
        senha_digitada = st.text_input("Digite a Senha", type="password")

# --- LÓGICA DAS PÁGINAS ---

if aba == "📋 Abrir Chamado":
    st.header("🏢 Portal de Atendimento - InfoHelp Tatuí")
    st.write("Conte-nos o que houve com seu equipamento para iniciarmos o suporte.")
    
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Seu Nome Completo")
            zap_cliente = st.text_input("Seu WhatsApp com DDD")
        with col2:
            aparelho = st.selectbox("Equipamento", ["Notebook", "Desktop / PC Gamer", "Monitor", "Impressora", "Rede / Wi-Fi", "Outro"])
            modelo = st.text_input("Marca / Modelo (Opcional)")
        
        # O campo que você quer que apareça no WhatsApp:
        detalhes_defeito = st.text_area("O que está acontecendo? (Descreva o defeito)")
        
        btn_enviar = st.form_submit_button("GERAR PROTOCOLO")

    if btn_enviar:
        if nome and zap_cliente and detalhes_defeito:
            # Gerar Protocolo e Triagem
            protocolo = f"IH-{datetime.datetime.now().strftime('%H%M%S')}"
            urgencia = ["parou", "urgente", "não liga", "quebrou", "tela azul", "trabalho"]
            nivel = "Alta" if any(p in detalhes_defeito.lower() for p in urgencia) else "Normal"
            
            # Salvar no sistema
            novo_item = {
                "ID": protocolo, "Cliente": nome, "WhatsApp": zap_cliente,
                "Equipamento": f"{aparelho} {modelo}", "Relato": detalhes_defeito,
                "Prioridade": nivel, "Data": datetime.datetime.now().strftime("%d/%m %H:%M")
            }
            st.session_state.db_chamados.append(novo_item)
            
            # --- MONTAGEM DA MENSAGEM DO WHATSAPP ---
            # Aqui incluímos o campo detalhes_defeito
            texto_formatado = (
                f"*INFOHELP TATUÍ - NOVO CHAMADO*\n\n"
                f"*Protocolo:* {protocolo}\n"
                f"*Cliente:* {nome}\n"
                f"*Equipamento:* {aparelho} {modelo}\n"
                f"*RELATO DO DEFEITO:* {detalhes_defeito}"
            )
            
            link_final = f"https://wa.me/{SEU_WHATSAPP}?text={urllib.parse.quote(texto_formatado)}"
            
            st.success(f"✅ Protocolo #{protocolo} gerado com sucesso!")
            
            # Botão de Ação do WhatsApp
            st.markdown(f"""
                <div style="background-color:#ffffff; padding:20px; border-radius:10px; border:2px solid #25D366; text-align:center;">
                    <h4 style="color:#25D366; margin-bottom:10px;">Ação Necessária:</h4>
                    <p>Clique no botão abaixo para enviar os detalhes ao nosso técnico:</p>
                    <a href="{link_final}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#25D366; color:white; padding:15px; border-radius:8px; font-weight:bold; font-size:18px;">
                            💬 ENVIAR VIA WHATSAPP
                        </div>
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Por favor, preencha o Nome, WhatsApp e o que está acontecendo.")

elif aba == "🔐 Painel ADM":
    if senha_digitada == SENHA_ADMIN:
        st.header("📊 Gestão de Chamados")
        
        if not st.session_state.db_chamados:
            st.info("Nenhum chamado recebido nesta sessão.")
        else:
            df = pd.DataFrame(st.session_state.db_chamados)
            
            # Métricas Rápidas
            c1, c2 = st.columns(2)
            c1.metric("Total de Chamados", len(df))
            c2.metric("Urgentes (Alta)", len(df[df['Prioridade'] == 'Alta']))
            
            st.write("### Fila de Trabalho")
            for item in st.session_state.db_chamados:
                classe_cor = "status-alta" if item['Prioridade'] == "Alta" else "status-normal"
                with st.expander(f"📦 {item['ID']} - {item['Cliente']}"):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**Aparelho:** {item['Equipamento']}")
                        st.write(f"**Defeito:** {item['Relato']}")
                    with col_b:
                        st.markdown(f"Prio: <span class='{classe_cor}'>{item['Prioridade']}</span>", unsafe_allow_html=True)
                        st.write(f"**Zap:** {item['WhatsApp']}")
                        st.caption(f"Recebido: {item['Data']}")
            
            if st.button("Limpar Todos os Dados"):
                st.session_state.db_chamados = []
                st.rerun()
    elif senha_digitada != "":
        st.error("❌ Senha incorreta. Acesso negado.")
    else:
        st.info("Digite a senha na barra lateral para visualizar os chamados.")