import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

# ==========================================
# 1. ESTÉTICA PREMIUM BRUNO HOHL (DARK MODE)
# ==========================================
st.set_page_config(page_title="Bruno Hohl | Assessment", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #333333; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Card de Questões */
    .question-card { 
        background-color: #0a0a0a; 
        border: 1px solid #222222; 
        padding: 30px; 
        border-radius: 8px; 
        margin-bottom: 25px; 
    }
    
    /* Botões Laranja/Preto */
    div.stButton > button:first-child { 
        background-color: #FF8000; 
        color: #000000; 
        border-radius: 0px; 
        border: none; 
        padding: 0.8rem 3rem; 
        font-weight: 700; 
        letter-spacing: 2px; 
        text-transform: uppercase; 
        width: 100%; 
        transition: 0.3s; 
    }
    div.stButton > button:hover { background-color: #FFA500; color: #000000; transform: scale(1.02); }
    
    /* Métricas e Inputs */
    div[data-testid="stMetric"] { background-color: #0a0a0a; border: 1px solid #333333; padding: 20px !important; border-radius: 4px; }
    label { color: #FFFFFF !important; font-weight: 400 !important; font-size: 1.1rem !important; line-height: 1.4 !important; }
    
    .stMarkdown p { color: #CCCCCC; }
    h1, h2, h3 { color: #FFFFFF !important; letter-spacing: -1px; }
    
    /* Estilo para as descrições da Fase 2 */
    .fase2-label {
        font-size: 1.1rem;
        color: #FFFFFF;
        margin-bottom: 10px;
        display: block;
        border-left: 3px solid #FF8000;
        padding-left: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS (CONTEÚDO)
# ==========================================
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

# DICIONÁRIO CORRIGIDO COM AS FRASES COMPLETAS
cenarios_fase2 = {
    "N1": "Construir uma base material e financeira inabalável, garantindo conforto, saúde física e total tranquilidade estrutural para mim e para o meu futuro, sem sobressaltos.",
    "N2": "Cultivar relacionamentos de alta qualidade, criando um círculo de confiança absoluta, apoio mútuo e harmonia com as pessoas que amo e com quem convivo.",
    "N3": "Atingir o nível máximo de excelência na minha área, superando metas desafiadoras e sendo amplamente reconhecido pela qualidade e impacto dos resultados que entrego.",
    "N4": "Ter total autonomia e liberdade para aprender coisas novas, inovar na forma de viver e me reinventar continuamente, rompendo com a rotina e o status quo.",
    "N5": "Viver de forma totalmente autêntica, alinhando minhas ações diárias aos meus valores mais profundos e sentindo que o meu trabalho reflete quem eu realmente sou.",
    "N6": "Atuar como um facilitador do sucesso alheio, construindo alianças poderosas, mentorando pessoas e criando ecossistemas onde todos ganham e crescem juntos.",
    "N7": "Dedicar minha energia a uma causa maior que eu mesmo, deixando uma marca positiva, ética e duradouro na sociedade para as próximas gerações."
}

escala_opcoes = ["Totalmente A", "Muito A", "Levemente A", "Levemente B", "Muito B", "Totalmente B"]
pontos_A, pontos_B = [5, 4, 3, 2, 1, 0], [0, 1, 2, 3, 4, 5]

# ==========================================
# 3. ESTADO E LÓGICA
# ==========================================
if 'etapa' not in st.session_state: st.session_state.etapa = 0
if 'respostas_fase1' not in st.session_state: st.session_state.respostas_fase1 = {}
if 'respostas_fase2' not in st.session_state: st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}
if 'dados_cliente' not in st.session_state: st.session_state.dados_cliente = {"nome": "", "email": ""}

def avancar(): st.session_state.etapa += 1
def reiniciar(): st.session_state.etapa = 0; st.session_state.respostas_fase1 = {}; st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}; st.session_state.dados_cliente = {"nome": "", "email": ""}

# ==========================================
# 4. SALVAMENTO (GSHEETS)
# ==========================================
def salvar_dados_gsheets(nome, email, scores, moedas, indices):
    try:
        sd = dict(st.secrets["connections"]["gsheets"])
        if "private_key" in sd: sd["private_key"] = sd["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(sd, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"]).sheet1
        nova_linha = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nome, email, f"{indices['ep']:.1f}%", f"{indices['ps']:.0f}%", f"{indices['cf']:.2f}", indices['maior_medo'], str(indices['zeros']), str(indices['top3'])]
        sheet.append_row(nova_linha)
        return True
    except Exception: traceback.print_exc(); return False

# ==========================================
# 5. INTERFACE
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color:#FF8000; font-size:24px;'>BRUNO HOHL</h1>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.etapa > 0:
        st.write(f"**CLIENTE:** {st.session_state.dados_cliente['nome']}")
        if st.button("REINICIAR"): reiniciar(); st.rerun()

# --- TELA 0: LOGIN ---
if st.session_state.etapa == 0:
    st.markdown("<h1 style='text-align: center;'>RADIOGRAFIA DO MOMENTO</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.form("login"):
            n, e = st.text_input("NOME COMPLETO"), st.text_input("E-MAIL")
            if st.form_submit_button("COMEÇAR"):
                if n and e: st.session_state.dados_cliente = {"nome": n, "email": e}; avancar(); st.rerun()

# --- TELA 1: FASE 1 (TENSÕES) ---
elif st.session_state.etapa == 1:
    st.markdown("<h2>FASE 1: INVENTÁRIO DE TENSÕES</h2>", unsafe_allow_html=True)
    st.progress(0.33)
    for p in perguntas_fase1:
        st.markdown(f"<div class='question-card'><b>ITEM {p['id']}</b>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        ca.caption(p['frase_A']); cb.caption(p['frase_B'])
        st.select_slider(" ", options=escala_opcoes, value="Levemente A", key=f"q_{p['id']}", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    if st.button("PRÓXIMA FASE"):
        for p in perguntas_fase1: st.session_state.respostas_fase1[p['id']] = st.session_state[f"q_{p['id']}"]
        avancar(); st.rerun()

# --- TELA 2: FASE 2 (VETOR) ---
elif st.session_state.etapa == 2:
    st.markdown("<h2>FASE 2: VETOR DE CRESCIMENTO</h2>", unsafe_allow_html=True)
    st.progress(0.66)
    
    tot = sum(st.session_state.respostas_fase2.values())
    z = sum(1 for v in st.session_state.respostas_fase2.values() if v == 0)
    
    # Barra Superior de Status
    c_met1, c_met2 = st.columns(2)
    c_met1.markdown(f"Fichas Disponíveis: <span style='color:#FF8000; font-size: 24px;'>**{10-tot}**</span>", unsafe_allow_html=True)
    c_met2.markdown(f"Áreas com Zero: <span style='color:#FF8000; font-size: 24px;'>**{z}/3**</span>", unsafe_allow_html=True)
    st.divider()

    # LOOP DA FASE 2 COM FRASES COMPLETAS
    for k, frase in cenarios_fase2.items():
        st.markdown(f"<span class='fase2-label'>**Cenário {k[1]}**<br>{frase}</span>", unsafe_allow_html=True)
        st.session_state.respostas_fase2[k] = st.number_input(
            "Quantidade de fichas:", 0, 10, st.session_state.respostas_fase2[k], key=f"f2_{k}", label_visibility="collapsed"
        )
        st.write("") # Espaçamento entre cenários

    if tot == 10 and z >= 3:
        if st.button("ANALISAR RESULTADOS"): avancar(); st.rerun()
    else:
        st.button("DISTRIBUIÇÃO PENDENTE", disabled=True)

# --- TELA 3: DASHBOARD ---
elif st.session_state.etapa == 3:
    sc = {"L1":0, "L2":0, "L3":0, "L4":0, "L5":0, "L6":0, "L7":0, "E1":0, "E2":0, "E3":0}
    for p in perguntas_fase1:
        idx = escala_opcoes.index(st.session_state.respostas_fase1[p['id']])
        sc[p['tag_A']] += pontos_A[idx]; sc[p['tag_B']] += pontos_B[idx]
    
    ep, m = (sum([sc['E1'],sc['E2'],sc['E3']])/105)*100, st.session_state.respostas_fase2
    ps = (sum([m['N4'],m['N5'],m['N6'],m['N7']])/10)*100
    
    base = sum([sc['L1'],sc['L2'],sc['L3']])/3
    topo = sum([m['N5'],m['N6'],m['N7']])/3
    cf = base / (topo * 10.5) if topo > 0 else 99.9
    
    st.markdown("<h2 style='text-align: center;'>MASTER ANALYSIS</h2>", unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    k1.metric("ENTROPIA", f"{ep:.1f}%"); k2.metric("PRONTIDÃO", f"{ps:.0f}%"); k3.metric("SUSTENTABILIDADE", f"{cf:.2f}")
    
    levels = ['N7', 'N6', 'N5', 'N4', 'N3', 'N2', 'N1']
    v_at = [sc['L7'], sc['L6'], sc['L5'], sc['L4'], sc['L3'], sc['L2'], sc['L1']]
    v_fu = [m['N7']*3.5, m['N6']*3.5, m['N5']*3.5, m['N4']*3.5, m['N3']*3.5, m['N2']*3.5, m['N1']*3.5]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=levels, x=v_at, name='REALIDADE ATUAL', orientation='h', marker_color='#333333'))
    fig.add_trace(go.Bar(y=levels, x=v_fu, name='DESEJO FUTURO', orientation='h', marker_color='#FF8000'))
    fig.update_layout(template='plotly_dark', barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("SALVAR E SINCRONIZAR"):
        t3 = ", ".join([f"N{k[1]} ({v})" for k,v in sorted(m.items(), key=lambda x:x[1], reverse=True)[:3]])
        z_tx = ", ".join([f"N{k[1]}" for k,v in m.items() if v == 0])
        if salvar_dados_gsheets(st.session_state.dados_cliente['nome'], st.session_state.dados_cliente['email'], sc, m, {"ep": ep, "ps": ps, "cf": cf, "maior_medo": "N/A", "zeros": z_tx, "top3": t3}):
            st.success("DADOS SINCRONIZADOS COM SUCESSO.")
