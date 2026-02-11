import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Bruno Hohl | Assessment", layout="wide", page_icon="🧭")

# ==========================================
# FUNÇÃO DE SALVAMENTO (GOOGLE SHEETS)
# ==========================================
def salvar_dados(nome, email, scores, moedas, indices):
    # Cria a linha de dados
    dados_novos = pd.DataFrame([{
        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Nome": nome,
        "Email": email,
        "I_Entropia": indices['ep'],
        "I_Prontidao": indices['ps'],
        "I_Sustentabilidade": indices['cf'],
        "Maior_Entropia": indices['maior_medo'],
        "Renuncias": str(indices['zeros']),
        "Top_Apostas": str(indices['top3']),
        "Scores_Fase1": str(scores),
        "Moedas_Fase2": str(moedas)
    }])
    
    try:
        # Conecta à planilha
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Lê dados existentes (se houver)
        try:
            dados_existentes = conn.read()
            df_final = pd.concat([dados_existentes, dados_novos], ignore_index=True)
        except:
            df_final = dados_novos
            
        # Atualiza a planilha
        conn.update(data=df_final)
        return True
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return False

# ==========================================
# DADOS E LÓGICA (Mantidos do anterior)
# ==========================================
# ... (COPIAR AQUI AS LISTAS 'perguntas_fase1', 'cenarios_fase2', ETC DO CÓDIGO ANTERIOR) ...
# ... Para economizar espaço aqui, use as mesmas listas de perguntas do código anterior ...
# ... Se precisar eu colo tudo de novo, mas a lógica de perguntas é idêntica ...

perguntas_fase1 = [
    {"id": 1, "tag_A": "E1", "tag_B": "L5", "frase_A": "Preciso ter previsibilidade financeira...", "frase_B": "Prefiro agir alinhado ao meu propósito..."},
    # ... (Imagine todas as 21 perguntas aqui) ...
    # IMPORTANTE: No seu código final, garanta que todas as perguntas estejam aqui!
]
# Vou simplificar apenas para caber na resposta, mas mantenha o seu dicionário completo.
# Se tiver dúvida, use o código anterior completo e só adicione a função salvar_dados no topo.

# ==========================================
# GESTÃO DE ESTADO
# ==========================================
if 'etapa' not in st.session_state: st.session_state.etapa = 0
if 'respostas_fase1' not in st.session_state: st.session_state.respostas_fase1 = {}
if 'respostas_fase2' not in st.session_state: st.session_state.respostas_fase2 = {}
if 'dados_cliente' not in st.session_state: st.session_state.dados_cliente = {"nome": "", "email": ""}

# ==========================================
# INTERFACE
# ==========================================

# ETAPA 0: CADASTRO
if st.session_state.etapa == 0:
    st.title("🧭 Radiografia do Momento")
    st.markdown("Bem-vindo ao Método Bruno Hohl.")
    with st.form("cadastro"):
        nome = st.text_input("Seu Nome Completo")
        email = st.text_input("Seu E-mail")
        submit = st.form_submit_button("Iniciar Diagnóstico")
        if submit and nome and email:
            st.session_state.dados_cliente = {"nome": nome, "email": email}
            st.session_state.etapa = 1
            st.rerun()

# ETAPA 1 e 2 (Igual ao código anterior - use a mesma lógica de avançar)
# ...

# ETAPA 3: DASHBOARD E ENVIO
elif st.session_state.etapa == 3:
    # ... (Todo o código de cálculo e gráficos do Dashboard anterior vai aqui) ...
    
    st.markdown("---")
    st.header("📤 Enviar Resultados para o Coach")
    st.info("Clique abaixo para registrar oficialmente seu diagnóstico na base de dados do Bruno Hohl.")
    
    if st.button("💾 Finalizar e Enviar Dados", type="primary"):
        # Prepara os índices para salvar
        indices_save = {
            "ep": i_ep, "ps": i_ps, "cf": i_cf,
            "maior_medo": msg_ent, # Variável do dashboard anterior
            "zeros": zeros, # Lista de zeros
            "top3": sorted_moedas[:3] # Top apostas
        }
        
        sucesso = salvar_dados(
            st.session_state.dados_cliente['nome'],
            st.session_state.dados_cliente['email'],
            scores,
            moedas,
            indices_save
        )
        
        if sucesso:
            st.success("✅ Dados enviados com sucesso! Aguarde o contato do seu coach.")
            st.balloons()    
