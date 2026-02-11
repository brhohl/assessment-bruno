import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Bruno Hohl | Assessment", layout="wide", page_icon="🧭")

# Estilização CSS para dar ar "Premium"
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 20px; text-align: center;}
    .stProgress > div > div > div > div { background-color: #2E86C1; }
    h1, h2, h3 { color: #154360; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS COMPLETO (PERGUNTAS E CENÁRIOS)
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
# GESTÃO DE ESTADO
# ==========================================
if 'etapa' not in st.session_state:
    st.session_state.etapa = 0
if 'respostas_fase1' not in st.session_state:
    st.session_state.respostas_fase1 = {}
if 'respostas_fase2' not in st.session_state:
    st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}
if 'dados_cliente' not in st.session_state:
    st.session_state.dados_cliente = {"nome": "", "email": ""}

def avancar():
    st.session_state.etapa += 1

def reiniciar():
    st.session_state.etapa = 0
    st.session_state.respostas_fase1 = {}
    st.session_state.respostas_fase2 = {k: 0 for k in cenarios_fase2.keys()}
    st.session_state.dados_cliente = {"nome": "", "email": ""}

# ==========================================
# FUNÇÃO DE SALVAMENTO (MODO DIRETO / GSPREAD)
# ==========================================
def salvar_dados(nome, email, scores, moedas, indices):
    try:
        # 1. Carrega as credenciais direto dos segredos
        # O Streamlit já tem isso salvo, só precisamos formatar para o Google aceitar
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        
        # Correção de segurança para a chave privada (caso tenha vindo com quebras de linha escapadas)
        if "private_key" in secrets_dict:
            secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")

        # 2. Define as permissões (Escopos)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # 3. Autentica com o Google
        creds = Credentials.from_service_account_info(secrets_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # 4. Abre a planilha e seleciona a primeira aba
        url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url_planilha).sheet1
        
        # 5. Prepara a linha de dados
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
        
        # 6. Adiciona no final (Append)
        sheet.append_row(nova_linha)
        return True
        
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")
        return False
# ==========================================
# TELA 0: CADASTRO
# ==========================================
if st.session_state.etapa == 0:
    st.title("🧭 Assessment de Consciência | Método Bruno Hohl")
    st.markdown("### Bem-vindo à Radiografia do Momento")
    st.info("Este sistema mapeia onde sua energia reside hoje e para onde ela pede para ir. O processo leva cerca de 8 minutos.")
    
    with st.form("cadastro"):
        st.markdown("**Identifique-se para iniciar:**")
        nome = st.text_input("Seu Nome Completo")
        email = st.text_input("Seu E-mail")
        submitted = st.form_submit_button("Iniciar Diagnóstico", type="primary")
        
        if submitted:
            if nome and email:
                st.session_state.dados_cliente = {"nome": nome, "email": email}
                avancar()
                st.rerun()
            else:
                st.warning("Por favor, preencha nome e e-mail.")

# ==========================================
# TELA 1: FASE 1 (TENSÕES)
# ==========================================
elif st.session_state.etapa == 1:
    st.title("Fase 1: Inventário de Tensões")
    st.progress(33)
    st.write(f"Olá, **{st.session_state.dados_cliente['nome']}**. Mova o seletor em direção à frase que melhor descreve sua vida **hoje**.")
    
    todas_respondidas = True
    
    for p in perguntas_fase1:
        st.markdown(f"**Item {p['id']}**")
        c1, c2 = st.columns(2)
        with c1: st.caption(p['frase_A'])
        with c2: st.caption(p['frase_B'], unsafe_allow_html=True) 
        
        # Slider
        resp = st.select_slider(
            f"Par {p['id']}", 
            options=escala_opcoes, 
            key=f"q_{p['id']}", 
            label_visibility="collapsed"
        )
        
        if resp is None: 
            todas_respondidas = False
        else: 
            st.session_state.respostas_fase1[p['id']] = resp
        st.divider()
        
    if st.button("Avançar para Fase 2", type="primary"):
        avancar()
        st.rerun()

# ==========================================
# TELA 2: FASE 2 (MOEDAS)
# ==========================================
elif st.session_state.etapa == 2:
    st.title("Fase 2: Vetor de Crescimento")
    st.progress(66)
    st.info("Você tem 10 Fichas de Energia para investir nos próximos 2 anos. **Regra:** Você deve deixar pelo menos 3 cenários com ZERO fichas.")
    
    # Inputs numéricos
    for k, v in cenarios_fase2.items():
        st.session_state.respostas_fase2[k] = st.number_input(f"{v}", 0, 10, st.session_state.respostas_fase2[k], key=k)

    # Validação em tempo real
    total = sum(st.session_state.respostas_fase2.values())
    restantes = 10 - total
    zeros = sum(1 for v in st.session_state.respostas_fase2.values() if v == 0)
    
    c_metrica1, c_metrica2 = st.columns(2)
    c_metrica1.metric("Fichas Disponíveis", restantes, delta_color="normal" if restantes == 0 else "inverse")
    c_metrica2.metric("Cenários Zerados (Mín 3)", zeros, delta_color="normal" if zeros >=3 else "inverse")

    if restantes == 0 and zeros >= 3:
        st.success("Configuração válida. Pronto para gerar a análise.")
        if st.button("Gerar Dashboard do Coach", type="primary"): 
            avancar()
            st.rerun()
    else:
        st.warning(f"Ajuste suas fichas. Faltam alocar: {restantes} | Zeros atuais: {zeros}")

# ==========================================
# TELA 3: DASHBOARD DO COACH (FINAL)
# ==========================================
elif st.session_state.etapa == 3:
    st.progress(100)
    
    # --- PROCESSAMENTO DOS DADOS ---
    scores = {"L1":0, "L2":0, "L3":0, "L4":0, "L5":0, "L6":0, "L7":0, "E1":0, "E2":0, "E3":0}
    for p in perguntas_fase1:
        if p['id'] in st.session_state.respostas_fase1:
            idx = escala_opcoes.index(st.session_state.respostas_fase1[p['id']])
            scores[p['tag_A']] += pontos_A[idx]
            scores[p['tag_B']] += pontos_B[idx]

    # Cálculo dos Índices
    total_fase1 = 105
    soma_entropia = scores['E1'] + scores['E2'] + scores['E3']
    i_ep = (soma_entropia / total_fase1) * 100
    
    moedas = st.session_state.respostas_fase2
    i_ps = ((moedas['N4'] + moedas['N5'] + moedas['N6'] + moedas['N7']) / 10) * 100
    
    avg_base = (scores['L1'] + scores['L2'] + scores['L3']) / 3
    avg_topo = (moedas['N5'] + moedas['N6'] + moedas['N7']) / 3
    denominador = (avg_topo * 10.5)
    i_cf = avg_base / denominador if denominador > 0 else 99.9

    # Diagnósticos de Texto
    txt_ep = "Fluxo Livre" if i_ep <= 10 else "Alerta de Atrito" if i_ep <= 25 else "Bloqueio Crítico"
    
    txt_ps = "Manutenção" if i_ps <= 20 else "Evolução Gradual" if i_ps <= 40 else "Virada de Chave"
    
    if i_cf < 0.7: txt_cf = "Frágil (Voo de Ícaro)"; help_cf = "Sonho alto, base fraca."
    elif i_cf <= 1.2: txt_cf = "Sustentável (Fluxo)"; help_cf = "Equilíbrio ideal."
    else: txt_cf = "Fixação (Gaiola de Ouro)"; help_cf = "Base pesada, pouco crescimento."
    
    # Maior Entropia
    max_ent = max(scores['E1'], scores['E2'], scores['E3'])
    if max_ent == scores['E1']: msg_ent = "E1: Controle/Escassez"
    elif max_ent == scores['E2']: msg_ent = "E2: Rejeição/Conflito"
    else: msg_ent = "E3: Status/Fracasso"

    # --- HEADER DO DASHBOARD ---
    st.markdown(f"## 🚁 Cockpit de Comando | {st.session_state.dados_cliente['nome']}")
    st.markdown("---")

    # 1. OS TRÊS ÍNDICES VITAIS
    col1, col2, col3 = st.columns(3)
    col1.metric("1. Entropia (Ruído)", f"{i_ep:.1f}%", txt_ep)
    col2.metric("2. Prontidão (Mudança)", f"{i_ps:.0f}%", txt_ps)
    col3.metric("3. Sustentabilidade", f"{i_cf:.2f}", txt_cf)

    st.markdown("---")

    # 2. A VISUALIZAÇÃO DA AMPULHETA
    c_chart1, c_chart2 = st.columns([2, 1])
    
    with c_chart1:
        st.subheader("⏳ A Forma da Consciência")
        st.caption("Comparativo: Realidade Atual (Azul) vs. Desejo Futuro (Verde)")
        
        fator_norm = 3.5 
        levels = ['N7 - Serviço', 'N6 - Colaboração', 'N5 - Alinhamento', 'N4 - Evolução', 'N3 - Performance', 'N2 - Relacionamento', 'N1 - Viabilidade']
        val_atual = [scores['L7'], scores['L6'], scores['L5'], scores['L4'], scores['L3'], scores['L2'], scores['L1']]
        val_futuro = [moedas['N7']*fator_norm, moedas['N6']*fator_norm, moedas['N5']*fator_norm, moedas['N4']*fator_norm, moedas['N3']*fator_norm, moedas['N2']*fator_norm, moedas['N1']*fator_norm]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(y=levels, x=val_atual, name='Atual', orientation='h', marker=dict(color='#2E86C1')))
        fig.add_trace(go.Bar(y=levels, x=val_futuro, name='Futuro', orientation='h', marker=dict(color='#27AE60')))
        fig.update_layout(barmode='group', height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c_chart2:
        st.subheader("🌪️ Radar de Medos")
        df_ent = pd.DataFrame({
            'r': [scores['E1'], scores['E2'], scores['E3'], scores['E1']],
            'theta': ['E1: Controle', 'E2: Aprovação', 'E3: Status', 'E1: Controle']
        })
        fig_radar = px.line_polar(df_ent, r='r', theta='theta', line_close=True)
        fig_radar.update_traces(fill='toself', line_color='red')
        fig_radar.update_layout(height=300)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.error(f"**Bloqueio Principal:** {msg_ent}")

    st.markdown("---")

    # 3. RENÚNCIAS E APOSTAS
    c_res1, c_res2 = st.columns(2)
    sorted_moedas = sorted(moedas.items(), key=lambda item: item[1], reverse=True)
    zeros_list = [cenarios_fase2[k] for k, v in moedas.items() if v == 0]
    top3_list = [f"{cenarios_fase2[k]} ({v})" for k, v in sorted_moedas[:3]]
    
    with c_res1:
        st.subheader("🚀 Top 3 Apostas")
        for item in top3_list:
            st.success(item)

    with c_res2:
        st.subheader("❌ As Renúncias")
        for z in zeros_list:
            st.warning(f"Abriu mão de: **{z}**")

    st.markdown("---")
    
    # 4. BOTÃO DE SALVAR
    st.subheader("📤 Finalizar Sessão")
    st.info("Envie os dados para a planilha do Coach para encerrar.")
    
    if st.button("💾 Salvar Dados e Encerrar", type="primary"):
        with st.spinner("Salvando na nuvem..."):
            indices_save = {
                "ep": i_ep, "ps": i_ps, "cf": i_cf,
                "maior_medo": msg_ent,
                "zeros": ", ".join(zeros_list),
                "top3": ", ".join(top3_list)
            }
            sucesso = salvar_dados(
                st.session_state.dados_cliente['nome'],
                st.session_state.dados_cliente['email'],
                scores,
                moedas,
                indices_save
            )
            
            if sucesso:
                st.success("✅ Dados salvos com sucesso!")
                st.balloons()
            
    if st.button("🔄 Reiniciar (Novo Cliente)"):
        reiniciar()
        st.rerun()
