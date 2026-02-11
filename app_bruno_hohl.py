import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

# ==========================================
# 1. ESTÉTICA BRUNO HOHL (CUSTOM CSS)
# ==========================================
st.set_page_config(page_title="Bruno Hohl | Assessment", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    /* Estética Inspirada em brunohohl.com */
    :root {
        --primary-color: #000000;
        --accent-color: #27AE60;
        --bg-light: #F9F9F9;
    }
    
    .stApp {
        background-color: white;
    }

    /* Esconder elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Customização da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Cards de Pergunta (Fase 1) */
    .question-card {
        background-color: #ffffff;
        border: 1px solid #eeeeee;
        padding: 25px;
        border-radius: 4px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .question-card:hover {
        border-color: #000000;
    }

    /* Botões Padrão Bruno Hohl */
    div.stButton > button:first-child {
        background-color: #000000;
        color: white;
        border-radius: 2px;
        border: 1px solid #000000;
        padding: 0.6rem 2rem;
        font-weight: 300;
        letter-spacing: 1px;
        text-transform: uppercase;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #333333;
        border-color: #333333;
        color: white;
    }

    /* Métricas do Dashboard */
    div[data-testid="stMetric"] {
        border-left: 3px solid #000000;
        background-color: #F9F9F9;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS (PERGUNTAS)
# ==========================================
# Mantendo o banco de dados robusto criado anteriormente
perguntas_fase1 = [
    {"id": 1, "tag_A": "E1", "tag_B": "L5", "frase_A": "Preciso ter previsibilidade financeira e controle detalhado sobre os processos antes de dar qualquer passo.", "frase_B": "Prefiro agir alinhado ao meu propósito, confiando que os resultados virão se eu for autêntico."},
    {"id": 2, "tag_A": "E2", "tag_B": "L5", "frase_A": "Adapto minha postura para garantir que todos fiquem confortáveis e o clima permaneça pacífico.", "frase_B": "Expresso minha visão de forma transparente, mesmo que isso gere algum desconforto momentâneo."},
    {"id": 3, "tag_A": "E3", "tag_B": "L4", "frase_A": "Foco em garantir que minhas entregas sejam impecáveis, à prova de críticas e falhas.", "frase_B": "Prefiro testar novas abordagens e aprender na prática, mesmo sabendo que posso errar."},
    {"id": 4, "tag_A": "E1", "tag_B": "L6", "frase_A": "Minha prioridade agora é organizar e proteger minhas finanças, garantindo que eu não passe por imprevistos.", "frase_B": "Minha prioridade agora é investir tempo em parcerias, pois acredito que o trabalho em conjunto traz os melhores resultados."},
    {"id": 5, "tag_A": "E2", "tag_B": "L7", "frase_A": "Valorizo profundamente ser reconhecido e aceito pelas pessoas com as quais convivo diariamente.", "frase_B": "Meu foco está em tomar decisões que beneficiarão as próximas gerações, independente de quem me aprove hoje."},
    {"id": 6, "tag_A": "L1", "tag_B": "L2", "frase_A": "Dedico minha energia a maximizar meus ganhos e construir um patrimônio sólido.", "frase_B": "Dedico minha energia a nutrir conexões profundas e construir um círculo de confiança ao meu redor."},
    {"id": 7, "tag_A": "L3", "tag_B": "L2", "frase_A": "Atingir metas desafiadoras e entregar alta performance é o que mais me motiva diariamente.", "frase_B": "Garantir que a equipe ou minha família trabalhe em total harmonia e colaboração é o que mais me motiva."},
    {"id": 8, "tag_A": "L1", "tag_B": "L3", "frase_A": "Prefiro a garantia de uma renda estável e um ambiente de trabalho sem grandes riscos.", "frase_B": "Prefiro assumir riscos se isso me colocar em uma posição de destaque e excelência profissional."},
    {"id": 9, "tag_A": "L3", "tag_B": "L4", "frase_A": "Busco ser o melhor naquilo que já faço, otimizando minhas habilidades atuais.", "frase_B": "Busco me reinventar completamente, aprendendo coisas que me tiram da minha zona de especialidade."},
    {"id": 10, "tag_A": "L1", "tag_B": "L4", "frase_A": "Confio em métodos comprovados que garantem estabilidade e continuidade.", "frase_B": "Gosto de questionar o status quo e buscar formas disruptivas de resolver problemas."},
    {"id": 11, "tag_A": "L2", "tag_B": "L4", "frase_A": "Sinto-me realizado quando faço parte de um grupo coeso que compartilha as mesmas rotinas.", "frase_B": "Sinto-me realizado quando tenho total autonomia para explorar novos caminhos e ideias."},
    {"id": 12, "tag_A": "L5", "tag_B": "L6", "frase_A": "Meu foco principal é encontrar um profundo alinhamento interno entre o que eu faço e os meus valores.", "frase_B": "Meu foco principal é construir alianças estratégicas no mundo externo para resolver problemas complexos."},
    {"id": 13, "tag_A": "L6", "tag_B": "L7", "frase_A": "Realizo-me atuando como mentor, ajudando pessoas próximas ou parceiros a atingirem seu potencial.", "frase_B": "Realizo-me atuando em causas maiores, dedicando minha energia ao serviço da sociedade."},
    {"id": 14, "tag_A": "L3", "tag_B": "L5", "frase_A": "O sucesso é medido pelo alcance de metas concretas e pelo reconhecimento da excelência do trabalho entregue.", "frase_B": "O sucesso é medido pela profunda coerência entre as minhas escolhas diárias e os meus valores mais essenciais."},
    {"id": 15, "tag_A": "L1", "tag_B": "L7", "frase_A": "Trabalho duro para construir uma base financeira que garanta tranquilidade para mim e minha família.", "frase_B": "Trabalho duro para deixar uma marca positiva no mundo, muito além do meu círculo familiar."},
    {"id": 16, "tag_A": "L2", "tag_B": "L5", "frase_A": "Valorizo muito manter um ambiente agradável e me adaptar para atender às necessidades das pessoas.", "frase_B": "Valorizo muito ser fiel ao que acredito, mesmo que isso signifique discordar do grupo."},
    {"id": 17, "tag_A": "L3", "tag_B": "L6", "frase_A": "Sinto que o progresso real vem de focar em superar meus próprios limites e alcançar a excelência.", "frase_B": "Sinto que o progresso real vem de atuar como um facilitador e criar oportunidades para o grupo."},
    {"id": 18, "tag_A": "L4", "tag_B": "L7", "frase_A": "Invisto a maior parte da minha energia em aprender coisas novas e aprimorar minhas próprias habilidades.", "frase_B": "Invisto a maior parte da minha energia em causas que possam gerar um benefício duradouro para a sociedade."},
    {"id": 19, "tag_A": "E3", "tag_B": "L5", "frase_A": "Para mim, é fundamental construir uma imagem profissional forte e ser reconhecido como autoridade.", "frase_B": "Para mim, é fundamental sentir que meu trabalho tem um significado real, independente do reconhecimento."},
    {"id": 20, "tag_A": "E1", "tag_B": "L2", "frase_A": "Prefiro poupar e acumular recursos financeiros como uma reserva de segurança rigorosa para o meu futuro.", "frase_B": "Prefiro utilizar parte dos meus recursos financeiros para fortalecer laços com as pessoas importantes."},
    {"id": 21, "tag_A": "L4", "tag_B": "L6", "frase_A": "Sinto-me mais motivado quando estou resolvendo problemas complexos e descobrindo formas inteligentes de trabalhar.", "frase_B": "Sinto-me mais motivado quando estou desenvolvendo soluções em parceria para gerar impacto positivo."}
]

cenarios_fase2 = {
    "N1": "Fundações Fortes",
    "N2": "Conexões Profundas",
    "N3": "Alta Performance",
    "N4": "Liberdade e Reinvenção",
    "N5": "Autenticidade e Significado",
    "N6": "Mentoria e Alianças",
    "N7": "Legado e Serviço"
}

escala_opcoes = ["Totalmente A", "Muito A", "Levemente A", "Levemente B", "Muito B", "Totalmente B"]
pontos_A = [5, 4, 3, 2, 1, 0]
pontos_B = [0, 1, 2, 3, 4, 5]

# ==========================================
# 3. GESTÃO DE ESTADO
# ==========================================
if 'etapa' not in st.session_state: st.session_state.etapa = 0
if 'respostas_fase1' not in st.session_state: st.session_state.respostas_fase1 = {}
if 'respostas_fase2' not in st.session_state: st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}
if 'dados_cliente' not in st.session_state: st.session_state.dados_cliente = {"nome": "", "email": ""}

def avancar(): st.session_state.etapa += 1
def reiniciar():
    st.session_state.etapa = 0
    st.session_state.respostas_fase1 = {}
    st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}
    st.session_state.dados_cliente = {"nome": "", "email": ""}

# ==========================================
# 4. FUNÇÃO DE SALVAMENTO (DIRETO GSPREAD)
# ==========================================
def salvar_dados_gsheets(nome, email, scores, moedas, indices):
    try:
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        if "private_key" in secrets_dict:
            secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")

        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url).sheet1
        
        nova_linha = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome, email, f"{indices['ep']:.1f}%", f"{indices['ps']:.0f}%",
            f"{indices['cf']:.2f}", indices['maior_medo'], str(indices['zeros']), str(indices['top3'])
        ]
        sheet.append_row(nova_linha)
        return True
    except Exception:
        traceback.print_exc()
        return False

# ==========================================
# 5. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>BRUNO HOHL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Diagnóstico de Consciência</p>", unsafe_allow_html=True)
    st.divider()
    
    if st.session_state.etapa > 0:
        st.write(f"👤 **Cliente:** {st.session_state.dados_cliente['nome']}")
        st.write(f"📧 **Email:** {st.session_state.dados_cliente['email']}")
        st.divider()
        if st.button("Reiniciar Teste"):
            reiniciar()
            st.rerun()

# ==========================================
# 6. INTERFACE PRINCIPAL
# ==========================================

# --- TELA 0: CADASTRO ---
if st.session_state.etapa == 0:
    st.markdown("<h1 style='text-align: center;'>RADIOGRAFIA DO MOMENTO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #555;'>Mapeamento de Fluxo e Potencial de Crescimento</p>", unsafe_allow_html=True)
    
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("cadastro"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail Profissional")
            submit = st.form_submit_button("COMEÇAR DIAGNÓSTICO")
            if submit:
                if nome and email:
                    st.session_state.dados_cliente = {"nome": nome, "email": email}
                    avancar()
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos para prosseguir.")

# --- TELA 1: FASE 1 (TENSÕES) ---
elif st.session_state.etapa == 1:
    st.markdown("<h2>Fase 1: Inventário de Tensões</h2>", unsafe_allow_html=True)
    st.write("Selecione a posição que melhor descreve sua **vida real hoje**.")
    st.progress(0.33)
    st.divider()

    for p in perguntas_fase1:
        with st.container():
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"**Questão {p['id']} de 21**")
            
            c1, c2 = st.columns([1, 1])
            with c1: st.caption(f"Opção A: {p['frase_A']}")
            with c2: st.caption(f"Opção B: {p['frase_B']}")
            
            st.select_slider(
                label=f"q_{p['id']}",
                options=escala_opcoes,
                value="Levemente A",
                label_visibility="collapsed",
                key=f"q_{p['id']}"
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("PROSSEGUIR PARA FASE 2"):
        # Salva as respostas
        for p in perguntas_fase1:
            st.session_state.respostas_fase1[p['id']] = st.session_state[f"q_{p['id']}"]
        avancar()
        st.rerun()

# --- TELA 2: FASE 2 (MOEDAS) ---
elif st.session_state.etapa == 2:
    st.markdown("<h2>Fase 2: Vetor de Crescimento</h2>", unsafe_allow_html=True)
    st.write("A Regra da Renúncia: Distribua **10 fichas** e deixe pelo menos **3 áreas zeradas**.")
    st.progress(0.66)
    
    # KPIs dinâmicos
    total_usado = sum(st.session_state.respostas_fase2.values())
    restantes = 10 - total_usado
    zeros = sum(1 for v in st.session_state.respostas_fase2.values() if v == 0)
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Fichas Disponíveis", restantes)
    col_kpi2.metric("Áreas com Zero", f"{zeros}/3")
    
    st.divider()
    
    for k, v in cenarios_fase2.items():
        st.session_state.respostas_fase2[k] = st.number_input(f"{v}", 0, 10, st.session_state.respostas_fase2[k], key=f"f2_{k}")
    
    st.write("")
    if restantes == 0 and zeros >= 3:
        if st.button("FINALIZAR E GERAR RELATÓRIO"):
            avancar()
            st.rerun()
    else:
        st.button("DISTRIBUIÇÃO INVÁLIDA", disabled=True)

# --- TELA 3: DASHBOARD (VISÃO DO COACH) ---
elif st.session_state.etapa == 3:
    # (O processamento dos cálculos permanece idêntico ao anterior para garantir acurácia)
    # ... código de cálculo ...
    
    # Processamento
    scores = {"L1":0, "L2":0, "L3":0, "L4":0, "L5":0, "L6":0, "L7":0, "E1":0, "E2":0, "E3":0}
    for p in perguntas_fase1:
        resp = st.session_state.respostas_fase1[p['id']]
        idx = escala_opcoes.index(resp)
        scores[p['tag_A']] += pontos_A[idx]
        scores[p['tag_B']] += pontos_B[idx]

    i_ep = ((scores['E1'] + scores['E2'] + scores['E3']) / 105) * 100
    moedas = st.session_state.respostas_fase2
    i_ps = ((moedas['N4'] + moedas['N5'] + moedas['N6'] + moedas['N7']) / 10) * 100
    avg_base = (scores['L1'] + scores['L2'] + scores['L3']) / 3
    avg_topo = (moedas['N5'] + moedas['N6'] + moedas['N7']) / 3
    i_cf = avg_base / (avg_topo * 10.5) if avg_topo > 0 else 99.9

    # Dashboard Master View
    st.markdown("<h1 style='text-align: center;'>MASTER ANALYSIS VIEW</h1>", unsafe_allow_html=True)
    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("ENTROPIA (Shadow)", f"{i_ep:.1f}%")
    c2.metric("PRONTIDÃO (Jump)", f"{i_ps:.0f}%")
    c3.metric("SUSTENTABILIDADE", f"{i_cf:.2f}")

    st.write("")
    
    # Gráfico Ampulheta
    fator = 3.5
    levels = ['N7', 'N6', 'N5', 'N4', 'N3', 'N2', 'N1']
    v_atual = [scores['L7'], scores['L6'], scores['L5'], scores['L4'], scores['L3'], scores['L2'], scores['L1']]
    v_fut = [moedas['N7']*fator, moedas['N6']*fator, moedas['N5']*fator, moedas['N4']*fator, moedas['N3']*fator, moedas['N2']*fator, moedas['N1']*fator]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=levels, x=v_atual, name='Realidade', orientation='h', marker_color='#000'))
    fig.add_trace(go.Bar(y=levels, x=v_fut, name='Desejo', orientation='h', marker_color='#27AE60'))
    fig.update_layout(barmode='group', height=450, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    # Botão Salvar no Final
    st.divider()
    if st.button("SALVAR RESULTADOS NA NUVEM"):
        with st.spinner("Sincronizando..."):
            res = salvar_dados_gsheets(
                st.session_state.dados_cliente['nome'],
                st.session_state.dados_cliente['email'],
                scores, moedas, {"ep": i_ep, "ps": i_ps, "cf": i_cf, "maior_medo": "N/A", "zeros": "N/A", "top3": "N/A"}
            )
            if res: st.success("Sincronizado com Sucesso.")
