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
        background: rgba(25, 20, 15, 0.95);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #d4af37;
    }
    h1, h2, h3 { color: #d4af37 !important; }
    .stButton>button {
        background: linear-gradient(45deg, #d4af37, #aa8a2e);
        color: black !important;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE IA COM FALLBACK DE MODELO ---
def analisar_destino(imagem, nome, data_nasc, signo):
    # Lista de nomes possíveis para o modelo em diferentes versões da API
    model_variants = [
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
        'gemini-1.5-flash-latest'
    ]
    
    prompt = f"""
    Aja como Madame Janara, uma cigana sábia. 
    Consulente: {nome}, Nascido em: {data_nasc.strftime('%d/%m/%Y')}, Signo: {signo}.
    Analise a palma da mão na foto e cruze com as energias zodiacais. 
    Seja poética, detalhada e inspiradora. Máximo 250 palavras.
    """
    
    imagem.thumbnail((800, 800))
    
    last_error = None
    for model_name in model_variants:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, imagem])
            return response.text
        except Exception as e:
            last_error = e
            continue
            
    raise last_error

# --- INTERFACE ---
st.title("🔮 Oráculo de Madame Janara")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Qual seu nome, viajante?", value="Anderson")
        data_nasc = st.date_input("Data de Nascimento", value=date(1981, 7, 28), 
                                 min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with col2:
        signo = st.selectbox("Seu Signo Solar:", ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                                                 "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], index=4)

    uploaded_file = st.file_uploader("Mostre-me sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None and nome:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Revelar meu Destino"):
            with st.spinner("Madame Janara consulta os astros..."):
                try:
                    leitura = analisar_destino(image, nome, data_nasc, signo)
                    st.markdown("---")
                    st.subheader(f"📜 A Profecia para {nome}")
                    st.write(leitura)
                    
                    tts = gTTS(text=leitura, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                except Exception as e:
                    st.error("As névoas continuam densas. Verifique a versão da biblioteca.")
                    st.exception(e)