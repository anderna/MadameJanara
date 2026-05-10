import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date, time
import urllib.parse

# --- 1. CONFIGURAÇÃO SEGURA DA API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. LAYOUT E ESTÉTICA AVANÇADA ---
st.set_page_config(page_title="Madame Janara v4.0", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1502481851512-e9e2529bbbf9?q=80&w=2069&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(15, 10, 5, 0.95); padding: 25px; border-radius: 20px; border: 1px solid #d4af37; margin-bottom: 20px; }
    .stButton>button { background: #d4af37; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background: #fff; box-shadow: 0 0 20px #d4af37; }
    .vip-section { border: 2px solid #ffd700; background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 15px; margin-top: 20px; }
    .soulmate-section { border: 2px solid #ff4d4d; background: rgba(74, 26, 26, 0.3); padding: 20px; border-radius: 15px; margin-top: 20px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE INTELIGÊNCIA ---
def obter_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return next((m for m in modelos if 'gemini-1.5-flash' in m), modelos[0])
    except: return 'models/gemini-1.5-flash'

def gerar_profecia_completa(imagem, d):
    model = genai.GenerativeModel(obter_modelo())
    
    # Prompt ultra-específico para evitar erros de split
    prompt = f"""
    Aja como Madame Janara, uma cigana sábia e carismática. 
    DADOS: Nome: {d['nome']}, Nascimento: {d['data_nasc']} {d['horario']} em {d['cidade']}, Signo: {d['signo']}.
    DADOS PARCEIRO: Nome: {d['p_nome']}, Signo: {d['p_signo']}.

    Gere EXATAMENTE 4 blocos de texto, separando cada um pela sequência '---'.
    BLOCO 1: Teaser místico de 2 frases.
    ---
    BLOCO 2: Leitura das linhas da mão cruzada com o signo solar.
    ---
    BLOCO 3: Mapa Astral VIP. Fale de Ascendente, Lua e finanças para os próximos 12 meses.
    ---
    BLOCO 4: Sinastria Amorosa. Analise a compatibilidade entre {d['nome']} e {d['p_nome']}. Dê um segredo de vidas passadas.
    
    Use português do Brasil, tom detalhado e carismático.
    """
    
    imagem.thumbnail((800, 800))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- 4. INTERFACE ---
st.title("🔮 O Grande Oráculo de Madame Janara")

# Inicialização segura de Session State
for key in ['resumo', 'padrao', 'vip', 'soulmate', 'analise_feita']:
    if key not in st.session_state: st.session_state[key] = None

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Seu nome:", value="Anderson")
        data_nasc = st.date_input("Nascimento:", value=date(1981, 7, 28), format="DD/MM/YYYY")
        cidade = st.text_input("Cidade de Origem:", value="São Paulo, SP")
    with c2:
        signo = st.selectbox("Seu Signo:", ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], index=4)
        horario = st.time_input("Hora do Nascimento:", value=time(14, 0))
    
    st.markdown("---")
    st.subheader("❤️ Conexão de Almas (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):", placeholder="Deixe vazio se não quiser análise de casal")
    p_signo = st.selectbox("Signo do Parceiro(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])

    uploaded_file = st.file_uploader("Foque bem na sua palma esquerda...", type=["jpg", "jpeg", "png"])

    if st.button("🌟 INVOCAR O DESTINO"):
        if uploaded_file and nome:
            with st.spinner("Madame Janara acessa as correntes do tempo..."):
                try:
                    image = Image.open(uploaded_file)
                    d = {'nome': nome, 'data_nasc': data_nasc, 'horario': horario, 'cidade': cidade, 'signo': signo, 'p_nome': p_nome, 'p_signo': p_signo}
                    res = gerar_profecia_completa(image, d)
                    
                    # Split robusto (limpa espaços e vazios)
                    partes = [p.strip() for p in res.split('---') if p.strip()]
                    
                    st.session_state.resumo = partes[0] if len(partes) > 0 else "As névoas estão densas..."
                    st.session_state.padrao = partes[1] if len(partes) > 1 else ""
                    st.session_state.vip = partes[2] if len(partes) > 2 else ""
                    st.session_state.soulmate = partes[3] if len(partes) > 3 else ""
                    st.session_state.analise_feita = True
                except Exception as e:
                    st.error("Erro na leitura. Tente novamente.")
        else:
            st.warning("Preencha seu nome e envie a foto da mão.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. EXIBIÇÃO DOS DEGRAUS (VALUE LADDER) ---
if st.session_state.analise_feita:
    # TIER 1: Teaser
    st.markdown("### ✨ O Brilho do Momento")
    st.info(st.session_state.resumo)
    
    # TIER 2: Standard
    with st.expander("🔓 Ver Leitura das Mãos (Gratuito na Beta)"):
        st.write(st.session_state.padrao)
        
    # TIER 3: VIP (Mapa Astral)
    if st.session_state.vip:
        st.markdown("<div class='vip-section'>", unsafe_allow_html=True)
        st.subheader("💎 Nível VIP: Mapa Astral & Futuro")
        if st.button("Revelar Mapa Astral Completo"):
            st.write(st.session_state.vip)
            tts = gTTS(text=st.session_state.vip, lang='pt', tld='com.br')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        st.markdown("</div>", unsafe_allow_html=True)

    # TIER 4: Soulmate (Relacionamento)
    if st.session_state.soulmate and p_nome:
        st.markdown("<div class='soulmate-section'>", unsafe_allow_html=True)
        st.subheader(f"🌹 Destino a Dois: {nome} & {p_nome}")
        email = st.text_input("Para onde enviamos seu Guia de Casal completo?", placeholder="seu@email.com")
        if st.button("💖 Desbloquear Análise de Almas"):
            if email:
                st.write(st.session_state.soulmate)
                msg = urllib.parse.quote(f"A Madame Janara revelou o futuro do meu relacionamento com {p_nome}! ✨ Veja o seu: https://madamejanara.streamlit.app")
                st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border-radius:50px; border:none; padding:15px; font-weight:bold; cursor:pointer;">📲 Compartilhar no WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Insira seu e-mail para acessar esta zona sagrada.")
        st.markdown("</div>", unsafe_allow_html=True)