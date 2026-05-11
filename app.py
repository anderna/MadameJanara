import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import io
from datetime import date, time
import urllib.parse

# --- 1. CONFIGURAÇÃO DA API ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. LÓGICA DE NUMEROLOGIA ---
def calcular_numerologia(data):
    if not data: return 0
    numeros = data.strftime('%d%m%Y')
    soma = sum(int(n) for n in numeros)
    while soma > 9 and soma not in [11, 22]: # Mantém números mestres
        soma = sum(int(n) for n in str(soma))
    return soma

# --- 3. LAYOUT MÍSTICO ---
st.set_page_config(page_title="Madame Janara v4.6", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=2094&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(10, 8, 5, 0.98); padding: 30px; border-radius: 25px; border: 1px solid #d4af37; }
    .stButton>button { background: #d4af37 !important; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; height: 3.5em; }
    .vip-section { border: 2px solid #ffd700; background: rgba(212, 175, 55, 0.1); padding: 25px; border-radius: 15px; margin-top: 20px; }
    .soulmate-section { border: 2px solid #ff4d4d; background: rgba(74, 26, 26, 0.3); padding: 25px; border-radius: 15px; margin-top: 20px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTÃO DE ESTADO ---
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'analise' not in st.session_state: st.session_state.analise = {"resumo": "", "padrao": "", "vip": "", "soulmate": "", "feita": False}

def limpar_tudo():
    st.session_state.form_id += 1
    st.session_state.analise = {"resumo": "", "padrao": "", "vip": "", "soulmate": "", "feita": False}
    st.rerun()

# --- 5. MOTOR DE IA (ANÁLISE QUALITATIVA CRUZADA) ---
def gerar_profecia(imagem, d, num_destino):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Aja como Madame Janara, a maior autoridade mundial em Quiromancia, Astrologia e Numerologia.
    DADOS DO CONSULENTE: {d['nome']}, Nasc: {d['data_nasc']} {d['horario']} em {d['cidade']}.
    SIGNO SOLAR: {d['signo']} | NÚMERO DE DESTINO (NUMEROLOGIA): {num_destino}
    DADOS PARCEIRO: {d['p_nome']} (Signo: {d['p_signo']})

    SUA MISSÃO: Realizar uma análise qualitativa PROFUNDA, cruzando os três domínios.
    Gere 4 partes separadas por '---'.

    1 (TEASER): Resumo místico e visceral (2 frases).
    ---
    2 (PADRÃO - CORRELAÇÃO MÃO/SIGNO): Mínimo 15 linhas. 
    Analise as linhas da mão (Vida, Cabeça, Coração) e explique como o Signo de {d['signo']} influencia essas marcas físicas.
    ---
    3 (VIP - A TRIANGULAÇÃO SAGRADA): Mínimo 40 linhas. 
    Cruze a Numerologia {num_destino} com o Mapa Astral e as marcas da mão. 
    Explique como o número {num_destino} governa sua missão de alma e como isso se manifesta no seu sucesso financeiro e desafios de carreira. 
    Seja detalhista sobre os próximos 12 meses, indicando datas ou períodos de poder.
    ---
    4 (SOULMATE - SINASTRIA DE ALMAS): Mínimo 35 linhas. 
    Análise qualitativa da compatibilidade entre {d['nome']} e {d['p_nome']}. 
    Cruze os elementos (Fogo, Terra, Ar, Água) e revele um karma de vida passada que as linhas da mão de {d['nome']} confirmam sobre este encontro.
    Dê 3 conselhos ritualísticos detalhados.
    """
    
    imagem.thumbnail((800, 800))
    config = genai.types.GenerationConfig(max_output_tokens=4096, temperature=0.85)
    response = model.generate_content([prompt, imagem], generation_config=config)
    return response.text

# --- 6. INTERFACE ---
st.title("🔮 Oráculo Supremo de Madame Janara")

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    fid = st.session_state.form_id
    
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome completo:", placeholder="O nome revela a vibração...", key=f"n_{fid}")
        data_nasc = st.date_input("Nascimento:", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY", key=f"d_{fid}")
        cidade = st.text_input("Cidade/UF de Origem:", placeholder="Onde as estrelas o viram nascer?", key=f"c_{fid}")
    with c2:
        signo = st.selectbox("Signo Solar:", ["Escolha...", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], key=f"s_{fid}")
        horario = st.time_input("Hora do Nascimento:", value=None, key=f"h_{fid}")
    
    # Cálculo de numerologia em tempo real para o UI
    num_exibido = calcular_numerologia(data_nasc) if data_nasc else "..."
    st.info(f"🔢 Sua Vibração Numerológica Calculada: **{num_exibido}**")

    st.markdown("---")
    st.subheader("❤️ Conexão de Almas (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):", key=f"pn_{fid}")
    p_signo = st.selectbox("Signo dele(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], key=f"ps_{fid}")

    uploaded_file = st.file_uploader("Sua palma esquerda (clara e iluminada)...", type=["jpg", "jpeg", "png"], key=f"f_{fid}")

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("🌟 INVOCAR O GRANDE ORÁCULO"):
            if uploaded_file and nome and data_nasc and signo != "Escolha...":
                with st.spinner("Madame Janara tece as teias do tempo..."):
                    try:
                        image = Image.open(uploaded_file)
                        d = {'nome': nome, 'data_nasc': data_nasc, 'horario': horario, 'cidade': cidade, 'signo': signo, 'p_nome': p_nome, 'p_signo': p_signo}
                        res = gerar_profecia(image, d, num_exibido)
                        partes = [p.strip() for p in res.split('---') if p.strip()]
                        
                        st.session_state.analise["resumo"] = partes[0] if len(partes) > 0 else ""
                        st.session_state.analise["padrao"] = partes[1] if len(partes) > 1 else ""
                        st.session_state.analise["vip"] = partes[2] if len(partes) > 2 else ""
                        st.session_state.analise["soulmate"] = partes[3] if len(partes) > 3 else ""
                        st.session_state.analise["feita"] = True
                    except Exception as e:
                        st.error(f"Erro na visão: {e}")
            else:
                st.warning("Preencha Nome, Data, Signo e envie a Foto.")
    with col_btn2:
        st.button("🗑️ Limpar", on_click=limpar_tudo)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. RESULTADOS QUALITATIVOS ---
res = st.session_state.analise
if res["feita"]:
    st.markdown("---")
    st.markdown(f"### ✨ O Brilho do Momento para {nome}")
    st.info(res["resumo"])
    
    with st.expander("🔓 Leitura das Mãos (Análise Quirológica)"):
        st.write(res["padrao"])
        
    if res["vip"]:
        st.markdown(f"<div class='vip-section'><h3>💎 A Triangulação: Numerologia & Destino VIP</h3>", unsafe_allow_html=True)
        if st.button("Revelar Laudo de Destino Completo"):
            st.write(res["vip"])
            tts = gTTS(text=res["vip"], lang='pt', tld='com.br')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        st.markdown("</div>", unsafe_allow_html=True)

    if res["soulmate"] and p_nome:
        st.markdown(f"<div class='soulmate-section'><h3>🌹 Sinastria de Almas: {nome} & {p_nome}</h3>", unsafe_allow_html=True)
        email = st.text_input("E-mail para o guia de casal completo:", key=f"m_{fid}")
        if st.button("💖 Revelar Segredos do Casal"):
            if email:
                st.write(res["soulmate"])
                msg = urllib.parse.quote(f"Estou chocado com a análise holística que a Madame Janara fez de nós dois! ✨ Confira: https://madamejanara.streamlit.app")
                st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border-radius:50px; border:none; padding:15px; font-weight:bold; cursor:pointer;">📲 Compartilhar Sinastria</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Insira seu e-mail para a análise de sinastria.")