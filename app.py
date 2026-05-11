import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date, time
import urllib.parse

# --- 1. CONFIGURAÇÃO DA API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. LÓGICA DE NUMEROLOGIA ---
def calcular_numerologia(data):
    if not data: return 0
    numeros = data.strftime('%d%m%Y')
    soma = sum(int(n) for n in numeros)
    while soma > 9 and soma not in [11, 22]:
        soma = sum(int(n) for n in str(soma))
    return soma

# --- 3. LAYOUT E ESTÉTICA ---
st.set_page_config(page_title="Madame Janara v5.1", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2094&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(10, 8, 5, 0.98); padding: 30px; border-radius: 25px; border: 1px solid #d4af37; }
    .stButton>button { background: #d4af37 !important; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; height: 3.5em; transition: 0.3s; }
    .stButton>button:hover { background: #fff !important; box-shadow: 0 0 20px #d4af37; }
    .vip-section { border: 2px solid #ffd700; background: rgba(212, 175, 55, 0.1); padding: 25px; border-radius: 15px; margin-top: 20px; }
    .soulmate-section { border: 2px solid #ff4d4d; background: rgba(74, 26, 26, 0.3); padding: 25px; border-radius: 15px; margin-top: 20px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTÃO DE ESTADO ---
if 'analise' not in st.session_state:
    st.session_state.analise = {"resumo": "", "padrao": "", "vip": "", "soulmate": "", "feita": False}

# --- 5. MOTOR DE IA (VARREDURA INDESTRUTÍVEL) ---
def gerar_profecia(imagem, d, num_destino):
    # O SEGREDO DA RESILIÊNCIA: Buscar a lista real e testar
    modelos_para_testar = []
    try:
        todos_modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Coloca os modelos 'flash' no topo da fila
        flash_models = [m for m in todos_modelos if 'flash' in m]
        outros_modelos = [m for m in todos_modelos if 'flash' not in m]
        modelos_para_testar = flash_models + outros_modelos
    except:
        modelos_para_testar = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-pro"]

    prompt = f"""
    Aja como Madame Janara, a maior autoridade em Quiromancia, Astrologia e Numerologia.
    DADOS: {d['nome']}, Nasc: {d['data_nasc']} {d['horario']} em {d['cidade']}.
    SIGNO: {d['signo']} | NUMEROLOGIA: {num_destino}
    PARCEIRO: {d['p_nome']} (Signo: {d['p_signo']})

    Gere 4 partes separadas por '---'. NÃO use títulos como 'Bloco' ou 'Nível'.

    1 (TEASER): Resumo místico curto de 2 frases.
    ---
    2 (GRATUITO): Análise qualitativa cruzando as linhas da mão com o signo solar. Desenvolva um texto denso de pelo menos 15 linhas.
    ---
    3 (VIP): A Triangulação: Numerologia {num_destino}, Mapa Astral e Quiromancia. Desenvolva pelo menos 35 linhas focando em carreira, finanças e os próximos 12 meses.
    ---
    4 (SOULMATE): Sinastria mística entre {d['nome']} e {d['p_nome']}. Desenvolva pelo menos 35 linhas. Revele conexões de vidas passadas e dê conselhos práticos para o casal.
    """
    
    imagem.thumbnail((800, 800))
    config = genai.types.GenerationConfig(max_output_tokens=4000, temperature=0.8)
    
    erro_final = None
    # Loop de tentativas: testa modelo por modelo até dar certo
    for m_name in modelos_para_testar:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content([prompt, imagem], generation_config=config)
            return response.text
        except Exception as e:
            erro_final = e
            continue # Tenta o próximo silenciosamente
            
    raise Exception(f"Falha de comunicação com os astros. Detalhe técnico: {erro_final}")

# --- 6. INTERFACE ---
st.title("🔮 Oráculo Supremo de Madame Janara")

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome completo:", placeholder="O nome revela a vibração...")
        data_nasc = st.date_input("Nascimento:", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY")
        cidade = st.text_input("Cidade de Origem:", placeholder="Onde as estrelas o viram nascer?")
    with c2:
        signo = st.selectbox("Signo Solar:", ["Escolha...", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])
        horario = st.time_input("Hora do Nascimento:", value=None)
    
    num_exibido = calcular_numerologia(data_nasc) if data_nasc else "..."
    st.info(f"🔢 Vibração Numerológica: **{num_exibido}**")

    st.markdown("---")
    st.subheader("❤️ Conexão de Almas (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):")
    p_signo = st.selectbox("Signo dele(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])

    uploaded_file = st.file_uploader("Sua palma esquerda (clara e iluminada)...", type=["jpg", "jpeg", "png"])

    if st.button("🌟 INVOCAR O GRANDE ORÁCULO"):
        if uploaded_file and nome and data_nasc and signo != "Escolha...":
            with st.spinner("Madame Jan