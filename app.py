import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io

# --- CONFIGURAÇÃO SEGURA DA API ---
# O app agora busca a chave nas configurações escondidas (Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    # Fallback para teste local se você ainda usar o arquivo .env ou manual
    os.environ["GOOGLE_API_KEY"] = "COLOQUE_AQUI_APENAS_PARA_TESTE_LOCAL"
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Madame Janara - O Oráculo Digital", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .main { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1); }
    h1 { color: #d4af37; text-align: center; font-family: 'Serif'; }
    .stButton>button { background-color: #d4af37; color: black; width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DESCOBERTA DE MODELO ---
def obter_modelo_disponivel():
    modelos_suportados = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_suportados.append(m.name)
        
        if 'models/gemini-1.5-flash' in modelos_suportados:
            return 'gemini-1.5-flash'
        return modelos_suportados[0].split('/')[-1]
    except:
        return 'gemini-1.5-flash'

def analisar_mao(imagem):
    nome_modelo = obter_modelo_disponivel()
    model = genai.GenerativeModel(nome_modelo)
    prompt = "Aja como Madame Janara, uma cigana experiente. Analise a palma da mão: 1. Saudação. 2. Ponto positivo. 3. Desafio (Vejo que sua energia...). 4. Motivação final. Máximo 150 palavras."
    
    imagem.thumbnail((1024, 1024))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- INTERFACE ---
st.title("✨ Madame Janara ✨")

with st.container():
    uploaded_file = st.file_uploader("Envie uma foto da sua palma...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Sua conexão com o destino...", use_column_width=True)
        
        if st.button("Revelar meu Destino"):
            with st.spinner("Madame Janara consulta os ventos..."):
                try:
                    resultado_texto = analisar_mao(image)
                    st.subheader("A Leitura de Madame Janara:")
                    st.write(resultado_texto)
                    
                    tts = gTTS(text=resultado_texto, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                    st.success("A luz guia seu caminho!")
                except Exception as e:
                    st.error("Madame Janara teve uma visão nublada.")
                    st.exception(e)
    else:
        st.info("Aguardando sua foto para iniciar a leitura...")