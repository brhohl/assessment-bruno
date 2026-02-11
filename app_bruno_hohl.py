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
    /* Fundo Preto Total e Texto Branco */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Customizada */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #333333;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Cards de Pergunta */
    .question-card {
        background-color: #0a0a0a;
        border: 1px solid #222222;
        padding: 30px;
        border-radius: 8px;
        margin-bottom: 25px;
    }

    /* Botões Bruno Hohl (Laranja/Dourado) */
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
    div.stButton > button:hover {
        background-color: #FFA500;
        color: #000000;
        transform: scale(1.02);
    }

    /* Inputs e Métricas */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a;
        border: 1px solid #333333;
        padding: 20px !important;
        border-radius: 4px;
    }
    
    /* Labels dos Inputs */
    label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    .stMarkdown p { color: #CCCCCC; }
    h1, h2, h3 { color: #FFFFFF !important; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS (PERGUNTAS E CENÁRIOS)
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
    {"id": 21, "tag_A": "
