import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Consultor de Imóveis IA", page_icon="🏠", layout="wide")

st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color:#F0F9FF; font-family:'Inter',sans-serif; }
    [data-testid="stSidebar"] { display:none; }
    .stTextInput>div>div>input, .stTextArea>div>textarea,
    .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color:#FFFFFF !important; color:#1A1A2E !important;
        border:1px solid #CED4DA !important; font-family:'Inter',sans-serif !important;
    }
    .stButton>button {
        width:100%; border-radius:10px; height:3.2em;
        background:linear-gradient(135deg,#0369A1,#0284C7) !important; color:white !important;
        font-weight:600; border:none; box-shadow:2px 2px 8px rgba(0,0,0,0.1);
        font-family:'Inter',sans-serif !important; transition:all 0.2s ease;
    }
    .stButton>button:hover { background:linear-gradient(135deg,#0284C7,#0369A1) !important; transform:translateY(-1px); }
    .stApp .stButton>button, .stApp .stButton>button p,
    .stApp .stButton>button span, .stApp .stButton>button div { color:white !important; }
    .stApp h1, .stApp h2, .stApp h3 { color:#0C4A6E !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
    .card { background:linear-gradient(135deg,#F0F9FF,#E0F2FE); padding:20px; border-radius:14px; border:1px solid #7DD3FC; margin-bottom:14px; white-space:normal; word-wrap:break-word; }
    .stApp .card, .stApp .card p, .stApp .card span, .stApp .card div, .stApp .card strong { color:#0C4A6E !important; }
    .card-blue { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; }
    .stApp .card-blue, .stApp .card-blue p, .stApp .card-blue div { color:#1E3A8A !important; }
    .card-red { background:linear-gradient(135deg,#FFF5F5,#FEE2E2); padding:20px; border-radius:14px; border:1px solid #FECACA; margin-bottom:14px; }
    .stApp .card-red, .stApp .card-red p, .stApp .card-red div { color:#7F1D1D !important; }
    .card-green { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; }
    .stApp .card-green, .stApp .card-green p, .stApp .card-green div { color:#14532D !important; }
    .card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
    .stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
    .badge { background:#0369A1; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-verde { background:#059669; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-amarelo { background:#B45309; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-roxo { background:#6D28D9; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#7DD3FC,transparent); margin:18px 0; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #7DD3FC; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item span, .stApp .hist-item div { color:#0C4A6E !important; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #7DD3FC; }
    .stApp .stat-box div, .stApp .stat-box span { color:#0C4A6E !important; }
    .chat-user { background:#FFFFFF; border:1px solid #7DD3FC; border-radius:12px 12px 4px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-user, .stApp .chat-user p, .stApp .chat-user div { color:#0C4A6E !important; }
    .chat-persona { background:#E0F2FE; border:1px solid #7DD3FC; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-persona, .stApp .chat-persona p, .stApp .chat-persona div { color:#0C4A6E !important; }

    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = "Você é um consultor imobiliário especialista. Ajuda pessoas a tomar decisões inteligentes sobre compra, venda, aluguel e investimento em imóveis. Explica financiamentos, analisa contratos em linguagem simples e alerta sobre riscos. Nunca garante valorização. Português do Brasil."

@st.cache_resource
def get_cache_consultor_imoveis():
    return {"perfis": {}}

_cache = get_cache_consultor_imoveis()

CHAVES_SALVAR = ["usuario","historico_consultor_imoveis"]

def gerar_json():
    return json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str)

def carregar_json_sessao(dados):
    _bloq = {'api_key','etapa','nome_login','chave_login','upload_login','btn_entrar_login'}
    _pref = (
        'btn_','sel_','ul_','dl_','cad_','_sub','_sm','_tab','_bsc',
        'ativo_','rem_','sel_pet_','ev_','prof_','hig_','prev_',
        'vac_','sint_','comp_','trad_','subs_','amb_','viag_','chat_',
        'duvida_','emerg_','peso_','data_','obs_','tipo_','vet_','desc_',
        'local_','prox_','alim','sit_emerg_','tc_','oraf','siau','agmag',
        'lv','mv','pt','pi','sh','wc','rv','rp','rc',
    )
    import re as _re
    for k, v in dados.items():
        if k in _bloq: continue
        if any(k.startswith(p) for p in _pref): continue
        if _re.match(r'.+_\d+$', k): continue
        st.session_state[k] = v

def salvar_perfil_cache(usuario):
    _cache["perfis"][usuario] = {k: st.session_state.get(k) for k in CHAVES_SALVAR}

def perfis_salvos():
    return [p for p in _cache["perfis"].keys() if len(p.strip()) >= 2]

def carregar_perfil_cache(usuario):
    return _cache["perfis"].get(usuario)

defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "historico_consultor_imoveis": [],
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 🏠 Consultor de Imóveis IA")
    st.markdown("<div class=\'card\'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** Pela complexidade dos agentes, no computador a experiência é mais agradável.")
    with st.container():
        nome  = st.text_input("Seu Nome:", key="nome_login")
        chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
        arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
        dados_login = json.load(arq_j) if arq_j else None
        if st.button("✨ ENTRAR", key="btn_entrar_login"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 caracteres.")
            elif chave.strip():
                st.session_state.usuario = nome.strip()
                st.session_state.api_key = chave
                if dados_login: carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":
    historico = st.session_state.get("historico_consultor_imoveis", [])
    salvar_perfil_cache(st.session_state.usuario)

    _tab_home_ci, _tab_comprar_alugar, _tab_financiamento, _tab_bairro, _tab_avaliacao_imovel, _tab_contrato_imovel, _tab_armadilhas, _tab_investimento_imovel, _tab_na_planta, _tab_negociacao_imovel, _tab_simulacoes = st.tabs(['🏠 Home', '⚖️ Comprar ou Alugar?', '💰 Calculadora de Financiamento', '📍 Análise de Bairro', '🔍 Avaliação de Imóvel', '📄 Análise de Contrato', '⚠️ Armadilhas Comuns', '📈 Investimento em Imóveis', '🏗️ Imóvel na Planta', '💡 Dicas de Negociação', '📊 Simulações'])

    # ── BARRA SALVAR — aparece em todas as abas ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bsc1, _bsc2 = st.columns(2)
        with _bsc1:
            import json as _jsv
            _dsv = {k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith('_') and k not in ('api_key',)}
            st.download_button("💾 Baixar meus dados (.json)",
                data=_jsv.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"dados_{st.session_state.get('usuario','user')}.json",
                mime="application/json", key="dl_barra_sv_consulto")
        with _bsc2:
            _fupsv = st.file_uploader("📂 Carregar dados salvos:", type=["json"], key="ul_barra_sv_consulto", label_visibility="collapsed")
            if _fupsv:
                try:
                    import json as _jld
                    for _k2,_v2 in _jld.loads(_fupsv.read().decode()).items():
                        if _k2 not in ('api_key','etapa'): st.session_state[_k2] = _v2
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")


    with _tab_home_ci:
        st.title(f"🏠 Olá, {st.session_state.usuario}!")
        st.markdown(f"*Comprar, alugar ou investir? A IA te ajuda a decidir.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"### Bem-vindo ao **Consultor de Imóveis IA**")
        st.markdown(f"<div class='card'>Use as abas acima para navegar entre as funcionalidades. Cada aba oferece uma ferramenta diferente com IA.</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🏠</div><div style='font-size:0.8em;'>Consultor de Imóveis IA</div></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>🤖</div><div style='font-size:0.8em;'>Powered by IA</div></div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div class='stat-box'><div style='font-size:1.8em;'>💾</div><div style='font-size:0.8em;'>Salve seus dados</div></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        col_sv, _ = st.columns([1,3])
        with col_sv:
            st.download_button("💾 Salvar dados (.json)", data=json.dumps({k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k not in ("api_key",)}, ensure_ascii=False, indent=2, default=str), file_name=f"consultor_imoveis_{st.session_state.usuario}.json", mime="application/json", key="dl_consul_1")

    with _tab_comprar_alugar:
        st.header("⚖️ Comprar ou Alugar?")
        prompt_comprar_alugar = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_comprar_alugar", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_comprar_alugar", use_container_width=True):
            if prompt_comprar_alugar.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_comprar_alugar}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_comprar_alugar = resp.choices[0].message.content
                        if resultado_comprar_alugar: st.session_state['res_comprar_alug_consul1'] = str(resultado_comprar_alugar)
                        st.session_state["res_comprar_alugar"] = resultado_comprar_alugar
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Comprar ou Alugar?","resumo":prompt_comprar_alugar[:60],"conteudo":resultado_comprar_alugar})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_comprar_alugar"):
            st.markdown(f"<div class='card'>{st.session_state['res_comprar_alugar']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_comprar_alugar"], file_name="comprar_alugar_resultado.txt", mime="text/plain", key="dl_comprar_alugar")

    with _tab_financiamento:
        st.header("💰 Calculadora de Financiamento")
        prompt_financiamento = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_financiamento", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_financiamento", use_container_width=True):
            if prompt_financiamento.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_financiamento}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_financiamento = resp.choices[0].message.content
                        if resultado_financiamento: st.session_state['res_financiament_consul2'] = str(resultado_financiamento)
                        st.session_state["res_financiamento"] = resultado_financiamento
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Calculadora de Financiamento","resumo":prompt_financiamento[:60],"conteudo":resultado_financiamento})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_financiamento"):
            st.markdown(f"<div class='card'>{st.session_state['res_financiamento']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_financiamento"], file_name="financiamento_resultado.txt", mime="text/plain", key="dl_financiamento")

    with _tab_bairro:
        st.header("📍 Análise de Bairro")
        prompt_bairro = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_bairro", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_bairro", use_container_width=True):
            if prompt_bairro.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_bairro}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_bairro = resp.choices[0].message.content
                        if resultado_bairro: st.session_state['res_bairro_consul3'] = str(resultado_bairro)
                        st.session_state["res_bairro"] = resultado_bairro
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Análise de Bairro","resumo":prompt_bairro[:60],"conteudo":resultado_bairro})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_bairro"):
            st.markdown(f"<div class='card'>{st.session_state['res_bairro']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_bairro"], file_name="bairro_resultado.txt", mime="text/plain", key="dl_bairro")

    with _tab_avaliacao_imovel:
        st.header("🔍 Avaliação de Imóvel")
        prompt_avaliacao_imovel = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_avaliacao_imovel", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_avaliacao_imovel", use_container_width=True):
            if prompt_avaliacao_imovel.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_avaliacao_imovel}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_avaliacao_imovel = resp.choices[0].message.content
                        if resultado_avaliacao_imovel: st.session_state['res_avaliacao_im_consul4'] = str(resultado_avaliacao_imovel)
                        st.session_state["res_avaliacao_imovel"] = resultado_avaliacao_imovel
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Avaliação de Imóvel","resumo":prompt_avaliacao_imovel[:60],"conteudo":resultado_avaliacao_imovel})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_avaliacao_imovel"):
            st.markdown(f"<div class='card'>{st.session_state['res_avaliacao_imovel']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_avaliacao_imovel"], file_name="avaliacao_imovel_resultado.txt", mime="text/plain", key="dl_avaliacao_imovel")

    with _tab_contrato_imovel:
        st.header("📄 Análise de Contrato")
        prompt_contrato_imovel = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_contrato_imovel", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_contrato_imovel", use_container_width=True):
            if prompt_contrato_imovel.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_contrato_imovel}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_contrato_imovel = resp.choices[0].message.content
                        if resultado_contrato_imovel: st.session_state['res_contrato_imo_consul5'] = str(resultado_contrato_imovel)
                        st.session_state["res_contrato_imovel"] = resultado_contrato_imovel
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Análise de Contrato","resumo":prompt_contrato_imovel[:60],"conteudo":resultado_contrato_imovel})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_contrato_imovel"):
            st.markdown(f"<div class='card'>{st.session_state['res_contrato_imovel']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_contrato_imovel"], file_name="contrato_imovel_resultado.txt", mime="text/plain", key="dl_contrato_imovel")

    with _tab_armadilhas:
        st.header("⚠️ Armadilhas Comuns")
        prompt_armadilhas = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_armadilhas", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_armadilhas", use_container_width=True):
            if prompt_armadilhas.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_armadilhas}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_armadilhas = resp.choices[0].message.content
                        if resultado_armadilhas: st.session_state['res_armadilhas_consul6'] = str(resultado_armadilhas)
                        st.session_state["res_armadilhas"] = resultado_armadilhas
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Armadilhas Comuns","resumo":prompt_armadilhas[:60],"conteudo":resultado_armadilhas})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_armadilhas"):
            st.markdown(f"<div class='card'>{st.session_state['res_armadilhas']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_armadilhas"], file_name="armadilhas_resultado.txt", mime="text/plain", key="dl_armadilhas")

    with _tab_investimento_imovel:
        st.header("📈 Investimento em Imóveis")
        prompt_investimento_imovel = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_investimento_imovel", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_investimento_imovel", use_container_width=True):
            if prompt_investimento_imovel.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_investimento_imovel}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_investimento_imovel = resp.choices[0].message.content
                        if resultado_investimento_imovel: st.session_state['res_investimento_consul7'] = str(resultado_investimento_imovel)
                        st.session_state["res_investimento_imovel"] = resultado_investimento_imovel
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Investimento em Imóveis","resumo":prompt_investimento_imovel[:60],"conteudo":resultado_investimento_imovel})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_investimento_imovel"):
            st.markdown(f"<div class='card'>{st.session_state['res_investimento_imovel']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_investimento_imovel"], file_name="investimento_imovel_resultado.txt", mime="text/plain", key="dl_investimento_imovel")

    with _tab_na_planta:
        st.header("🏗️ Imóvel na Planta")
        prompt_na_planta = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_na_planta", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_na_planta", use_container_width=True):
            if prompt_na_planta.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_na_planta}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_na_planta = resp.choices[0].message.content
                        if resultado_na_planta: st.session_state['res_na_planta_consul8'] = str(resultado_na_planta)
                        st.session_state["res_na_planta"] = resultado_na_planta
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Imóvel na Planta","resumo":prompt_na_planta[:60],"conteudo":resultado_na_planta})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_na_planta"):
            st.markdown(f"<div class='card'>{st.session_state['res_na_planta']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_na_planta"], file_name="na_planta_resultado.txt", mime="text/plain", key="dl_na_planta")

    with _tab_negociacao_imovel:
        st.header("💡 Dicas de Negociação")
        prompt_negociacao_imovel = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_negociacao_imovel", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_negociacao_imovel", use_container_width=True):
            if prompt_negociacao_imovel.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_negociacao_imovel}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_negociacao_imovel = resp.choices[0].message.content
                        if resultado_negociacao_imovel: st.session_state['res_negociacao_i_consul9'] = str(resultado_negociacao_imovel)
                        st.session_state["res_negociacao_imovel"] = resultado_negociacao_imovel
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Dicas de Negociação","resumo":prompt_negociacao_imovel[:60],"conteudo":resultado_negociacao_imovel})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_negociacao_imovel"):
            st.markdown(f"<div class='card'>{st.session_state['res_negociacao_imovel']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_negociacao_imovel"], file_name="negociacao_imovel_resultado.txt", mime="text/plain", key="dl_negociacao_imovel")

    with _tab_simulacoes:
        st.header("📊 Simulações")
        prompt_simulacoes = st.text_area("Descreva sua situação ou dúvida:", height=120, key="prompt_simulacoes", placeholder="Digite aqui...")
        if st.button("🤖 GERAR COM IA", key="btn_simulacoes", use_container_width=True):
            if prompt_simulacoes.strip():
                with st.spinner("A IA está analisando..."):
                    try:
                        client = Groq(api_key=st.session_state.api_key)
                        msgs = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt_simulacoes}]
                        resp = client.chat.completions.create(messages=msgs, model="openai/gpt-oss-120b", max_tokens=2048)
                        resultado_simulacoes = resp.choices[0].message.content
                        if resultado_simulacoes: st.session_state['res_simulacoes_consul10'] = str(resultado_simulacoes)
                        st.session_state["res_simulacoes"] = resultado_simulacoes
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Simulações","resumo":prompt_simulacoes[:60],"conteudo":resultado_simulacoes})
                        st.session_state.historico_consultor_imoveis = historico
                    except Exception as e:
                        st.error(f"Erro na API: {e}")
            else:
                st.warning("Digite sua situação antes de gerar.")
        if st.session_state.get("res_simulacoes"):
            st.markdown(f"<div class='card'>{st.session_state['res_simulacoes']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar resultado", data=st.session_state["res_simulacoes"], file_name="simulacoes_resultado.txt", mime="text/plain", key="dl_simulacoes")


# --- RODAPÉ ---
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Consultor de Imóveis IA · Quiz Com Prêmios</div>", unsafe_allow_html=True)
