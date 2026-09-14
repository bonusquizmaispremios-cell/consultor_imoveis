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

SYSTEM_PROMPT = """Você é um consultor imobiliário especialista. Ajuda pessoas a tomar decisões inteligentes sobre compra, venda, aluguel e investimento em imóveis. Explica financiamentos, analisa contratos em linguagem simples e alerta sobre riscos. Nunca garante valorização. Português do Brasil.

REGRA CRÍTICA — NUNCA INVENTE NOMES REAIS:
- NUNCA cite nomes de escolas, hospitais, supermercados, shoppings, ruas ou estabelecimentos específicos de cidades que você não tem certeza absoluta que existem.
- Ao falar de infraestrutura local, use termos GENÉRICOS: "escolas públicas e particulares da região", "comércio local", "hospitais e UPAs", "linhas de ônibus", "praças e parques".
- Se precisar exemplificar, diga EXPLICITAMENTE: "verifique com moradores locais ou no Google Maps a existência de X na região".
- Alucinações com nomes de lugares inexistentes causam dano real ao usuário. Prefira ser genérico e honesto a inventar detalhes locais."""

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
        st.markdown("*Seu consultor imobiliário pessoal — orientação inteligente para cada etapa.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _c1, _c2, _c3 = st.columns(3)
        _c1.markdown("<div class='stat-box'><div style='font-size:2em'>🏠</div><b>Compra e Aluguel</b><br><small>Decisão inteligente</small></div>", unsafe_allow_html=True)
        _c2.markdown("<div class='stat-box'><div style='font-size:2em'>💰</div><b>Financiamento</b><br><small>Simule e compare</small></div>", unsafe_allow_html=True)
        _c3.markdown("<div class='stat-box'><div style='font-size:2em'>📄</div><b>Contratos</b><br><small>Sem juridiquês</small></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("### 🗺️ O que cada aba faz")
        for _ic, _nm, _desc in [
            ("⚖️","Comprar ou Alugar","Responde qual é melhor para seu momento financeiro e de vida"),
            ("💰","Financiamento","Simula parcelas, juros, prazo e compara bancos — você só informa os dados"),
            ("📍","Análise de Bairro","A IA avalia o bairro que você está considerando"),
            ("🔍","Avaliação de Imóvel","Descubra se o preço pedido está justo"),
            ("📄","Análise de Contrato","Cole o contrato e a IA destaca cláusulas perigosas"),
            ("⚠️","Armadilhas Comuns","Os erros mais comuns e como se proteger"),
            ("📈","Investimento","Análise de rentabilidade e riscos reais"),
            ("🏗️","Imóvel na Planta","Tudo que verificar antes de assinar com construtora"),
            ("💡","Negociação","Estratégia para conseguir desconto e melhores condições"),
            ("📊","Simulações","Compare cenários de compra, aluguel e investimento"),
        ]:
            st.markdown(f"**{_ic} {_nm}** — {_desc}")

    with _tab_comprar_alugar:
        st.header("⚖️ Comprar ou Alugar?")
        st.markdown("*Responda as perguntas e a IA decide qual é o melhor caminho para você agora.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _ca1, _ca2 = st.columns(2)
        with _ca1:
            _ca_tempo = st.selectbox("Por quanto tempo pretende ficar no local?", ["Menos de 2 anos","2 a 5 anos","Mais de 5 anos","Não sei ainda"], key="ca_tempo")
            _ca_renda = st.selectbox("Situação financeira atual:", ["Renda estável (CLT/aposentado)","Renda variável (autônomo/freela)","Estou acumulando patrimônio","Tenho reserva mas sem estabilidade"], key="ca_renda")
            _ca_obj = st.selectbox("Seu principal objetivo:", ["Ter minha própria casa","Flexibilidade para mudar","Investir o dinheiro","Não pagar aluguel"], key="ca_obj")
        with _ca2:
            _ca_valor = st.number_input("Valor do imóvel considerado (R$):", min_value=0, value=350000, step=10000, key="ca_valor", format="%d")
            _ca_aluguel = st.number_input("Aluguel equivalente (R$):", min_value=0, value=2000, step=100, key="ca_aluguel", format="%d")
            _ca_entrada = st.number_input("Entrada disponível (R$):", min_value=0, value=70000, step=5000, key="ca_entrada", format="%d")
        _ca_obs = st.text_input("Algum detalhe importante? (opcional):", key="ca_obs", placeholder="Ex: Tenho filho pequeno, moro em SP, já tentei financiamento...")
        if st.button("⚖️ ANALISAR — COMPRAR OU ALUGAR?", key="btn_ca", use_container_width=True):
            _ca_prompt = f"""Analise se é melhor COMPRAR ou ALUGAR:
- Tempo no local: {_ca_tempo}
- Situação financeira: {_ca_renda}
- Objetivo: {_ca_obj}
- Valor do imóvel: R$ {_ca_valor:,.0f}
- Aluguel equivalente: R$ {_ca_aluguel:,.0f}/mês
- Entrada disponível: R$ {_ca_entrada:,.0f}
- Observações: {_ca_obs or "nenhuma"}

Dê recomendação clara (COMPRAR ou ALUGAR), explique o raciocínio financeiro, calcule custo de oportunidade da entrada, e liste prós e contras para este perfil específico."""
            with st.spinner("Analisando seu perfil..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_ca_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_ca_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_ca"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Comprar ou Alugar","resumo":f"R${_ca_valor:,.0f}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_ca"):
            st.markdown(f"<div class='card'>{st.session_state['res_ca']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar análise", data=st.session_state["res_ca"], file_name="comprar_ou_alugar.txt", key="dl_ca")

    with _tab_financiamento:
        st.header("💰 Simulador de Financiamento")
        st.markdown("*Preencha os dados e a IA simula, compara bancos e alerta sobre armadilhas.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _fn1, _fn2 = st.columns(2)
        with _fn1:
            _fn_tipo = st.selectbox("Tipo de imóvel:", ["Apartamento novo","Apartamento usado","Casa nova","Casa usada","Terreno"], key="fn_tipo")
            _fn_valor = st.number_input("Valor do imóvel (R$):", min_value=50000, value=350000, step=10000, key="fn_valor", format="%d")
            _fn_entrada = st.number_input("Entrada disponível (R$):", min_value=0, value=70000, step=5000, key="fn_entrada", format="%d")
            _fn_prazo = st.selectbox("Prazo desejado (anos):", [10,15,20,25,30,35], index=3, key="fn_prazo")
        with _fn2:
            _fn_renda = st.number_input("Renda familiar bruta mensal (R$):", min_value=1000, value=8000, step=500, key="fn_renda", format="%d")
            _fn_sistema = st.selectbox("Sistema de amortização:", ["Não sei — me explique","SAC (parcelas decrescentes)","PRICE (parcelas fixas)"], key="fn_sistema")
            _fn_prog = st.selectbox("Programa habitacional:", ["Não sei","Minha Casa Minha Vida","FGTS","Nenhum"], key="fn_prog")
            _fn_banco = st.selectbox("Preferência de banco?", ["Qualquer — compare para mim","Caixa Econômica","Banco do Brasil","Itaú","Bradesco","Santander"], key="fn_banco")
        _fn_obs = st.text_input("Algum detalhe adicional?", key="fn_obs", placeholder="Ex: Tenho FGTS de R$30mil, nome limpo, já tenho outro imóvel...")
        if st.button("💰 SIMULAR FINANCIAMENTO", key="btn_fn", use_container_width=True):
            _fn_financiado = _fn_valor - _fn_entrada
            _fn_prompt = f"""Simule e analise este financiamento:
- Tipo: {_fn_tipo} | Valor: R$ {_fn_valor:,.0f} | Entrada: R$ {_fn_entrada:,.0f} ({_fn_entrada/_fn_valor*100:.0f}%)
- Financiado: R$ {_fn_financiado:,.0f} | Prazo: {_fn_prazo} anos | Renda: R$ {_fn_renda:,.0f}/mês
- Sistema: {_fn_sistema} | Programa: {_fn_prog} | Banco: {_fn_banco}
- Obs: {_fn_obs or "nenhuma"}

Forneça: 1) Parcela inicial e final estimadas com taxa média de mercado 2) Se o comprometimento de renda está dentro dos 30% 3) Comparativo dos melhores bancos para este perfil 4) Custo total do financiamento 5) Alertas sobre taxas embutidas, seguros e CET 6) Dicas para reduzir o custo"""
            with st.spinner("Simulando..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_fn_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_fn_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_fn"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Financiamento","resumo":f"R${_fn_valor:,.0f}/{_fn_prazo}a","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_fn"):
            st.markdown(f"<div class='card'>{st.session_state['res_fn']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar simulação", data=st.session_state["res_fn"], file_name="financiamento.txt", key="dl_fn")

    with _tab_bairro:
        st.header("📍 Análise de Bairro")
        st.markdown("*Descreva o bairro e a IA avalia pontos positivos, negativos e o que pesquisar antes de decidir.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.info("⚠️ **Atenção:** A análise é baseada em características gerais da região. A IA **não cita nomes reais** de estabelecimentos para evitar informações incorretas. Confirme sempre detalhes locais no Google Maps ou com moradores.")
        _br1, _br2 = st.columns(2)
        with _br1:
            _br_cidade = st.text_input("Cidade:", key="br_cidade", placeholder="Ex: São Paulo, Belo Horizonte...")
            _br_nome = st.text_input("Bairro ou região:", key="br_nome", placeholder="Ex: Lapa, Savassi, Batel...")
            _br_perfil = st.selectbox("Seu perfil:", ["Família com filhos","Jovem profissional","Aposentado","Investidor","Estudante"], key="br_perfil")
        with _br2:
            _br_uso = st.selectbox("Uso do imóvel:", ["Moradia própria","Aluguel para terceiros","Escritório/comercial"], key="br_uso")
            _br_prior = st.multiselect("O que mais importa para você?", ["Segurança","Transporte público","Escolas","Comércio próximo","Silêncio","Valorização","Lazer","Acesso rápido ao trabalho"], default=["Segurança","Transporte público"], key="br_prior")
            _br_m2 = st.text_input("Valor do m² pedido (opcional):", key="br_m2", placeholder="Ex: R$ 8.500/m²")
        _br_obs = st.text_area("Informações extras:", height=70, key="br_obs", placeholder="Ex: Fica perto de avenida movimentada, tem mata ao redor...")
        if st.button("📍 ANALISAR BAIRRO", key="btn_br", use_container_width=True):
            _br_prompt = f"""Analise este bairro para compra/locação:
- Cidade: {_br_cidade} | Bairro: {_br_nome}
- Perfil: {_br_perfil} | Uso: {_br_uso}
- Prioridades: {", ".join(_br_prior)} | Preço m²: {_br_m2 or "não informado"}
- Obs: {_br_obs or "nenhuma"}

Analise: 1) Características típicas da região 2) Pontos fortes e fracos para este perfil 3) Tendência de valorização 4) O que pesquisar ANTES de fechar 5) Infraestrutura e serviços 6) Alertas de risco"""
            with st.spinner("🔍 Buscando informações reais sobre o bairro..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    # Usar compound-beta para busca web real — verifica estabelecimentos que existem
                    _br_prompt_web = f"""Pesquise na web e analise o bairro/região {_br_nome} em {_br_cidade} para {_br_uso}.

Perfil do comprador: {_br_perfil}
Prioridades: {", ".join(_br_prior)}
Preço m²: {_br_m2 or "não informado"}
Observações: {_br_obs or "nenhuma"}

IMPORTANTE: Pesquise na web e cite APENAS estabelecimentos, escolas, hospitais, linhas de transporte e serviços que você VERIFICOU QUE EXISTEM nesta cidade/bairro. Se não encontrar informações verificadas, diga explicitamente "não encontrei dados verificados sobre X — recomendo pesquisar no Google Maps".

Analise: 1) Características reais da região 2) Estabelecimentos verificados (escolas, hospitais, supermercados, transporte) 3) Pontos fortes e fracos para este perfil 4) Tendência de valorização 5) O que pesquisar antes de fechar"""
                    try:
                        # Tentar com compound-beta (tem web search nativo)
                        _r = _client.chat.completions.create(
                            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_br_prompt_web}],
                            model="compound-beta",
                            max_tokens=2048
                        )
                    except:
                        # Fallback: modelo padrão sem web search
                        _r = _client.chat.completions.create(
                            messages=[{"role":"system","content":SYSTEM_PROMPT + " NUNCA invente nomes de estabelecimentos. Use apenas termos genéricos para infraestrutura local."},{"role":"user","content":_br_prompt_web}],
                            model="openai/gpt-oss-120b",
                            max_tokens=2048
                        )
                    _res = _r.choices[0].message.content
                    st.session_state["res_br"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Bairro","resumo":f"{_br_nome}/{_br_cidade}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_br"):
            st.markdown(f"<div class='card'>{st.session_state['res_br']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar análise", data=st.session_state["res_br"], file_name="analise_bairro.txt", key="dl_br")

    with _tab_avaliacao_imovel:
        st.header("🔍 Avaliação de Imóvel")
        st.markdown("*Descreva o imóvel e descubra se o preço pedido está justo.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _av1, _av2 = st.columns(2)
        with _av1:
            _av_tipo = st.selectbox("Tipo:", ["Apartamento","Casa","Terreno","Comercial","Rural"], key="av_tipo")
            _av_cidade = st.text_input("Cidade/Bairro:", key="av_cidade", placeholder="Ex: Campinas - Cambuí")
            _av_area = st.number_input("Área (m²):", min_value=10, value=80, key="av_area")
            _av_quartos = st.selectbox("Quartos:", [1,2,3,4,5], index=1, key="av_quartos")
            _av_vagas = st.selectbox("Vagas de garagem:", [0,1,2,3], key="av_vagas")
        with _av2:
            _av_preco = st.number_input("Preço pedido (R$):", min_value=50000, value=400000, step=10000, key="av_preco", format="%d")
            _av_idade = st.selectbox("Idade do imóvel:", ["Lançamento/Planta","0-5 anos","5-15 anos","15-30 anos","Mais de 30 anos"], key="av_idade")
            _av_estado = st.selectbox("Estado de conservação:", ["Excelente","Bom","Regular — precisa reformas","Precisa reforma completa"], key="av_estado")
            _av_andar = st.text_input("Andar/localização:", key="av_andar", placeholder="Ex: 5º andar, térreo, perto do metrô...")
        _av_dif = st.multiselect("Diferenciais:", ["Piscina","Academia","Portaria 24h","Playground","Área gourmet","Vista privilegiada","Varanda grande","Sol manhã","Alto padrão","Nenhum"], key="av_dif")
        _av_obs = st.text_area("Informações adicionais:", height=70, key="av_obs", placeholder="Ex: Condomínio R$900/mês, IPTU R$2.400/ano, vizinhança tranquila...")
        if st.button("🔍 AVALIAR IMÓVEL", key="btn_av", use_container_width=True):
            _av_m2 = _av_preco / _av_area if _av_area > 0 else 0
            _av_prompt = f"""Avalie se o preço está justo:
- Tipo: {_av_tipo} | Local: {_av_cidade} | Área: {_av_area}m² | Quartos: {_av_quartos} | Vagas: {_av_vagas}
- Preço: R$ {_av_preco:,.0f} (R$ {_av_m2:,.0f}/m²) | Idade: {_av_idade} | Estado: {_av_estado}
- Andar: {_av_andar} | Diferenciais: {", ".join(_av_dif) or "nenhum"}
- Obs: {_av_obs or "nenhuma"}

Avalie: 1) Preço por m² vs mercado 2) Veredicto (ABAIXO/JUSTO/ACIMA) 3) Fatores que justificam ou penalizam 4) Margem de negociação estimada 5) Custos ocultos (ITBI, escritura, reforma) 6) Recomendação final"""
            with st.spinner("Avaliando..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_av_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_av_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_av"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Avaliação","resumo":f"R${_av_preco:,.0f} {_av_cidade}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_av"):
            st.markdown(f"<div class='card'>{st.session_state['res_av']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar avaliação", data=st.session_state["res_av"], file_name="avaliacao.txt", key="dl_av")

    with _tab_contrato_imovel:
        st.header("📄 Análise de Contrato")
        st.markdown("*Cole o contrato — a IA destaca cláusulas perigosas e o que negociar.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _co_tipo = st.selectbox("Tipo de contrato:", ["Compra e Venda","Locação (Aluguel)","Promessa de Compra e Venda","Financiamento bancário","Permuta","Outro"], key="co_tipo")
        _co_texto = st.text_area("Cole o contrato ou os trechos principais:", height=220, key="co_texto", placeholder="Cole aqui as cláusulas, ou os pontos que geraram dúvida...")
        _co_preoc = st.multiselect("O que mais te preocupa?", ["Multas por rescisão","Prazo de entrega","Reajuste","Responsabilidade por reformas","Garantias","Rescisão unilateral","Vícios ocultos","Não sei — analise tudo"], default=["Não sei — analise tudo"], key="co_preoc")
        if st.button("📄 ANALISAR CONTRATO", key="btn_co", use_container_width=True):
            if _co_texto.strip():
                _co_prompt = f"""Analise este contrato de {_co_tipo}:
Preocupações: {", ".join(_co_preoc)}

CONTRATO:
{_co_texto}

Analise: 1) CLÁUSULAS PERIGOSAS (destaque cada uma) 2) O que está FALTANDO 3) O que pode ser NEGOCIADO 4) Multas — são abusivas? 5) Proteção legal ao comprador/locatário 6) Recomendação: ASSINAR / NEGOCIAR ANTES / CONSULTAR ADVOGADO"""
                with st.spinner("Analisando contrato..."):
                    try:
                        _client = Groq(api_key=st.session_state.api_key)
                        try:
                            _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_co_prompt}], model="compound-beta", max_tokens=2048)
                        except:
                            _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_co_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                        _res = _r.choices[0].message.content
                        st.session_state["res_co"] = _res
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Contrato","resumo":_co_tipo,"conteudo":_res})
                        st.session_state.historico_consultor_imoveis = historico
                        st.rerun()
                    except Exception as _e: st.error(f"Erro: {_e}")
            else:
                st.warning("Cole o contrato antes de analisar.")
        if st.session_state.get("res_co"):
            st.markdown(f"<div class='card'>{st.session_state['res_co']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar análise", data=st.session_state["res_co"], file_name="analise_contrato.txt", key="dl_co")

    with _tab_armadilhas:
        st.header("⚠️ Armadilhas Comuns")
        st.markdown("*Selecione seu momento e a IA lista os principais golpes, erros e como se proteger.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _am1, _am2 = st.columns(2)
        with _am1:
            _am_momento = st.selectbox("Em que momento você está?", ["Procurando para comprar","Prestes a assinar compra","Procurando para alugar","Prestes a assinar aluguel","Comprando na planta","Negociando financiamento","Acabei de comprar","Pensando em vender"], key="am_momento")
            _am_tipo = st.selectbox("Tipo de imóvel:", ["Apartamento","Casa","Terreno","Comercial"], key="am_tipo")
        with _am2:
            _am_preoc = st.multiselect("O que mais te preocupa?", ["Golpes e fraudes","Cláusulas abusivas","Documentação irregular","Dívidas escondidas","Construtora problemática","Corretor desonesto","Preço superfaturado","Financiamento com pegadinha"], key="am_preoc")
        if st.button("⚠️ VER ARMADILHAS DO MEU MOMENTO", key="btn_am", use_container_width=True):
            _am_prompt = f"""Liste as principais armadilhas para alguém que está: {_am_momento}
Tipo: {_am_tipo} | Preocupações: {", ".join(_am_preoc) or "geral"}

Para cada armadilha: nome, como acontece, como identificar, como se proteger. Seja específico e prático."""
            with st.spinner("Listando armadilhas..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_am_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_am_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_am"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Armadilhas","resumo":_am_momento,"conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_am"):
            st.markdown(f"<div class='card'>{st.session_state['res_am']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_am"], file_name="armadilhas.txt", key="dl_am")

    with _tab_investimento_imovel:
        st.header("📈 Investimento em Imóveis")
        st.markdown("*Analise a rentabilidade real antes de decidir.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _iv1, _iv2 = st.columns(2)
        with _iv1:
            _iv_tipo = st.selectbox("Tipo de investimento:", ["Comprar para alugar","Comprar para revender","Planta para revenda","FIIs (comparar)","Flipping (compra+reforma+venda)"], key="iv_tipo")
            _iv_valor = st.number_input("Valor do imóvel (R$):", min_value=50000, value=400000, step=10000, key="iv_valor", format="%d")
            _iv_aluguel = st.number_input("Aluguel esperado (R$):", min_value=0, value=2500, step=100, key="iv_aluguel", format="%d")
        with _iv2:
            _iv_condo = st.number_input("Condomínio + IPTU mensal (R$):", min_value=0, value=1200, step=100, key="iv_condo", format="%d")
            _iv_horizonte = st.selectbox("Horizonte de investimento:", ["1-2 anos","3-5 anos","5-10 anos","Mais de 10 anos"], key="iv_horizonte")
            _iv_capital = st.number_input("Capital disponível total (R$):", min_value=0, value=500000, step=10000, key="iv_capital", format="%d")
        _iv_obs = st.text_area("Contexto adicional:", height=70, key="iv_obs", placeholder="Ex: Já tenho imóvel próprio, região em valorização...")
        if st.button("📈 ANALISAR INVESTIMENTO", key="btn_iv", use_container_width=True):
            _iv_yield = (_iv_aluguel - _iv_condo) * 12 / _iv_valor * 100 if _iv_valor > 0 else 0
            _iv_prompt = f"""Analise este investimento imobiliário:
- Tipo: {_iv_tipo} | Valor: R$ {_iv_valor:,.0f} | Aluguel: R$ {_iv_aluguel:,.0f}/mês
- Custos fixos: R$ {_iv_condo:,.0f}/mês | Yield bruto: {_iv_yield:.2f}% a.a.
- Horizonte: {_iv_horizonte} | Capital disponível: R$ {_iv_capital:,.0f}
- Obs: {_iv_obs or "nenhuma"}

Analise: 1) Yield líquido real (vacância, manutenção, IR) 2) Comparação com Selic e FIIs 3) Valorização necessária para superar renda fixa 4) Riscos 5) VALE A PENA ou NÃO para este perfil"""
            with st.spinner("Analisando investimento..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_iv_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_iv_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_iv"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Investimento","resumo":f"R${_iv_valor:,.0f}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_iv"):
            st.markdown(f"<div class='card'>{st.session_state['res_iv']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar análise", data=st.session_state["res_iv"], file_name="investimento.txt", key="dl_iv")

    with _tab_na_planta:
        st.header("🏗️ Imóvel na Planta")
        st.markdown("*Tudo que verificar antes de assinar com a construtora.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _pl1, _pl2 = st.columns(2)
        with _pl1:
            _pl_const = st.text_input("Nome da construtora:", key="pl_const", placeholder="Ex: MRV, Cyrela, construtora local...")
            _pl_preco = st.number_input("Valor total (R$):", min_value=50000, value=350000, step=10000, key="pl_preco", format="%d")
            _pl_entrada = st.number_input("Entrada durante obra (R$):", min_value=0, value=70000, step=5000, key="pl_entrada", format="%d")
        with _pl2:
            _pl_prazo = st.text_input("Prazo de entrega prometido:", key="pl_prazo", placeholder="Ex: Dezembro de 2027")
            _pl_tipo = st.selectbox("Tipo:", ["Apartamento","Casa em condomínio","Loteamento"], key="pl_tipo")
            _pl_fin = st.selectbox("Financiamento após obra:", ["Banco (SBPE)","Minha Casa Minha Vida","Pela construtora","Não definido"], key="pl_fin")
        _pl_preoc = st.multiselect("O que mais te preocupa?", ["Construtora desconhecida","Prazo de entrega","Qualidade do acabamento","Mudança de projeto","O que fazer se atrasar","Distrato — posso desistir?","Parcela após entrega","Documentação do terreno"], key="pl_preoc")
        _pl_obs = st.text_area("Informações adicionais:", height=70, key="pl_obs", placeholder="Ex: Unidade de 58m², 2 quartos, 8º andar...")
        if st.button("🏗️ ANALISAR COMPRA NA PLANTA", key="btn_pl", use_container_width=True):
            _pl_prompt = f"""Analise esta compra na planta:
- Construtora: {_pl_const or "não informada"} | Tipo: {_pl_tipo}
- Valor: R$ {_pl_preco:,.0f} | Entrada: R$ {_pl_entrada:,.0f} | Entrega: {_pl_prazo}
- Financiamento pós-obra: {_pl_fin} | Preocupações: {", ".join(_pl_preoc) or "geral"}
- Obs: {_pl_obs or "nenhuma"}

Oriente: 1) O que verificar ANTES de assinar (RGI, alvará, memorial descritivo) 2) Direitos em caso de atraso (Lei do Distrato) 3) Cláusulas que não podem mudar 4) Riscos desta situação 5) Checklist de documentos 6) Como calcular parcela pós-entrega"""
            with st.spinner("Analisando..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_pl_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_pl_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_pl"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Na Planta","resumo":f"{_pl_const} R${_pl_preco:,.0f}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_pl"):
            st.markdown(f"<div class='card'>{st.session_state['res_pl']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_pl"], file_name="imovel_planta.txt", key="dl_pl")

    with _tab_negociacao_imovel:
        st.header("💡 Estratégia de Negociação")
        st.markdown("*Descreva a situação e a IA monta estratégia para conseguir o melhor preço.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _ng1, _ng2 = st.columns(2)
        with _ng1:
            _ng_preco = st.number_input("Preço pedido (R$):", min_value=10000, value=400000, step=5000, key="ng_preco", format="%d")
            _ng_meta = st.number_input("Quanto você quer pagar (R$):", min_value=10000, value=370000, step=5000, key="ng_meta", format="%d")
            _ng_tempo = st.selectbox("Há quanto tempo está anunciado?", ["Acabou de sair","1-3 meses","3-6 meses","Mais de 6 meses","Não sei"], key="ng_tempo")
        with _ng2:
            _ng_motiv = st.selectbox("Motivação do vendedor:", ["Não sei","Urgência — precisa vender logo","Mudança de cidade","Necessidade financeira","Sem urgência","Inventário/espólio"], key="ng_motiv")
            _ng_pagto = st.selectbox("Forma de pagamento:", ["À vista","Financiamento bancário","FGTS + financiamento","Parcelado com vendedor"], key="ng_pagto")
            _ng_extras = st.multiselect("Além do preço, negociar:", ["Mobília incluída","Pintura nova","Reparos antes da entrega","Prazo de entrega","Isenção de ITBI"], key="ng_extras")
        _ng_obs = st.text_area("Contexto da negociação:", height=70, key="ng_obs", placeholder="Ex: Visitei 3x, dono mora fora, está há 8 meses no mercado...")
        if st.button("💡 MONTAR ESTRATÉGIA DE NEGOCIAÇÃO", key="btn_ng", use_container_width=True):
            _ng_desc = (_ng_preco - _ng_meta) / _ng_preco * 100 if _ng_preco > 0 else 0
            _ng_prompt = f"""Monte estratégia de negociação:
- Preço pedido: R$ {_ng_preco:,.0f} | Meta: R$ {_ng_meta:,.0f} (desconto {_ng_desc:.1f}%)
- Tempo no mercado: {_ng_tempo} | Motivação vendedor: {_ng_motiv}
- Pagamento: {_ng_pagto} | Extras a negociar: {", ".join(_ng_extras) or "só o preço"}
- Contexto: {_ng_obs or "nenhum"}

Forneça: 1) Análise do poder de barganha 2) Estratégia passo a passo 3) Primeira oferta recomendada e justificativa 4) Como apresentar a proposta 5) Como responder contrapropostas 6) Quando aceitar"""
            with st.spinner("Montando estratégia..."):
                try:
                    _client = Groq(api_key=st.session_state.api_key)
                    try:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_ng_prompt}], model="compound-beta", max_tokens=2048)
                    except:
                        _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_ng_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                    _res = _r.choices[0].message.content
                    st.session_state["res_ng"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Negociação","resumo":f"R${_ng_preco:,.0f}→R${_ng_meta:,.0f}","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico
                    st.rerun()
                except Exception as _e: st.error(f"Erro: {_e}")
        if st.session_state.get("res_ng"):
            st.markdown(f"<div class='card'>{st.session_state['res_ng']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar estratégia", data=st.session_state["res_ng"], file_name="negociacao.txt", key="dl_ng")

    with _tab_simulacoes:
        st.header("📊 Simulações Comparativas")
        st.markdown("*Compare cenários lado a lado para tomar a melhor decisão.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _sm_tipo = st.selectbox("O que quer comparar?", [
            "Comprar à vista vs financiado",
            "Comprar vs alugar + investir a diferença",
            "SAC vs PRICE — qual amortização vale mais",
            "Imóvel A vs Imóvel B — qual comprar",
            "Comprar agora vs esperar 2 anos",
            "Vender e alugar vs manter e alugar",
        ], key="sm_tipo")
        _sm_desc = st.text_area("Descreva os cenários com os números:", height=150, key="sm_desc",
            placeholder="Ex: Tenho R$400mil. Opção 1: comprar à vista. Opção 2: dar R$80mil de entrada e financiar em 30 anos com parcela de R$2.800...")
        if st.button("📊 SIMULAR E COMPARAR", key="btn_sm", use_container_width=True):
            if _sm_desc.strip():
                _sm_prompt = f"""Compare estes cenários — tipo: {_sm_tipo}

{_sm_desc}

Simule: 1) Tabela comparativa com números 2) Custo total em 10 e 20 anos 3) Ponto de equilíbrio 4) Vantagens e desvantagens 5) Recomendação clara"""
                with st.spinner("Simulando cenários..."):
                    try:
                        _client = Groq(api_key=st.session_state.api_key)
                        try:
                            _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_sm_prompt}], model="compound-beta", max_tokens=2048)
                        except:
                            _r = _client.chat.completions.create(messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":_sm_prompt}], model="openai/gpt-oss-120b", max_tokens=2048)
                        _res = _r.choices[0].message.content
                        st.session_state["res_sm"] = _res
                        historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Simulação","resumo":_sm_tipo,"conteudo":_res})
                        st.session_state.historico_consultor_imoveis = historico
                        st.rerun()
                    except Exception as _e: st.error(f"Erro: {_e}")
            else:
                st.warning("Descreva os cenários antes de simular.")
        if st.session_state.get("res_sm"):
            st.markdown(f"<div class='card'>{st.session_state['res_sm']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar simulação", data=st.session_state["res_sm"], file_name="simulacao.txt", key="dl_sm")

# --- RODAPÉ ---
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Consultor de Imóveis IA · Quiz Com Prêmios</div>", unsafe_allow_html=True)
