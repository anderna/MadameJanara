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

# --- CSS AVANÇADO (Interface Imersiva e Temática) ---
st.markdown("""
    <style>
    /* Fundo com imagem mística e overlay escuro para leitura */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url('https://images.unsplash.com/photo-1514467950401-6d8a0116a84d?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #f3e5ab;
    }
    /* Estilização dos inputs para o padrão BR e Místico */
    .main {
        background: rgba(30, 20, 10, 0.9);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #d4af37;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.4);
    }
    h1, h2, h3 {
        color: #d4af37 !important;
        font-family: 'Playfair Display', serif;
    }
    .stButton>button {
        background: linear-gradient(45deg, #d4af37, #aa8a2e);
        color: black !important;
        border: none;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 50px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #d4af37;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DESCOBERTA DE MODELO ---
def analisar_destino(imagem, nome, data_nasc, signo):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é Madame Janara, uma cigana mística de linhagem antiga, sábia e extremamente carismática.
    DADOS DO CONSULENTE:
    Nome: {nome}
    Data de Nascimento: {data_nasc.strftime('%d/%m/%Y')}
    Signo Solar: {signo}
    
    SUA TAREFA:
    Analise a imagem da palma da mão e faça uma leitura profunda cruzando as linhas com a energia astrológica de {signo}.
    
    ESTRUTURA DA RESPOSTA:
    1. Saudação calorosa e mística invocando os ancestrais.
    2. Revelação do Zodíaco: Como a data de nascimento molda o caráter do consulente.
    3. Leitura da Palma: Detalhes específicos sobre o que as linhas dizem (foco em sucesso, amor e saúde espiritual).
    4. O "Segredo da Estrada": Um conselho específico para o momento atual ('Vejo que sua energia tem sido muito exigida...').
    5. Benção Final: Uma mensagem poderosa de encerramento.
    
    TOM: Poético, detalhado, empático e encorajador. Máximo 300 palavras.
    """
    
    imagem.thumbnail((1024, 1024))
    response = model.generate_content([prompt, imagem])
    return response.text

# --- INTERFACE ---
st.title("🔮 O Oráculo de Madame Janara")
st.markdown("#### Entre na tenda, viajante. Seu destino está gravado nas estrelas e em suas mãos.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Como devo chamá-lo(a)?", placeholder="Seu nome aqui...")
        # Correção da Data: min_value e max_value definidos para permitir nascidos antes de 2016
        data_nasc = st.date_input(
            "Data de Nascimento", 
            value=date(1985, 1, 1),
            min_value=date(1900, 1, 1), 
            max_value=date.today(),
            format="DD/MM/YYYY" # Formato brasileiro
        )
    with col2:
        signos = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
                  "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
        signo = st.selectbox("Seu Signo Solar:", signos)
        st.markdown("<br>", unsafe_allow_html=True) # Espaçador

    uploaded_file = st.file_uploader("Mostre-me sua palma para que eu possa ler sua jornada...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None and nome:
        image = Image.open(uploaded_file)
        st.image(image, width=300, caption="Sua conexão com o oculto...")
        
        if st.button("Revelar o que o Destino reserva"):
            with st.spinner("Madame Janara consulta os astros e as correntes..."):
                try:
                    leitura = analisar_destino(image, nome, data_nasc, signo)
                    st.markdown("---")
                    st.subheader(f"📜 A Profecia de {nome}")
                    st.write(leitura)
                    
                    # Geração de Áudio
                    tts = gTTS(text=leitura, lang='pt', tld='com.br')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3')
                    
                    st.success("Que os ventos soprem a seu favor!")
                except Exception as e:
                    st.error("As névoas do tempo estão muito densas. Tente novamente.")
    else:
        st.info("Para começar, preencha seus dados e mostre-me sua mão.")