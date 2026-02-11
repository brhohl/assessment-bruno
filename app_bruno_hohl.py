import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

# ==========================================
# 1. CONFIGURAÇÃO VISUAL (UI/UX)
# ==========================================
st.set_page_config(
    page_title="Assessment | Bruno Hohl", 
    layout="wide", 
    page_icon="🧭",
    initial_sidebar_state="expanded"
)

# CSS Customizado para visual "Enterprise"
st.markdown("""
<style>
    /* Esconde menu padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Títulos e Cores */
    h1, h2, h3 {
        color: #0f2c45; /* Azul Profundo */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Botões Primários */
    div.stButton > button:first-child {
        background-color: #0f2c45;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #1a4b75;
        color: white;
    }
    
    /* Ajuste de Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
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

cenarios_fase2 = {
    "N1": "Fundações Fortes (N1)",
    "N2": "Conexões Profundas (N2)",
    "N3": "Alta Performance (N3)",
    "N4": "Liberdade e Reinvenção (N4)",
    "N5": "Autenticidade e Significado (N5)",
    "N6": "Mentoria e Alianças (N6)",
    "N7": "Legado e Serviço (N7)"
}

escala_opcoes = ["Totalmente A", "Muito A", "Levemente A", "Levemente B", "Muito B", "Totalmente B"]
pontos_A = [5, 4, 3, 2, 1, 0]
pontos_B = [0, 1, 2, 3, 4, 5]

# ==========================================
# 3. GESTÃO DE ESTADO (SESSION STATE)
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
# 4. FUNÇÃO DE SALVAMENTO (GOOGLE SHEETS)
# ==========================================
def salvar_dados_gsheets(nome, email, scores, moedas, indices):
    try:
        # Carrega Segredos
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        if "private_key" in secrets_dict:
            secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")

        # Autenticação
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Conexão
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url).sheet1
        
        # Dados
        nova_linha = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome,
            email,
            f"{indices['ep']:.1f}%",
            f"{indices['ps']:.0f}%",
            f"{indices['cf']:.2f}",
            indices['maior_medo'],
            str(indices['zeros']),
            str(indices['top3'])
        ]
        
        sheet.append_row(nova_linha)
        return True
        
    except Exception:
        # Log silencioso ou print no console para debug
        traceback.print_exc()
        return False

# ==========================================
# 5. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1903/1903902.png", width=50) # Placeholder Logo
    st.markdown("### Método Bruno Hohl")
    st.divider()
    
    if st.session_state.etapa > 0:
        st.write(f"👤 **Cliente:** {st.session_state.dados_cliente['nome']}")
        
        # Barra de Progresso Geral
        progresso_geral = 0
        if st.session_state.etapa == 1: progresso_geral = 33
        elif st.session_state.etapa == 2: progresso_geral = 66
        elif st.session_state.etapa == 3: progresso_geral = 100
        
        st.write("Progresso:")
        st.progress(progresso_geral)
    else:
        st.info("Bem-vindo ao diagnóstico de consciência.")

# ==========================================
# 6. INTERFACE PRINCIPAL
# ==========================================

# --- TELA 0: LOGIN ---
if st.session_state.etapa == 0:
    st.title("🧭 Radiografia do Momento")
    st.markdown("""
    Este diagnóstico mapeia onde sua energia mental e emocional está alocada hoje e identifica
    os vetores de crescimento para o seu próximo ciclo.
    
    * **Tempo estimado:** 8 minutos
    * **Confidencialidade:** Seus dados são restritos ao seu Coach.
    """)
    
    with st.container():
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("") # Espaço
        with c2:
            with st.form("login_form"):
                nome = st.text_input("Nome Completo")
                email = st.text_input("E-mail")
                submitted = st.form_submit_button("Iniciar Sessão ➤", type="primary")
                
                if submitted:
                    if nome and email:
                        st.session_state.dados_cliente = {"nome": nome, "email": email}
                        avancar()
                        st.rerun()
                    else:
                        st.error("Por favor, preencha todos os campos.")

# --- TELA 1: FASE 1 ---
elif st.session_state.etapa == 1:
    st.subheader("Fase 1: Inventário de Tensões")
    st.markdown("Mova o seletor para o lado que melhor representa sua **realidade atual** (não o que você gostaria que fosse).")
    st.divider()
    
    todas_respondidas = True
    
    # Loop de Perguntas com Layout Melhorado
    for p in perguntas_fase1:
        st.markdown(f"**Questão {p['id']}**")
        
        # Colunas para as frases (Mobile Friendly)
        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.info(p['frase_A'])
        with col_dir:
            st.success(p['frase_B'])
            
        # Slider Centralizado
        val = st.select_slider(
            label=f"q_{p['id']}",
            options=escala_opcoes,
            value=st.session_state.respostas_fase1.get(p['id'], "Levemente A"), # Default neutro visual
            label_visibility="collapsed",
            key=f"slider_{p['id']}"
        )
        st.session_state.respostas_fase1[p['id']] = val
        st.markdown("---")

    if st.button("Salvar e Avançar para Fase 2 ➤", type="primary"):
        avancar()
        st.rerun()

# --- TELA 2: FASE 2 ---
elif st.session_state.etapa == 2:
    st.subheader("Fase 2: Vetor de Crescimento")
    st.markdown("""
    Você tem **10 Fichas de Energia** para investir nos próximos 2 anos.
    
    ⚠️ **Regra da Renúncia:** Para avançar, você deve deixar **pelo menos 3 cenários com ZERO fichas**.
    """)
    st.divider()
    
    # Controle de Moedas (Sticky Header Simulada)
    total_usado = sum(st.session_state.respostas_fase2.values())
    restantes = 10 - total_usado
    zeros = sum(1 for v in st.session_state.respostas_fase2.values() if v == 0)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Fichas Totais", "10")
    kpi2.metric("Disponíveis", f"{restantes}", delta_color="normal" if restantes == 0 else "inverse")
    kpi3.metric("Renúncias (Zeros)", f"{zeros}/3", delta_color="normal" if zeros >=3 else "inverse")
    
    st.markdown("### Distribua suas fichas:")
    
    # Inputs
    for k, desc in cenarios_fase2.items():
        val = st.number_input(
            f"{desc}", 
            min_value=0, 
            max_value=10, 
            value=st.session_state.respostas_fase2[k],
            key=f"num_{k}"
        )
        st.session_state.respostas_fase2[k] = val

    st.markdown("---")
    
    # Validação
    valido = (restantes == 0) and (zeros >= 3)
    
    if valido:
        st.success("✅ Distribuição válida!")
        if st.button("Gerar Análise Final ➤", type="primary"):
            avancar()
            st.rerun()
    else:
        st.warning(f"Ajuste pendente: Fichas sobrando ({restantes}) ou Zeros insuficientes ({zeros}).")

# --- TELA 3: DASHBOARD ---
elif st.session_state.etapa == 3:
    # Cálculos (Engine)
    scores = {"L1":0, "L2":0, "L3":0, "L4":0, "L5":0, "L6":0, "L7":0, "E1":0, "E2":0, "E3":0}
    for p in perguntas_fase1:
        if p['id'] in st.session_state.respostas_fase1:
            idx = escala_opcoes.index(st.session_state.respostas_fase1[p['id']])
            scores[p['tag_A']] += pontos_A[idx]
            scores[p['tag_B']] += pontos_B[idx]

    total_fase1 = 105
    soma_entropia = scores['E1'] + scores['E2'] + scores['E3']
    i_ep = (soma_entropia / total_fase1) * 100
    
    moedas = st.session_state.respostas_fase2
    i_ps = ((moedas['N4'] + moedas['N5'] + moedas['N6'] + moedas['N7']) / 10) * 100
    
    avg_base = (scores['L1'] + scores['L2'] + scores['L3']) / 3
    avg_topo = (moedas['N5'] + moedas['N6'] + moedas['N7']) / 3
    denominador = (avg_topo * 10.5)
    i_cf = avg_base / denominador if denominador > 0 else 99.9

    # Textos Dinâmicos
    txt_ep = "Fluxo Livre" if i_ep <= 10 else "Alerta de Atrito" if i_ep <= 25 else "Bloqueio Crítico"
    txt_ps = "Manutenção" if i_ps <= 20 else "Evolução Gradual" if i_ps <= 40 else "Virada de Chave"
    if i_cf < 0.7: txt_cf = "Frágil (Voo de Ícaro)"
    elif i_cf <= 1.2: txt_cf = "Sustentável (Fluxo)"
    else: txt_cf = "Fixação (Gaiola de Ouro)"
    
    max_ent = max(scores['E1'], scores['E2'], scores['E3'])
    if max_ent == scores['E1']: msg_ent = "Controle & Escassez"
    elif max_ent == scores['E2']: msg_ent = "Rejeição & Conflito"
    else: msg_ent = "Status & Fracasso"

    # Layout do Dashboard
    st.subheader(f"Dashboard Executivo: {st.session_state.dados_cliente['nome']}")
    st.caption("Visão exclusiva do Coach")
    st.markdown("---")

    # 1. KPIs Principais
    col1, col2, col3 = st.columns(3)
    col1.metric("Entropia (Medo)", f"{i_ep:.1f}%", txt_ep, delta_color="inverse")
    col2.metric("Prontidão (Mudança)", f"{i_ps:.0f}%", txt_ps)
    col3.metric("Sustentabilidade", f"{i_cf:.2f}", txt_cf)
    
    st.markdown("---")

    # 2. Gráficos (Visual Clean)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("#### ⏳ Ampulheta de Energia")
        fator = 3.5
        levels = ['N7 Serviço', 'N6 Colaboração', 'N5 Alinhamento', 'N4 Evolução', 'N3 Performance', 'N2 Relação', 'N1 Viabilidade']
        v_atual = [scores['L7'], scores['L6'], scores['L5'], scores['L4'], scores['L3'], scores['L2'], scores['L1']]
        v_futuro = [moedas['N7']*fator, moedas['N6']*fator, moedas['N5']*fator, moedas['N4']*fator, moedas['N3']*fator, moedas['N2']*fator, moedas['N1']*fator]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=levels, x=v_atual, name='Atual (L)', orientation='h',
            marker_color='#2E86C1', opacity=0.8
        ))
        fig.add_trace(go.Bar(
            y=levels, x=v_futuro, name='Futuro (Desejo)', orientation='h',
            marker_color='#27AE60', opacity=0.8
        ))
        fig.update_layout(
            barmode='group', 
            height=400, 
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### 🌪️ Gatilho de Bloqueio")
        st.error(f"**{msg_ent}**")
        st.caption("Onde a energia está sendo drenada hoje.")
        
        df_ent = pd.DataFrame({
            'r': [scores['E1'], scores['E2'], scores['E3'], scores['E1']],
            'theta': ['Controle', 'Aprovação', 'Status', 'Controle']
        })
        fig_radar = px.line_polar(df_ent, r='r', theta='theta', line_close=True)
        fig_radar.update_traces(fill='toself', line_color='#E74C3C')
        fig_radar.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 3. Insights Finais
    st.markdown("---")
    col_ins1, col_ins2 = st.columns(2)
    
    top_apostas = sorted(moedas.items(), key=lambda x: x[1], reverse=True)[:3]
    top_txt = [f"{cenarios_fase2[k].split('(')[0]} ({v})" for k, v in top_apostas]
    zeros_txt = [cenarios_fase2[k].split('(')[0] for k, v in moedas.items() if v == 0]

    with col_ins1:
        st.info(f"**Apostas Principais:** {', '.join(top_txt)}")
    with col_ins2:
        st.warning(f"**Renúncias Conscientes:** {', '.join(zeros_txt)}")

    # Botão Salvar
    st.markdown("### 💾 Registro")
    if st.button("Salvar na Base de Dados e Finalizar", type="primary"):
        with st.spinner("Conectando ao servidor..."):
            indices_save = {
                "ep": i_ep, "ps": i_ps, "cf": i_cf,
                "maior_medo": msg_ent,
                "zeros": zeros_txt,
                "top3": top_txt
            }
            ok = salvar_dados_gsheets(
                st.session_state.dados_cliente['nome'],
                st.session_state.dados_cliente['email'],
                scores,
                moedas,
                indices_save
            )
            if ok:
                st.toast("Sucesso! Dados salvos na nuvem.", icon="☁️")
                st.success("Sessão finalizada com sucesso.")
            else:
                st.error("Erro ao salvar. Verifique a conexão.")

    if st.button("🔄 Iniciar Novo Cliente"):
        reiniciar()
        st.rerun()
