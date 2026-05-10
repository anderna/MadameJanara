import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date, time
import urllib.parse

# --- 1. CONFIGURAÇÃO SEGURA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. LAYOUT MÍSTICO ---
st.set_page_config(page_title="Madame Janara v4.1", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1514467950401-6d8a0116a84d?q=80&w=2070&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(15, 10, 5, 0.95); padding: 25px; border-radius: 20px; border: 1px solid #d4af37; }
    .stButton>button { background: #d4af37; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; }
    .vip-section { border: 2px solid #ffd700; background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 15px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE IA ---
def gerar_profecia(imagem, d):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt ajustado para evitar repetição de instruções
    prompt = f"""
    Você é Madame Janara, uma cigana mística. 
    DADOS: Nome: {d['nome']}, Nascimento: {d['data_nasc']} {d['horario']} em {d['cidade']}, Signo: {d['signo']}.
    PARCEIRO: {d['p_nome']}, Signo: {d['p_signo']}.

    Gere 4 blocos de texto puros, SEM TÍTULOS como 'Bloco 1' ou 'Nível'. 
    Apenas o conteúdo místico, separando cada parte por '---'.

    PARTE 1: Teaser místico de 2 frases curtas.
    ---
    PARTE 2: Leitura profunda das linhas da mão com {d['signo']}.
    ---
    PARTE 3: Mapa Astral VIP. Sucesso e finanças.
    ---
    PARTE 4: Sinastria Amorosa com {d['p_nome']}. Segredo de vidas passadas.
    """
    
    imagem.thumbnail((800, 800))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- 4. INTERFACE (LGPD COMPLIANT) ---
st.title("🔮 O Grande Oráculo de Madame Janara")

# Inicialização de estado
for key in ['resumo', 'padrao', 'vip', 'soulmate', 'analise_feita']:
    if key not in st.session_state: st.session_state[key] = None

# Função para resetar (LGPD)
def reset_session():
    for key in st.session_state.keys():
        st.session_state[key] = None
    st.rerun()

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        # Removido value="Anderson" para privacidade
        nome = st.text_input("Seu nome:", placeholder="Como devo chamá-lo?") 
        data_nasc = st.date_input("Nascimento:", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY")
        cidade = st.text_input("Cidade de Origem:", placeholder="Onde você nasceu?")
    with c2:
        signo = st.selectbox("Seu Signo:", ["Escolha...", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])
        horario = st.time_input("Hora do Nascimento:", value=None)
    
    st.markdown("---")
    st.subheader("❤️ Conexão de Almas (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):")
    p_signo = st.selectbox("Signo do Parceiro(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])

    uploaded_file = st.file_uploader("Foque bem na sua palma esquerda...", type=["jpg", "jpeg", "png"])

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("🌟 INVOCAR O DESTINO"):
            if uploaded_file and nome and signo != "Escolha...":
                with st.spinner("Madame Janara acessa as correntes do tempo..."):
                    try:
                        image = Image.open(uploaded_file)
                        d = {'nome': nome, 'data_nasc': data_nasc, 'horario': horario, 'cidade': cidade, 'signo': signo, 'p_nome': p_nome, 'p_signo': p_signo}
                        res = gerar_profecia(image, d)
                        partes = [p.strip() for p in res.split('---') if p.strip()]
                        
                        st.session_state.resumo = partes[0] if len(partes) > 0 else ""
                        st.session_state.padrao = partes[1] if len(partes) > 1 else ""
                        st.session_state.vip = partes[2] if len(partes) > 2 else ""
                        st.session_state.soulmate = partes[3] if len(partes) > 3 else ""
                        st.session_state.analise_feita = True
                    except:
                        st.error("As névoas estão densas. Tente novamente.")
            else:
                st.warning("Por favor, preencha nome, signo e envie a foto.")
    
    with col_btn2:
        if st.button("🗑️ Limpar"):
            reset_session()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. RESULTADOS ---
if st.session_state.analise_feita:
    st.markdown("### ✨ O Brilho do Momento")
    st.info(st.session_state.resumo)
    
    with st.expander("🔓 Ver Leitura das Mãos (Gratuito na Beta)"):
        st.write(st.session_state.padrao)
        
    if st.session_state.vip:
        st.markdown("<div class='vip-section'>", unsafe_allow_html=True)
        st.subheader("💎 Mapa Astral & Futuro")
        if st.button("Revelar Mapa Astral Completo"):
            st.write(st.session_state.vip)
            tts = gTTS(text=st.session_state.vip, lang='pt', tld='com.br')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.soulmate and p_nome:
        st.markdown("<div class='soulmate-section'>", unsafe_allow_html=True)
        st.subheader(f"🌹 Destino a Dois: {nome} & {p_nome}")
        email = st.text_input("E-mail para receber o guia completo:")
        if st.button("💖 Desbloquear Análise de Almas"):
            if email:
                st.write(st.session_state.soulmate)
                msg = urllib.parse.quote(f"A Madame Janara revelou o futuro do meu relacionamento! ✨ Veja o seu: https://madamejanara.streamlit.app")
                st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border-radius:50px; border:none; padding:15px; font-weight:bold; cursor:pointer;">📲 Compartilhar no WhatsApp</button></a>', unsafe_allow_html=True)