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

# --- 2. LAYOUT MÍSTICO ---
st.set_page_config(page_title="Madame Janara v4.5", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.92), rgba(0,0,0,0.88)), 
                    url('https://images.unsplash.com/photo-1514467950401-6d8a0116a84d?q=80&w=2070&auto=format&fit=crop');
        background-size: cover; background-attachment: fixed; color: #f3e5ab;
    }
    .main-box { background: rgba(15, 10, 5, 0.95); padding: 25px; border-radius: 20px; border: 1px solid #d4af37; }
    .stButton>button { background: #d4af37 !important; color: black !important; font-weight: 900; border-radius: 50px; width: 100%; height: 3.5em; }
    .vip-section { border: 2px solid #ffd700; background: rgba(212, 175, 55, 0.1); padding: 20px; border-radius: 15px; margin-top: 15px; }
    .soulmate-section { border: 2px solid #ff4d4d; background: rgba(74, 26, 26, 0.3); padding: 20px; border-radius: 15px; margin-top: 15px; }
    h1, h2, h3 { color: #d4af37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTÃO DE ESTADO ---
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'analise' not in st.session_state: st.session_state.analise = {"resumo": "", "padrao": "", "vip": "", "soulmate": "", "feita": False}

def limpar_tudo():
    st.session_state.form_id += 1
    st.session_state.analise = {"resumo": "", "padrao": "", "vip": "", "soulmate": "", "feita": False}
    st.rerun()

# --- 4. MOTOR DE IA (AUTODESCOBERTA E CONTEÚDO DENSO) ---
def obter_melhor_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in modelos:
            if 'gemini-1.5-flash' in m: return m
        return modelos[0]
    except: return 'models/gemini-1.5-flash'

def gerar_profecia(imagem, d):
    nome_modelo = obter_melhor_modelo()
    model = genai.GenerativeModel(nome_modelo)
    
    # Prompt de alta densidade: Exige tópicos específicos para forçar o texto longo
    prompt = f"""
    Você é Madame Janara, uma cigana mística com voz sábia e detalhista. 
    DADOS: {d['nome']}, Nasc: {d['data_nasc']} {d['horario']} em {d['cidade']}, Signo: {d['signo']}.
    PARCEIRO: {d['p_nome']}, Signo: {d['p_signo']}.

    Gere 4 partes separadas por '---'. NÃO escreva 'Parte' ou 'Bloco'.

    1 (TEASER): Um resumo místico de impacto (2 frases).
    ---
    2 (PADRÃO): Leitura das mãos cruzada com {d['signo']}. Desenvolva pelo menos 15 linhas de texto. 
    Fale sobre a Linha da Vida (vitalidade), Linha da Cabeça (intelecto) e como o Sol em {d['signo']} potencializa essas marcas. 
    Seja carismática e detalhista.
    ---
    3 (VIP): Mapa Astral e Destino Profissional. Desenvolva pelo menos 35 linhas de texto. 
    Analise o impacto do Ascendente e da Lua no destino financeiro de {d['nome']}. 
    Fale sobre oportunidades de carreira, grandes mudanças nos próximos 12 meses e dê um conselho espiritual profundo. 
    Use metáforas de estrelas, rotas e caravanas.
    ---
    4 (SOULMATE): Sinastria mística entre {d['nome']} e {d['p_nome']}. Desenvolva pelo menos 35 linhas de texto. 
    Explore a química entre {d['signo']} e {d['p_signo']}. 
    Revele um segredo de uma vida passada que eles compartilharam e dê 3 recomendações ritualísticas e práticas para a harmonia eterna do casal.
    """
    
    imagem.thumbnail((800, 800))
    # Configuração para permitir respostas longas (tokens aumentados)
    config = genai.types.GenerationConfig(max_output_tokens=3000, temperature=0.8)
    
    response = model.generate_content([prompt, imagem], generation_config=config)
    return response.text

# --- 5. INTERFACE ---
st.title("🔮 O Oráculo de Madame Janara")

with st.container():
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    fid = st.session_state.form_id
    
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Seu nome:", placeholder="Nome completo", key=f"n_{fid}")
        data_nasc = st.date_input("Nascimento:", value=None, min_value=date(1900, 1, 1), format="DD/MM/YYYY", key=f"d_{fid}")
        cidade = st.text_input("Cidade de Origem:", placeholder="Onde você nasceu?", key=f"c_{fid}")
    with c2:
        signo = st.selectbox("Seu Signo:", ["Escolha...", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], key=f"s_{fid}")
        horario = st.time_input("Hora do Nascimento:", value=None, key=f"h_{fid}")
    
    st.markdown("---")
    st.subheader("❤️ Conexão de Almas (Opcional)")
    p_nome = st.text_input("Nome do Parceiro(a):", key=f"pn_{fid}")
    p_signo = st.selectbox("Signo do Parceiro(a):", ["Não informado", "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"], key=f"ps_{fid}")

    uploaded_file = st.file_uploader("Sua palma esquerda...", type=["jpg", "jpeg", "png"], key=f"f_{fid}")

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("🌟 INVOCAR O DESTINO"):
            if uploaded_file and nome and data_nasc and signo != "Escolha...":
                with st.spinner("Madame Janara consulta os ventos..."):
                    try:
                        image = Image.open(uploaded_file)
                        d = {'nome': nome, 'data_nasc': data_nasc, 'horario': horario, 'cidade': cidade, 'signo': signo, 'p_nome': p_nome, 'p_signo': p_signo}
                        res = gerar_profecia(image, d)
                        partes = [p.strip() for p in res.split('---') if p.strip()]
                        
                        st.session_state.analise["resumo"] = partes[0] if len(partes) > 0 else ""
                        st.session_state.analise["padrao"] = partes[1] if len(partes) > 1 else ""
                        st.session_state.analise["vip"] = partes[2] if len(partes) > 2 else ""
                        st.session_state.analise["soulmate"] = partes[3] if len(partes) > 3 else ""
                        st.session_state.analise["feita"] = True
                    except Exception as e:
                        st.error(f"Madame Janara teve uma visão nublada. Erro: {e}")
            else:
                st.warning("Preencha Nome, Data, Signo e envie a Foto.")
    with col_btn2:
        st.button("🗑️ Limpar", on_click=limpar_tudo)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. RESULTADOS ---
res = st.session_state.analise
if res["feita"]:
    st.markdown("---")
    st.markdown(f"### ✨ O Brilho do Momento para {nome}")
    st.info(res["resumo"])
    
    with st.expander("🔓 Leitura das Mãos (Fase Beta Gratuita)"):
        st.write(res["padrao"])
        
    if res["vip"]:
        st.markdown(f"<div class='vip-section'><h3>💎 Mapa Astral & Futuro VIP</h3>", unsafe_allow_html=True)
        if st.button("Revelar Destino VIP Completo"):
            st.write(res["vip"])
            tts = gTTS(text=res["vip"], lang='pt', tld='com.br')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3')
        st.markdown("</div>", unsafe_allow_html=True)

    if res["soulmate"] and p_nome:
        st.markdown(f"<div class='soulmate-section'><h3>🌹 Conexão de Almas: {nome} & {p_nome}</h3>", unsafe_allow_html=True)
        email = st.text_input("E-mail para o guia de casal:", key=f"m_{fid}")
        if st.button("💖 Desbloquear Almas"):
            if email:
                st.write(res["soulmate"])
                msg = urllib.parse.quote(f"A Madame Janara revelou o futuro do meu relacionamento com {p_nome}! ✨ Veja o seu: https://madamejanara.streamlit.app")
                st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border-radius:50px; border:none; padding:15px; font-weight:bold; cursor:pointer;">📲 Compartilhar no WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Insira seu e-mail.")
        st.markdown("</div>", unsafe_allow_html=True)