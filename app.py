import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date

# --- CONFIGURAÇÃO SEGURA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- CSS TEMA MÍSTICO ---
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
        background: rgba(20, 15, 10, 0.9);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #d4af37;
    }
    .stButton>button {
        background: #d4af37;
        color: black !important;
        width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE IA ---
def analisar_destino(imagem, nome, data_nasc, signo):
    # Usando o modelo mais estável para produção
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Aja como Madame Janara, uma cigana sábia. 
    Consulente: {nome}, Nascido em: {data_nasc.strftime('%d/%m/%Y')}, Signo: {signo}.
    Analise a imagem da mão cruzando com o zodíaco. 
    Seja detalhada, carismática e misteriosa. Máximo 250 palavras.
    """
    
    # Otimização agressiva para fotos de alta resolução (como S26 Ultra)
    # Reduzimos para 800px para garantir que o upload seja instantâneo
    imagem.thumbnail((800, 800)) 
    
    response = model.generate_content([prompt, imagem])
    return response.text

# --- INTERFACE ---
st.title("🔮 Oráculo de Madame Janara")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Qual seu nome, viajante?")
        data_nasc = st.date_input("Data de Nascimento", value=date(1981, 7, 28), 
                                 min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with col2:
        signo = st.selectbox("Seu Signo:", ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                                            "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"])

    uploaded_file = st.file_uploader("Mostre sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Revelar meu Destino"):
            with st.spinner("Madame Janara consulta os ventos..."):
                try:
                    # Chamar a IA
                    resultado = analisar_destino(image, nome, data_nasc, signo)
                    
                    st.markdown("---")
                    st.subheader(f"📜 A Profecia para {nome}")
                    st.write(resultado)
                    
                    # Áudio
                    tts = gTTS(text=resultado, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                    
                except Exception as e:
                    st.error("As névoas do tempo estão nubladas. Erro técnico:")
                    # Revelar o erro real para o Anderson debugar
                    st.exception(e)