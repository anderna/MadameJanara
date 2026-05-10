import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS # Mantido como fallback, mas recomendo ElevenLabs
import os
import io

# --- CONFIGURAÇÃO SEGURA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- CSS AVANÇADO (Interface Imersiva) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com/photo-1515515024443-43152697813a?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        color: #f3e5ab;
    }
    .stTextInput>div>div>input, .stDateInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid #d4af37;
    }
    .main {
        background: rgba(20, 20, 25, 0.85);
        padding: 40px;
        border-radius: 25px;
        border: 2px solid #d4af37;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
    }
    h1 {
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 4px #000;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA REFINADA DA MADAME ---
def analisar_destino(imagem, nome, data_nasc, signo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é Madame Janara. Uma cigana mística, carismática e profunda.
    DADOS DO CONSULENTE:
    Nome: {nome}
    Nascimento: {data_nasc}
    Signo: {signo}
    
    TAREFA:
    Analise a palma da mão na imagem e cruze com as energias do signo de {signo}.
    A resposta deve ser detalhada, rica em metáforas (fogueira, cartas, estrelas, caravana).
    
    ESTRUTURA:
    1. Saudação calorosa chamando pelo nome.
    2. O que o Zodíaco revela combinado com a linha da cabeça.
    3. Um desafio atual (seja empática: 'Vejo que sua energia tem sido muito exigida...').
    4. Um segredo revelado pelas linhas da mão sobre o futuro próximo.
    5. Conselho final motivador e poderoso.
    
    Tom: Detalhado, misterioso e acolhedor. Use cerca de 250 palavras.
    """
    
    imagem.thumbnail((1024, 1024))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- INTERFACE DE USUÁRIO ---
st.title("🔮 O Oráculo de Madame Janara")
st.markdown("### Deixe que as estrelas e suas mãos contem sua história...")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Qual seu nome, viajante?")
        data_nasc = st.date_input("Quando você viu a luz pela primeira vez?")
    with col2:
        signos = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                  "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
        signo = st.selectbox("Seu signo solar:", signos)
        horario = st.time_input("Hora do nascimento (opcional)", value=None)

    uploaded_file = st.file_uploader("Mostre-me sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None and nome:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Consultar o Destino"):
            with st.spinner("Madame Janara embaralha as energias..."):
                try:
                    leitura = analisar_destino(image, nome, data_nasc, signo)
                    st.markdown("---")
                    st.subheader(f"📜 A Profecia para {nome}")
                    st.write(leitura)
                    
                    # Áudio
                    tts = gTTS(text=leitura, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                    
                except Exception as e:
                    st.error("As névoas do tempo estão muito densas. Tente novamente.")