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
st.set_page_config(page_title="Madame Janara v6.6", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2094&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(10, 8, 5, 0.98); padding: 30px; border-radius: 25px; border: 1px solid #d4af37; margin-bottom: 20px;}
    .tier-box { background: rgba(212, 175, 55, 0.05); padding: 25px; border-radius: 15px; border-left: 4px solid #d4af37; margin-top: 15px; }
    .soulmate-box { background: rgba(74, 26, 26, 0.2); padding: 25px; border-radius: 15px; border-left: 4px solid #ff4d4d; margin-top: 15px; }
    .stButton>button { background: linear-gradient(45deg, #d4af37, #aa8a2e) !important; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; height: 3.5em; transition: 0.3s; border: none; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; font-family: 'Playfair Display', serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTÃO DE ESTADO E CACHE ---
tiers = ['t1_gratis', 't2_mao', 't3_mapa', 't4_num', 't5_casal']
for t in tiers:
    if t not in st.session_state: st.session_state[t] = None
    if f"btn_{t}" not in st.session_state: st.session_state[f"btn_{t}"] = False

def unlock_t2(): st.session_state.btn_t2_mao = True
def unlock_t3(): st.session_state.btn_t3_mapa = True
def unlock_t4(): st.session_state.btn_t4_num = True
def unlock_t5(): st.session_state.btn_t5_casal = True

# O SEGREDO ESTÁ AQUI: Descobre o modelo disponível e guarda na memória por 1 hora
# Isso impede o erro 404 (porque usa o nome oficial) e impede o erro 429 (porque só consulta a lista 1 vez)
@st.cache_data(ttl=3600)
def descobrir_modelo_seguro():
    try:
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Tenta encontrar o Flash primeiro
        for m in modelos_disponiveis:
            if 'gemini-1.5-flash' in m:
                return m
        # Se não achar, tenta o Pro
        for m in modelos_disponiveis:
            if 'gemini-1.5-pro' in m:
                return m
        # Se falhar tudo, pega o primeiro que suportar geração e visão
        return modelos_disponiveis[0]
    except:
        return "gemini-1.5-flash" # Fallback extremo

# --- 5. MOTOR DE IA OTIMIZADO ---
def chamar_ia(prompt, imagem):
    try:
        nome_modelo = descobrir_modelo_seguro()
        model = genai.GenerativeModel(nome_modelo)
        config = genai.types.GenerationConfig(max_output_tokens=2048, temperature=0.85)
        imagem.thumbnail((800, 800))
        return model.generate_content([prompt, imagem], generation_config=config).text
    except Exception as e:
        if "429" in str(e) or "Quota" in str(e):
            raise Exception("As energias estão muito intensas! Aguarde 60 segundos para os astros se alinharem novamente.")
        else:
            raise Exception(f"Erro na comunicação com os astros. Detalhe técnico: {e} (Modelo tentado: {descobrir_modelo_seguro()})")

def gerar_t1(d, img):
    p = f"Aja como Madame Janara. DADOS: {d['nome']}, Signo: {d['signo']}, Numerologia: {d['num_d']}. Crie um resumo místico de 10 linhas cruzando a mão, astrologia e numerologia. Conclua com uma bênção curta."
    return chamar_ia(p, img)

def gerar_t2(d, img):
    p = f"Aja como Madame Janara. DADOS: {d['nome']}. Faça uma leitura profunda das linhas da Mão da foto. Mínimo de 25 linhas. Termine com uma bênção cigana."
    return chamar_ia(p, img)

def gerar_t3(d, img):
    p = f"Aja como Madame Janara. DADOS: {d['nome']}, Signo: {d['signo']}. Cruze o Mapa Astral com as linhas da Mão da foto. Mínimo de 30 linhas. Termine com uma bênção."
    return chamar_ia(p, img)

def gerar_t4(d, img):
    p = f"Aja como Madame Janara. DADOS: {d['nome']}, Numerologia: {d['num_d']}. Faça uma previsão de 12 meses cruzando a numerologia {d['num_d']} com a mão. Mínimo de 35 linhas focando em finanças. Finalize com bênção."
    return chamar_ia(p, img)

def gerar_t5(d, img):
    p = f"Aja como Madame Janara. DADOS: {d['nome']} ({d['signo']}, Num: {d['num_d']}). PARCEIRO: {d['p_nome']} ({d['p_signo']}, Num: {d['p_num']}). Faça A Sinastria de Almas profunda. Cruze astros, numerologia e linhas da mão. Mínimo de 40 linhas. Encerre perfeitamente com uma bênção para o casal."
    return chamar_ia(p, img)

# --- 6. INTERFACE ---
st.title("🔮 O Grande Oráculo de Madame Janara")

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Seu Nome:")
        data_nasc = st.date_input("Nascimento:", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with c2:
        signo = st.selectbox("Seu Signo:", ["Escolha...", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])
        horario = st.time_input("Hora de Nascimento (Opcional):", value=None)
    
    num_exibido = calcular_numerologia(data_nasc) if data_nasc else "..."
    st.info(f"🔢 Sua Vibração: **{num_exibido}**")

    st.markdown("---")
    st.subheader("❤️ Aprofundamento Amoroso (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):")
    c3, c4 = st.columns(2)
    with c3:
        p_data = st.date_input("Nasc. Parceiro(a):", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with c4:
        p_signo = st.selectbox("Signo dele(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])
    
    p_num = calcular_numerologia(p_data) if p_data else "..."

    uploaded_file = st.file_uploader("Sua palma esquerda (clara e iluminada)...", type=["jpg", "jpeg", "png"])

    if st.button("✨ DESPERTAR O ORÁCULO (Gratuito)"):
        if uploaded_file and nome and data_nasc and signo != "Escolha...":
            with st.spinner("Madame Janara tem os primeiros vislumbres..."):
                try:
                    img = Image.open(uploaded_file)
                    st.session_state.imagem_cache = img
                    d = {'nome': nome, 'data_nasc': data_nasc, 'signo': signo, 'num_d': num_exibido, 'p_nome': p_nome, 'p_data': p_data, 'p_signo': p_signo, 'p_num': p_num}
                    st.session_state.dados_cache = d
                    
                    st.session_state.t1_gratis = gerar_t1(d, img)
                except Exception as e:
                    st.error(f"{e}")
        else:
            st.warning("Preencha Nome, Data, Signo e envie a Foto.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. EXIBIÇÃO DA ESCADA DE VALOR ---
if st.session_state.t1_gratis:
    st.markdown("### ✨ O Despertar (Análise Básica)")
    st.info(st.session_state.t1_gratis)

    # TIER 2
    st.markdown("<div class='tier-box'>", unsafe_allow_html=True)
    st.subheader("1️⃣ Nível I: O Caminho das Mãos")
    st.write("Uma leitura profunda apenas de suas linhas (Vida, Cabeça e Coração).")
    if st.button("🔓 Desbloquear Leitura das Mãos", on_click=unlock_t2): pass
    if st.session_state.btn_t2_mao:
        if not st.session_state.t2_mao:
            with st.spinner("Lendo as linhas sagradas..."):
                try:
                    st.session_state.t2_mao = gerar_t2(st.session_state.dados_cache, st.session_state.imagem_cache)
                except Exception as e:
                    st.error(f"{e}")
        if st.session_state.t2_mao: st.write(st.session_state.t2_mao)
    st.markdown("</div>", unsafe_allow_html=True)

    # TIER 3
    if st.session_state.btn_t2_mao:
        st.markdown("<div class='tier-box'>", unsafe_allow_html=True)
        st.subheader("2️⃣ Nível II: O Mapa das Estrelas")
        st.write("O cruzamento sagrado entre o seu Mapa Astral detalhado e a Quiromancia.")
        if st.button("🔓 Desbloquear Mapa Astral + Mãos", on_click=unlock_t3): pass
        if st.session_state.btn_t3_mapa:
            if not st.session_state.t3_mapa:
                with st.spinner("Mapeando os astros..."):
                    try:
                        st.session_state.t3_mapa = gerar_t3(st.session_state.dados_cache, st.session_state.imagem_cache)
                    except Exception as e:
                        st.error(f"{e}")
            if st.session_state.t3_mapa: st.write(st.session_state.t3_mapa)
        st.markdown("</div>", unsafe_allow_html=True)

    # TIER 4
    if st.session_state.btn_t3_mapa:
        st.markdown("<div class='tier-box'>", unsafe_allow_html=True)
        st.subheader("3️⃣ Nível III: A Coroa do Destino")
        st.write("Inclui a vibração da sua Numerologia e revela os próximos 12 meses de carreira e finanças.")
        if st.button("💎 Desbloquear Previsão Completa VIP", on_click=unlock_t4): pass
        if st.session_state.btn_t4_num:
            if not st.session_state.t4_num:
                with st.spinner("Calculando o destino financeiro..."):
                    try:
                        st.session_state.t4_num = gerar_t4(st.session_state.dados_cache, st.session_state.imagem_cache)
                    except Exception as e:
                        st.error(f"{e}")
            if st.session_state.t4_num: st.write(st.session_state.t4_num)
        st.markdown("</div>", unsafe_allow_html=True)

    # TIER 5
    if st.session_state.btn_t4_num and p_nome and p_data:
        st.markdown("<div class='soulmate-box'>", unsafe_allow_html=True)
        st.subheader(f"🌹 Nível Master: A Fusão de Almas")
        st.write(f"A mais complexa de todas as leituras. Cruza astros, numerologia e karmas entre você e {p_nome}.")
        if st.button("💖 Desbloquear Sinastria Suprema", on_click=unlock_t5): pass
        if st.session_state.btn_t5_casal:
            if not st.session_state.t5_casal:
                with st.spinner("Conectando as duas almas..."):
                    try:
                        st.session_state.t5_casal = gerar_t5(st.session_state.dados_cache, st.session_state.imagem_cache)
                    except Exception as e:
                        st.error(f"{e}")
            if st.session_state.t5_casal:
                st.write(st.session_state.t5_casal)
                st.markdown("---")
                st.success("Ouça a sua profecia finalizada:")
                try:
                    tts = gTTS(text=st.session_state.t5_casal, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                except: pass
        st.markdown("</div>", unsafe_allow_html=True)