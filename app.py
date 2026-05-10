import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io

# --- CONFIGURAÇÃO DA API ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyAj-gvxEEYcecTPb9sdXWrhVTL1fh58_9g"
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
    # Listamos os modelos para o terminal (você verá isso no VS Code)
    # Isso ajuda no troubleshooting de Managed Services
    print("--- Verificando Inventário de Modelos ---")
    modelos_suportados = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos_suportados.append(m.name)
            print(f"Modelo encontrado: {m.name}")
    
    # Prioridade 1: models/gemini-1.5-flash
    # Prioridade 2: models/gemini-1.5-pro
    # Prioridade 3: Qualquer um que contenha 'flash'
    if 'models/gemini-1.5-flash' in modelos_suportados:
        return 'gemini-1.5-flash'
    elif 'models/gemini-1.5-pro' in modelos_suportados:
        return 'gemini-1.5-pro'
    
    # Fallback para o primeiro disponível que suporte conteúdo
    return modelos_suportados[0].split('/')[-1] if modelos_suportados else 'gemini-1.5-flash'

# --- LÓGICA DA IA ---
def analisar_mao(imagem):
    nome_modelo = obter_modelo_disponivel()
    model = genai.GenerativeModel(nome_modelo)
    
    prompt = """
    Aja como Madame Janara, uma cigana experiente e empática. 
    Analise a imagem da palma da mão fornecida.
    ESTRUTURA DA RESPOSTA:
    1. Saudação mística personalizada.
    2. PONTO POSITIVO: Identifique uma linha forte e elogia.
    3. DESAFIO: Use 'Vejo que sua energia tem sido muito exigida...'.
    4. MOTIVAÇÃO FINAL: Previsão de luz e conselho prático.
    Máximo 150 palavras. Use português do Brasil.
    """
    
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
                    st.error("A visão ainda está nublada. Verifique os logs no terminal.")
                    st.exception(e)
    else:
        st.info("Aguardando sua foto para iniciar a leitura...")