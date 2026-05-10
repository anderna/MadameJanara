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

# --- BARRA LATERAL DE DIAGNÓSTICO (Para você ver o que está acontecendo) ---
with st.sidebar:
    st.header("🛠️ Status do Sistema")
    try:
        # Tenta listar os modelos disponíveis
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.success(f"Modelos detectados: {len(models)}")
        selected_model = st.selectbox("Motor da Madame:", models, index=0)
    except Exception as e:
        st.error("Erro ao listar modelos. Verifique sua API Key.")
        selected_model = "models/gemini-1.5-flash"

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
    .main { background: rgba(25, 20, 15, 0.95); border: 1px solid #d4af37; border-radius: 20px; padding: 20px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    .stButton>button { background: #d4af37; color: black !important; font-weight: bold; width: 100%; border-radius: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DA IA ---
def analisar_destino(imagem, nome, data_nasc, signo, model_name):
    # Forçamos o uso do modelo selecionado no diagnóstico
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Aja como Madame Janara, uma cigana sábia e carismática. 
    Consulente: {nome}, Nascido em: {data_nasc.strftime('%d/%m/%Y')}, Signo: {signo}.
    
    TAREFA: Analise a palma da mão na foto e cruze com as energias de {signo}.
    ESTRUTURA:
    1. Saudação mística personalizada chamando pelo nome.
    2. O que o Zodíaco revela (baseado na data de nascimento).
    3. Leitura das linhas da mão com detalhes e mistério.
    4. O 'Segredo da Estrada' (conselho empático).
    5. Benção cigana final.
    Mínimo 200 palavras. Use português do Brasil.
    """
    
    imagem.thumbnail((800, 800))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- INTERFACE ---
st.title("🔮 Oráculo de Madame Janara")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Seu nome, viajante:", value="Anderson")
        data_nasc = st.date_input("Data de Nascimento", value=date(1981, 7, 28), 
                                 min_value=date(1900, 1, 1), format="DD/MM/YYYY")
    with col2:
        signo = st.selectbox("Seu Signo:", ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                                            "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], index=4)

    uploaded_file = st.file_uploader("Mostre sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file and nome:
        image = Image.open(uploaded_file)
        st.image(image, width=300)
        
        if st.button("Revelar meu Destino"):
            with st.spinner("Madame Janara consulta os ventos sagrados..."):
                try:
                    leitura = analisar_destino(image, nome, data_nasc, signo, selected_model)
                    st.markdown("---")
                    st.subheader(f"📜 A Profecia de {nome}")
                    st.write(leitura)
                    
                    tts = gTTS(text=leitura, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                except Exception as e:
                    st.error("As névoas continuam densas. Erro na leitura.")
                    st.exception(e)