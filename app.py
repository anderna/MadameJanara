import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date
import urllib.parse

# --- 1. CONFIGURAÇÃO SEGURA DA API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. LAYOUT E CSS (Estética Gypsy Tech) ---
st.set_page_config(page_title="Madame Janara - Oráculo Digital", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1514467950401-6d8a0116a84d?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #f3e5ab;
    }
    .main {
        background: rgba(20, 15, 10, 0.95);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #d4af37;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
    }
    h1, h2, h3 { color: #d4af37 !important; font-family: 'Playfair Display', serif; }
    .stButton>button {
        background: linear-gradient(45deg, #d4af37, #aa8a2e);
        color: black !important;
        font-weight: bold;
        width: 100%;
        border-radius: 50px;
        border: none;
        padding: 10px 20px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #d4af37; }
    .premium-box {
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 15px;
        background: rgba(212, 175, 55, 0.05);
        margin-top: 20px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DE DESCOBERTA DE MODELO ---
def obter_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos:
            if 'gemini-1.5-flash' in m: return m
        return modelos[0]
    except:
        return 'models/gemini-1.5-flash'

# --- 4. MOTOR DE IA (Análise de Destino) ---
def analisar_destino(imagem, nome, data_nasc, signo):
    nome_modelo = obter_modelo()
    model = genai.GenerativeModel(nome_modelo)
    
    prompt = f"""
    Aja como Madame Janara, uma cigana mística, sábia e carismática.
    Consulente: {nome}, Nascido em: {data_nasc.strftime('%d/%m/%Y')}, Signo: {signo}.
    
    ESTRUTURA DA RESPOSTA (OBRIGATÓRIO):
    Separe os dois blocos abaixo usando EXATAMENTE o separador '---'
    
    Bloco 1 (Teaser): Uma síntese mística de no máximo 3 frases curtas e impactantes.
    ---
    Bloco 2 (Completo): Uma leitura profunda e detalhada (250 palavras) cruzando as linhas da mão com {signo}. 
    Seja empática, fale sobre desafios ('Vejo que sua energia...') e traga uma profecia de luz.
    """
    
    imagem.thumbnail((800, 800)) # Otimização para S26 Ultra
    response = model.generate_content([prompt, imagem])
    return response.text

# --- 5. INTERFACE DO USUÁRIO ---
st.title("🔮 O Oráculo de Madame Janara")
st.markdown("<p style='text-align: center;'>Entre na tenda, viajante. Seu destino aguarda.</p>", unsafe_allow_html=True)

# Inicialização de Session State
if 'leitura_resumo' not in st.session_state: st.session_state.leitura_resumo = None
if 'leitura_completa' not in st.session_state: st.session_state.leitura_completa = None

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Como devo chamá-lo(a)?", value="Anderson")
        data_nasc = st.date_input("Data de Nascimento", value=date(1981, 7, 28), 
                                 min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with col2:
        signo = st.selectbox("Seu Signo Solar:", ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                                                 "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], index=4)

    uploaded_file = st.file_uploader("Mostre-me sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file and nome:
        image = Image.open(uploaded_file)
        st.image(image, width=300, caption="Sua conexão com o destino...")
        
        if st.button("Revelar meu Destino"):
            with st.spinner("Madame Janara embaralha as energias..."):
                try:
                    resultado = analisar_destino(image, nome, data_nasc, signo)
                    if '---' in resultado:
                        partes = resultado.split('---')
                        st.session_state.leitura_resumo = partes[0]
                        st.session_state.leitura_completa = partes[1]
                    else:
                        st.session_state.leitura_resumo = resultado
                        st.session_state.leitura_completa = "As névoas estão densas para a visão completa agora."
                except Exception as e:
                    st.error("Madame Janara teve uma visão nublada. Tente novamente.")

# --- 6. EXIBIÇÃO E VIRALIZAÇÃO ---
if st.session_state.leitura_resumo:
    st.markdown("---")
    st.subheader(f"✨ O Brilho do Momento para {nome}")
    st.write(st.session_state.leitura_resumo)
    
    st.info("💡 Aproveite: A leitura completa está liberada gratuitamente na fase beta!")
    
    if st.button("🔓 Ver Profecia Completa (Grátis hoje)"):
        st.markdown(f"<div class='premium-box'><h3>📜 A Visão Profunda</h3>{st.session_state.leitura_completa}</div>", unsafe_allow_html=True)
        
        # Geração de Áudio (Voz da Madame)
        try:
            tts = gTTS(text=st.session_state.leitura_completa, lang='pt', tld='com.br')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        except:
            st.warning("O vento levou a voz da Madame, mas as palavras permanecem.")

        # Botão WhatsApp Viral
        texto_share = f"Madame Janara revelou meu destino! ✨ Fiquei impressionado com o que ela viu para meu signo de {signo}. Veja o seu também antes que a fase beta acabe!"
        link_app = "https://madamejanara.streamlit.app"
        msg_final = urllib.parse.quote(f"{texto_share}\n\n{link_app}")
        
        st.markdown(f"""
            <a href="https://wa.me/?text={msg_final}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 50px; text-align: center; font-weight: bold; font-size: 18px; margin-top: 20px;">
                    📲 Compartilhar no WhatsApp
                </div>
            </a>
        """, unsafe_allow_html=True)