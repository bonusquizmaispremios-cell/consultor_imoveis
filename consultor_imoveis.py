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
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#7DD3FC,transparent); margin:18px 0; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #7DD3FC; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item div { color:#0C4A6E !important; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #7DD3FC; }
    .stApp .stat-box div, .stApp .stat-box span { color:#0C4A6E !important; }
    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """Você é um Consultor Imobiliário IA especializado no mercado brasileiro.
Sua prioridade absoluta é precisão, transparência e segurança das informações.

REGRAS OBRIGATÓRIAS:
1. NUNCA invente valores de imóveis, bairros, ruas, distâncias, índices, taxas, leis ou informações sobre cidades.
2. Diferencie claramente: dado do usuário / cálculo do sistema / estimativa / opinião.
3. Quando depender de dados atuais, informe que é necessário consultar fonte atualizada.
4. NUNCA afirme que imóvel está barato/caro sem explicar a metodologia.
5. NUNCA diga que cláusula é ilegal definitivamente sem ressalvar que não substitui advogado.
6. Quando não tiver dados suficientes, diga: "Não tenho informações suficientes para afirmar isso."
7. NUNCA crie referências, links ou nomes de fontes inexistentes.
8. Sempre informe grau de confiança: 🟢 Alto (dados objetivos) / 🟡 Médio (estimativas) / 🔴 Baixo (faltam dados).
9. NUNCA invente nomes de estabelecimentos locais. Se não verificou, não cita.
10. Evite: "Com certeza", "Esse bairro é seguro", "Esse banco tem a menor taxa".
    Prefira: "Os indicadores sugerem...", "É necessário confirmar...", "Não encontrei dados verificados."

COMPORTAMENTO: É preferível admitir limitação do que fornecer informação incorreta.
Sempre mostre premissas, metodologia, diferencie fato de estimativa, apresente riscos."""

# ══ MOTOR DE CÁLCULOS — Python puro, sem IA ══
def calcular_sac(valor, prazo_meses, taxa_anual):
    taxa = (1+taxa_anual/100)**(1/12)-1
    amort = valor/prazo_meses
    parcelas, saldo = [], valor
    for i in range(prazo_meses):
        j = saldo*taxa
        parcelas.append({"mes":i+1,"parcela":amort+j,"amort":amort,"juros":j,"saldo":max(0,saldo-amort)})
        saldo -= amort
    return parcelas

def calcular_price(valor, prazo_meses, taxa_anual):
    taxa = (1+taxa_anual/100)**(1/12)-1
    p = valor*(taxa*(1+taxa)**prazo_meses)/((1+taxa)**prazo_meses-1) if taxa>0 else valor/prazo_meses
    parcelas, saldo = [], valor
    for i in range(prazo_meses):
        j = saldo*taxa; a = p-j
        parcelas.append({"mes":i+1,"parcela":p,"amort":a,"juros":j,"saldo":max(0,saldo-a)})
        saldo -= a
    return parcelas

def custo_total_compra(valor_imovel):
    itbi = valor_imovel*0.02
    escritura = 1500 if valor_imovel<=200000 else valor_imovel*0.008 if valor_imovel<=500000 else valor_imovel*0.006
    registro = valor_imovel*0.01
    return {"itbi":itbi,"escritura":escritura,"registro":registro,
            "total_extras":itbi+escritura+registro,"total_geral":valor_imovel+itbi+escritura+registro}

def roi_imovel(valor, aluguel_mensal, custos_mensais, vacancia_pct=5):
    liq = aluguel_mensal*(1-vacancia_pct/100)-custos_mensais
    anual = liq*12
    cap = anual/valor*100 if valor>0 else 0
    pay = valor/anual if anual>0 else 0
    return {"receita_anual":anual,"cap_rate":cap,"yield_mensal":cap/12,"payback_anos":pay}

def chamar_ia(prompt, sistema=None):
    try:
        client = Groq(api_key=st.session_state.api_key)
        sys = sistema or SYSTEM_PROMPT
        try:
            r = client.chat.completions.create(
                messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
                model="compound-beta", max_tokens=2500)
        except:
            r = client.chat.completions.create(
                messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
                model="openai/gpt-oss-120b", max_tokens=2048)
        return r.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"

@st.cache_resource
def get_cache(): return {"perfis": {}}
_cache = get_cache()

def carregar_json_sessao(dados):
    _bloq = {'api_key','etapa','nome_login','chave_login','upload_login','btn_entrar_login'}
    _pref = ('btn_','sel_','ul_','dl_','_sub','_tab','_bsc','ca_','fn_','ct_','br_',
             'av_','co_','doc_','iv_','pl_','am_','ng_','sm_','cmp_')
    import re as _re
    for k,v in dados.items():
        if k in _bloq: continue
        if any(k.startswith(p) for p in _pref): continue
        if _re.match(r'.+_?\d+$', k): continue
        st.session_state[k] = v

defaults = {
    "etapa":"Login","usuario":"","api_key":"",
    "historico_consultor_imoveis":[],"imoveis_comp":[],
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 🏠 Consultor de Imóveis IA")
    st.markdown("<div class='card'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** No computador a experiência é mais agradável.")
    nome  = st.text_input("Seu Nome:", key="nome_login")
    chave = st.text_input("🔑 Chave API da Groq:", type="password", key="chave_login")
    arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
    if st.button("✨ ENTRAR", key="btn_entrar_login"):
        if len(nome.strip()) < 2: st.warning("Nome muito curto.")
        elif chave.strip():
            st.session_state.usuario = nome.strip()
            st.session_state.api_key = chave
            if arq_j: carregar_json_sessao(json.load(arq_j))
            st.session_state.etapa = "App"; st.rerun()
        else: st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":
    historico = st.session_state.get("historico_consultor_imoveis", [])

    (_tab_home_ci, _tab_ca, _tab_fn, _tab_ct,
     _tab_bairro, _tab_av, _tab_cmp,
     _tab_co, _tab_doc,
     _tab_iv, _tab_pl,
     _tab_am, _tab_ng, _tab_sm) = st.tabs([
        "🏠 Home", "⚖️ Comprar ou Alugar", "💰 Financiamento", "💸 Custo Total",
        "📍 Raio-X Bairro", "🔍 Avaliador", "🆚 Comparador",
        "📄 Contrato", "📋 Documentação",
        "📈 Investimento", "🏗️ Na Planta",
        "⚠️ Armadilhas", "💡 Negociação", "📊 Simulações"
    ])

    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bs1, _bs2 = st.columns(2)
        with _bs1:
            _dsv = {k:st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith("_") and k!="api_key"}
            st.download_button("💾 Baixar (.json)", data=json.dumps(_dsv,ensure_ascii=False,indent=2,default=str),
                file_name=f"imoveis_{st.session_state.get('usuario','user')}.json", mime="application/json", key="dl_sv_ci")
        with _bs2:
            _fup = st.file_uploader("📂 Carregar:", type=["json"], key="ul_sv_ci", label_visibility="collapsed")
            if _fup:
                try:
                    for _k2,_v2 in json.loads(_fup.read().decode()).items():
                        if _k2 not in ("api_key","etapa"): st.session_state[_k2]=_v2
                    st.success("✅ Restaurado!"); st.rerun()
                except: st.error("Arquivo inválido.")

    # ══ HOME ══
    with _tab_home_ci:
        st.title("🏠 Consultor de Imóveis IA")
        st.markdown(f"*Olá, {st.session_state.usuario}! Análise com dados reais, cálculos precisos e total transparência.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("""<div class='card-yellow'>⚠️ <b>Compromisso de transparência:</b> Este consultor diferencia
        <b>dados fornecidos por você</b>, <b>cálculos matemáticos em Python</b> e <b>estimativas da IA</b>.
        Quando não houver dados suficientes, a IA diz claramente. Nunca inventará valores ou nomes.</div>""", unsafe_allow_html=True)
        _hc1,_hc2,_hc3,_hc4 = st.columns(4)
        _hc1.markdown("<div class='stat-box'>🔢<br><b>Python</b><br><small>SAC, PRICE, ROI</small></div>", unsafe_allow_html=True)
        _hc2.markdown("<div class='stat-box'>🔍<br><b>Web Search</b><br><small>Dados verificados</small></div>", unsafe_allow_html=True)
        _hc3.markdown("<div class='stat-box'>🟢<br><b>Confiança</b><br><small>Indicada em cada resposta</small></div>", unsafe_allow_html=True)
        _hc4.markdown("<div class='stat-box'>📋<br><b>Checklists</b><br><small>Documentação completa</small></div>", unsafe_allow_html=True)
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        for _grp,_items in [
            ("💰 DECISÃO DE COMPRA",["⚖️ Comprar ou Alugar — análise financeira com cálculo de oportunidade","💰 Financiamento — SAC e PRICE calculados em Python + análise da IA","💸 Custo Total — ITBI, escritura, registro, reforma, mudança","📊 Simulações — compare cenários lado a lado"]),
            ("📍 LOCALIZAÇÃO",["📍 Raio-X do Bairro — busca web real, cita apenas o verificado","🔍 Avaliador — faixa de valor com metodologia transparente","🆚 Comparador — até 3 imóveis com ranking automático"]),
            ("📄 SEGURANÇA JURÍDICA",["📄 Contrato — checklist jurídico com 🟢🟡🔴","📋 Documentação — checklist por tipo de operação"]),
            ("📈 INVESTIMENTO",["📈 Rentabilidade — ROI, Cap Rate, yield vs Selic calculados em Python","🏗️ Na Planta — checklist + pesquisa da construtora na web"]),
            ("💡 NEGOCIAÇÃO",["⚠️ Armadilhas — erros do seu momento específico","💡 Negociação — estratégia passo a passo"]),
        ]:
            st.markdown(f"**{_grp}**")
            for _i in _items: st.markdown(f"&nbsp;&nbsp;&nbsp;• {_i}")

    # ══ COMPRAR OU ALUGAR ══
    with _tab_ca:
        st.header("⚖️ Comprar ou Alugar?")
        st.markdown("*Análise financeira personalizada — o sistema calcula, a IA explica.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _ca1,_ca2 = st.columns(2)
        with _ca1:
            _ca_tempo = st.selectbox("Tempo pretendido no local:", ["Menos de 2 anos","2 a 5 anos","Mais de 5 anos","Não sei ainda"], key="ca_tempo")
            _ca_renda = st.selectbox("Situação financeira:", ["Renda estável (CLT/aposentado)","Renda variável (autônomo)","Acumulando patrimônio","Tenho reserva mas sem estabilidade"], key="ca_renda")
            _ca_obj = st.selectbox("Objetivo principal:", ["Ter minha própria casa","Flexibilidade para mudar","Investir o patrimônio","Parar de pagar aluguel"], key="ca_obj")
        with _ca2:
            _ca_valor = st.number_input("Valor do imóvel (R$):", min_value=0, value=350000, step=10000, key="ca_valor", format="%d")
            _ca_aluguel = st.number_input("Aluguel equivalente (R$/mês):", min_value=0, value=2000, step=100, key="ca_aluguel", format="%d")
            _ca_entrada = st.number_input("Entrada disponível (R$):", min_value=0, value=70000, step=5000, key="ca_entrada", format="%d")
            _ca_rentab = st.number_input("Rentabilidade aplicação (% a.a.):", min_value=0.0, value=13.0, step=0.5, key="ca_rentab")
        if _ca_valor > 0 and _ca_entrada > 0:
            _ca_custo = custo_total_compra(_ca_valor)
            _ca_rend_m = _ca_entrada*(_ca_rentab/100/12)
            st.markdown(f"<div class='card-blue'>📊 <b>Cálculo Python:</b> Financiado: <b>R$ {_ca_valor-_ca_entrada:,.0f}</b> | Extras compra: <b>R$ {_ca_custo['total_extras']:,.0f}</b> | Rend. mensal da entrada: <b>R$ {_ca_rend_m:,.0f}</b></div>", unsafe_allow_html=True)
        _ca_obs = st.text_input("Detalhe adicional:", key="ca_obs", placeholder="Ex: Tenho filho pequeno, moro em SP...")
        if st.button("⚖️ ANALISAR", key="btn_ca", use_container_width=True):
            _ca_p = f"""Analise COMPRAR ou ALUGAR com base nos dados:
- Tempo: {_ca_tempo} | Renda: {_ca_renda} | Objetivo: {_ca_obj}
- Imóvel: R$ {_ca_valor:,.0f} | Aluguel: R$ {_ca_aluguel:,.0f}/mês | Entrada: R$ {_ca_entrada:,.0f}
- Rentabilidade alternativa: {_ca_rentab}% a.a.
CÁLCULOS PYTHON: Financiado R$ {_ca_valor-_ca_entrada:,.0f} | Extras R$ {custo_total_compra(_ca_valor)['total_extras']:,.0f} | Rend. mensal entrada R$ {_ca_entrada*(_ca_rentab/100/12):,.0f}
Obs: {_ca_obs or "nenhuma"}
Forneça: 1) RECOMENDAÇÃO CLARA com justificativa 2) Cenários 5 e 10 anos 3) Prós/contras para este perfil 4) 🟢/🟡/🔴 grau de confiança"""
            with st.spinner("Analisando..."):
                _res = chamar_ia(_ca_p)
                st.session_state["res_ca"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Comprar/Alugar","resumo":f"R${_ca_valor:,.0f}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_ca"):
            st.markdown(f"<div class='card'>{st.session_state['res_ca']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_ca"], file_name="comprar_alugar.txt", key="dl_ca")

    # ══ FINANCIAMENTO ══
    with _tab_fn:
        st.header("💰 Calculadora de Financiamento")
        st.markdown("*Cálculos SAC e PRICE em Python puro — a IA interpreta os resultados.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.info("🔢 Os cálculos são feitos em Python. A IA apenas interpreta e orienta.")
        _fn1,_fn2 = st.columns(2)
        with _fn1:
            _fn_tipo = st.selectbox("Tipo:", ["Apartamento novo","Apartamento usado","Casa nova","Casa usada","Terreno"], key="fn_tipo")
            _fn_valor = st.number_input("Valor do imóvel (R$):", min_value=50000, value=350000, step=10000, key="fn_valor", format="%d")
            _fn_entrada = st.number_input("Entrada (R$):", min_value=0, value=70000, step=5000, key="fn_entrada", format="%d")
            _fn_prazo = st.selectbox("Prazo (anos):", [10,15,20,25,30,35], index=3, key="fn_prazo")
        with _fn2:
            _fn_taxa = st.number_input("Taxa de juros (% a.a.):", min_value=1.0, value=10.5, step=0.1, key="fn_taxa")
            _fn_sistema = st.selectbox("Sistema:", ["SAC (parcelas decrescentes)","PRICE (parcelas fixas)","Comparar SAC vs PRICE"], key="fn_sistema")
            _fn_renda = st.number_input("Renda familiar bruta (R$/mês):", min_value=1000, value=8000, step=500, key="fn_renda", format="%d")
            _fn_banco = st.selectbox("Banco:", ["Informado pelo usuário","Caixa Econômica","Banco do Brasil","Itaú","Bradesco","Santander"], key="fn_banco")
        _fn_financiado = max(0, _fn_valor - _fn_entrada)
        _fn_meses = _fn_prazo * 12
        if _fn_financiado > 0 and _fn_taxa > 0:
            if "SAC" in _fn_sistema or "Comparar" in _fn_sistema:
                _sac = calcular_sac(_fn_financiado, _fn_meses, _fn_taxa)
                _s1,_su,_st = _sac[0]["parcela"],_sac[-1]["parcela"],sum(p["parcela"] for p in _sac)
            if "PRICE" in _fn_sistema or "Comparar" in _fn_sistema:
                _prc = calcular_price(_fn_financiado, _fn_meses, _fn_taxa)
                _pp,_pt = _prc[0]["parcela"],sum(p["parcela"] for p in _prc)
            _ce = custo_total_compra(_fn_valor)
            _p1 = _s1 if "SAC" in _fn_sistema else _pp
            _comp = _p1/_fn_renda*100
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("### 🔢 Resultados (Python)")
            if "Comparar" in _fn_sistema:
                _rc1,_rc2 = st.columns(2)
                with _rc1: st.markdown(f"<div class='card-green'><b>📉 SAC</b><br>1ª parcela: <b>R$ {_s1:,.2f}</b><br>Última: <b>R$ {_su:,.2f}</b><br>Total: <b>R$ {_st:,.2f}</b><br>Juros: <b>R$ {_st-_fn_financiado:,.2f}</b></div>", unsafe_allow_html=True)
                with _rc2: st.markdown(f"<div class='card-blue'><b>📊 PRICE</b><br>Parcela fixa: <b>R$ {_pp:,.2f}</b><br>Total: <b>R$ {_pt:,.2f}</b><br>Juros: <b>R$ {_pt-_fn_financiado:,.2f}</b><br>A mais que SAC: <b>R$ {_pt-_st:,.2f}</b></div>", unsafe_allow_html=True)
            elif "SAC" in _fn_sistema:
                st.markdown(f"<div class='card-green'><b>📉 SAC</b> | R$ {_fn_financiado:,.0f} | {_fn_taxa}% a.a. | {_fn_prazo} anos<br>1ª parcela: <b>R$ {_s1:,.2f}</b> | Última: <b>R$ {_su:,.2f}</b> | Total: <b>R$ {_st:,.2f}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='card-blue'><b>📊 PRICE</b> | Parcela fixa: <b>R$ {_pp:,.2f}</b> | Total: <b>R$ {_pt:,.2f}</b></div>", unsafe_allow_html=True)
            _cc = "card-green" if _comp<=30 else ("card-yellow" if _comp<=35 else "card-red")
            _ic = "✅" if _comp<=30 else ("⚠️" if _comp<=35 else "🚨")
            st.markdown(f"<div class='{_cc}'>{_ic} Comprometimento de renda: <b>{_comp:.1f}%</b> (limite: 30%) | Custos extras: <b>R$ {_ce['total_extras']:,.0f}</b></div>", unsafe_allow_html=True)
            st.caption("⚠️ Simulação com a taxa informada. Valores reais dependem do banco, análise de crédito e seguros.")
            _fn_obs = st.text_input("Observações:", key="fn_obs", placeholder="Ex: Tenho FGTS R$30mil, nome limpo...")
            if st.button("🤖 ANÁLISE DA IA", key="btn_fn", use_container_width=True):
                _fn_calc = f"SAC: 1ª R${_s1:,.0f}/última R${_su:,.0f}/total R${_st:,.0f}" if "SAC" in _fn_sistema or "Comparar" in _fn_sistema else ""
                _fn_calc += f" | PRICE: R${_pp:,.0f}/mês/total R${_pt:,.0f}" if "PRICE" in _fn_sistema or "Comparar" in _fn_sistema else ""
                _fn_p = f"""Interprete os resultados do financiamento:
DADOS: {_fn_tipo} | R${_fn_valor:,.0f} | Entrada R${_fn_entrada:,.0f} | {_fn_prazo}a | {_fn_taxa}%a.a. | Renda R${_fn_renda:,.0f}/mês | Banco: {_fn_banco}
CÁLCULOS PYTHON: {_fn_calc} | Comprometimento: {_comp:.1f}% | Custos extras: R${_ce['total_extras']:,.0f}
Obs: {_fn_obs or "nenhuma"}
Analise: 1) Adequação do comprometimento 2) SAC vs PRICE — qual indicado 3) Taxas ocultas (seguros MIP/DFI) 4) Dicas para reduzir custo 5) Sobre {_fn_banco}: só o que tiver certeza 6) 🟢/🟡/🔴"""
                with st.spinner("Analisando..."):
                    _res = chamar_ia(_fn_p)
                    st.session_state["res_fn"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Financiamento","resumo":f"R${_fn_valor:,.0f}/{_fn_prazo}a/{_fn_taxa}%","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico; st.rerun()
            if st.session_state.get("res_fn"):
                st.markdown(f"<div class='card'>{st.session_state['res_fn']}</div>", unsafe_allow_html=True)
                st.download_button("📋 Baixar", data=st.session_state["res_fn"], file_name="financiamento.txt", key="dl_fn")

    # ══ CUSTO TOTAL ══
    with _tab_ct:
        st.header("💸 Custo Total da Compra")
        st.markdown("*Quanto você REALMENTE vai gastar além do preço do imóvel.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.info("🔢 Todos os valores calculados em Python. A IA comenta e orienta.")
        _ct1,_ct2 = st.columns(2)
        with _ct1:
            _ct_valor = st.number_input("Valor do imóvel (R$):", min_value=50000, value=400000, step=10000, key="ct_valor", format="%d")
            _ct_entrada = st.number_input("Entrada (R$):", min_value=0, value=80000, step=5000, key="ct_entrada", format="%d")
            _ct_reforma = st.number_input("Reforma estimada (R$):", min_value=0, value=0, step=5000, key="ct_reforma", format="%d")
        with _ct2:
            _ct_moveis = st.number_input("Móveis/Eletrodomésticos (R$):", min_value=0, value=0, step=1000, key="ct_moveis", format="%d")
            _ct_mudanca = st.number_input("Mudança (R$):", min_value=0, value=2000, step=500, key="ct_mudanca", format="%d")
            _ct_estado = st.selectbox("Estado:", ["MG","SP","RJ","RS","PR","SC","BA","GO","DF","Outro"], key="ct_estado")
        _ct_c = custo_total_compra(_ct_valor)
        _ct_extras = _ct_c["total_extras"]+_ct_reforma+_ct_moveis+_ct_mudanca
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"""<div class='card'>
        <b>💰 Detalhamento dos Custos</b><br><br>
        🏠 Imóvel: <b>R$ {_ct_valor:,.0f}</b><br>
        📋 ITBI (~2%): <b>R$ {_ct_c['itbi']:,.0f}</b><br>
        📝 Escritura: <b>R$ {_ct_c['escritura']:,.0f}</b><br>
        🏛️ Registro (~1%): <b>R$ {_ct_c['registro']:,.0f}</b><br>
        🔨 Reforma: <b>R$ {_ct_reforma:,.0f}</b><br>
        🛋️ Móveis/Eletro: <b>R$ {_ct_moveis:,.0f}</b><br>
        🚚 Mudança: <b>R$ {_ct_mudanca:,.0f}</b><br><br>
        💰 <b>TOTAL GERAL: R$ {_ct_c['total_geral']+_ct_reforma+_ct_moveis+_ct_mudanca:,.0f}</b><br>
        💳 Além da entrada, precisa de: <b>R$ {_ct_extras:,.0f}</b>
        </div>""", unsafe_allow_html=True)
        st.caption("⚠️ ITBI varia por município (2-3%). Confirme na Prefeitura e Cartório.")
        if st.button("🤖 ORIENTAÇÃO DA IA", key="btn_ct", use_container_width=True):
            _ct_p = f"""Oriente sobre custos de compra de imóvel R$ {_ct_valor:,.0f} no estado {_ct_estado}.
CALCULADOS PYTHON: ITBI R${_ct_c['itbi']:,.0f} | Escritura R${_ct_c['escritura']:,.0f} | Registro R${_ct_c['registro']:,.0f} | Extras totais R${_ct_extras:,.0f}
Oriente: 1) Como confirmar ITBI exato no município 2) Isenções possíveis (primeiro imóvel, MCMV) 3) Custos que as pessoas esquecem 4) Como planejar o fluxo de caixa 5) 🟢/🟡/🔴"""
            with st.spinner("Orientando..."):
                _res = chamar_ia(_ct_p)
                st.session_state["res_ct"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Custo Total","resumo":f"R${_ct_valor:,.0f}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_ct"):
            st.markdown(f"<div class='card'>{st.session_state['res_ct']}</div>", unsafe_allow_html=True)

    # ══ RAIO-X BAIRRO ══
    with _tab_bairro:
        st.header("📍 Raio-X do Bairro")
        st.markdown("*Busca web real — a IA cita apenas o que verificou. Se não encontrou, diz claramente.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.warning("⚠️ A IA pesquisa na web e cita apenas estabelecimentos verificados. Se não encontrar, orienta como você pode confirmar.")
        _br1,_br2 = st.columns(2)
        with _br1:
            _br_cidade = st.text_input("Cidade:", key="br_cidade", placeholder="Ex: Betim")
            _br_estado = st.text_input("Estado:", key="br_estado", placeholder="Ex: MG", max_chars=2)
            _br_nome = st.text_input("Bairro:", key="br_nome", placeholder="Ex: Brasília")
            _br_end = st.text_input("Endereço de referência:", key="br_end", placeholder="Ex: Rua das Flores, 100")
        with _br2:
            _br_perfil = st.selectbox("Perfil:", ["Família com filhos","Jovem profissional","Aposentado","Investidor","Estudante"], key="br_perfil")
            _br_uso = st.selectbox("Uso:", ["Moradia própria","Aluguel para terceiros","Comercial"], key="br_uso")
            _br_prior = st.multiselect("Prioridades:", ["Segurança","Transporte público","Escolas","Saúde","Comércio","Silêncio","Valorização","Lazer"], default=["Segurança","Transporte público"], key="br_prior")
        if st.button("🔍 RAIO-X DO BAIRRO", key="btn_br", use_container_width=True):
            _loc = f"bairro {_br_nome}, {_br_cidade}/{_br_estado}"
            _br_p = f"""Você tem busca web. PESQUISE AGORA sobre {_loc}:

1. Busque: "escolas {_br_nome} {_br_cidade} {_br_estado}" → liste NOMES REAIS encontrados
2. Busque: "supermercado {_br_nome} {_br_cidade}" → liste NOMES REAIS encontrados
3. Busque: "hospital UBS posto saúde {_br_nome} {_br_cidade}" → liste o que encontrou
4. Busque: "ônibus transporte {_br_cidade} {_br_nome}" → informe linhas reais se encontrar
5. Busque: "imóveis {_br_nome} {_br_cidade} preço m²" → faixa de preço se encontrar
6. Busque: "bairro {_br_nome} {_br_cidade} valorização" → tendências encontradas

Perfil: {_br_perfil} | Uso: {_br_uso} | Prioridades: {", ".join(_br_prior)}
Endereço: {_br_end or "não informado"}

REGRAS ABSOLUTAS:
- Cite APENAS nomes verificados na busca
- Se não encontrou: "Não encontrei dados verificados sobre [X] em {_loc} — pesquise no Google Maps: '[X] {_br_nome} {_br_cidade}'"
- NUNCA escreva "tipicamente tem" ou "costuma ter" sem fonte verificada
- Informe fontes encontradas e 🟢/🟡/🔴"""
            with st.spinner(f"🔍 Pesquisando {_loc}..."):
                _res = chamar_ia(_br_p)
                st.session_state["res_br"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Bairro","resumo":f"{_br_nome}/{_br_cidade}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_br"):
            st.markdown(f"<div class='card'>{st.session_state['res_br']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_br"], file_name="raio_x_bairro.txt", key="dl_br")

    # ══ AVALIADOR ══
    with _tab_av:
        st.header("🔍 Avaliador Inteligente")
        st.markdown("*Faixa de valor estimada com metodologia transparente.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _av1,_av2 = st.columns(2)
        with _av1:
            _av_tipo = st.selectbox("Tipo:", ["Apartamento","Casa","Terreno","Comercial","Rural"], key="av_tipo")
            _av_cidade = st.text_input("Cidade/Bairro:", key="av_cidade", placeholder="Ex: Betim - Centro")
            _av_area = st.number_input("Área (m²):", min_value=10, value=80, key="av_area")
            _av_quartos = st.selectbox("Quartos:", [1,2,3,4,5], index=1, key="av_quartos")
            _av_vagas = st.selectbox("Vagas:", [0,1,2,3], key="av_vagas")
        with _av2:
            _av_preco = st.number_input("Preço pedido (R$):", min_value=50000, value=400000, step=10000, key="av_preco", format="%d")
            _av_idade = st.selectbox("Idade:", ["Lançamento","0-5 anos","5-15 anos","15-30 anos","Mais de 30 anos"], key="av_idade")
            _av_estado = st.selectbox("Conservação:", ["Excelente","Bom","Regular","Precisa reforma completa"], key="av_estado")
            _av_condo = st.number_input("Condomínio (R$/mês):", min_value=0, value=0, key="av_condo", format="%d")
            _av_iptu = st.number_input("IPTU anual (R$):", min_value=0, value=0, key="av_iptu", format="%d")
        _av_dif = st.multiselect("Diferenciais:", ["Piscina","Academia","Portaria 24h","Área gourmet","Vista privilegiada","Varanda grande","Alto padrão","Nenhum"], key="av_dif")
        _av_obs = st.text_area("Informações adicionais:", height=60, key="av_obs", placeholder="Ex: 5º andar, reformado 2022, próximo ao metrô...")
        _av_m2 = _av_preco/_av_area if _av_area>0 else 0
        st.markdown(f"<div class='card-blue'>📊 <b>Cálculo Python:</b> Preço/m²: <b>R$ {_av_m2:,.0f}/m²</b> | Custo mensal extra: <b>R$ {_av_condo+_av_iptu/12:,.0f}</b></div>", unsafe_allow_html=True)
        if st.button("🔍 AVALIAR", key="btn_av", use_container_width=True):
            _av_p = f"""Avalie este imóvel com transparência metodológica:
{_av_tipo} | {_av_cidade} | {_av_area}m² | {_av_quartos}qts | {_av_vagas}vagas
Preço: R$ {_av_preco:,.0f} (R$ {_av_m2:,.0f}/m² — calculado Python) | Idade: {_av_idade} | Estado: {_av_estado}
Condo: R$ {_av_condo}/mês | IPTU: R$ {_av_iptu}/ano | Dif: {", ".join(_av_dif) or "nenhum"}
Obs: {_av_obs or "nenhuma"}
PESQUISE preço médio m² em {_av_cidade} para este tipo. Analise:
1) Veredicto: ABAIXO/JUSTO/ACIMA — com metodologia explicada
2) Fatores que valorizam ou penalizam
3) Margem de negociação estimada e justificativa
4) Custo total mensal (parcela + condo + IPTU)
5) 🟢/🟡/🔴 — seja honesto sobre limitações da análise remota"""
            with st.spinner("Avaliando..."):
                _res = chamar_ia(_av_p)
                st.session_state["res_av"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Avaliação","resumo":f"R${_av_preco:,.0f} {_av_cidade}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_av"):
            st.markdown(f"<div class='card'>{st.session_state['res_av']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_av"], file_name="avaliacao.txt", key="dl_av")

    # ══ COMPARADOR ══
    with _tab_cmp:
        st.header("🆚 Comparador de Imóveis")
        st.markdown("*Cadastre até 3 imóveis — ranking automático por custo-benefício.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        if "imoveis_comp" not in st.session_state: st.session_state["imoveis_comp"] = []
        _ci = st.session_state["imoveis_comp"]
        st.markdown("### ➕ Adicionar Imóvel")
        _cm1,_cm2,_cm3 = st.columns(3)
        with _cm1:
            _cn = st.text_input("Identificação:", key="cmp_nome", placeholder="Ex: Ap Centro")
            _cv = st.number_input("Preço (R$):", min_value=10000, value=350000, step=5000, key="cmp_valor", format="%d")
            _ca2 = st.number_input("Área (m²):", min_value=10, value=80, key="cmp_area")
        with _cm2:
            _cb = st.text_input("Bairro/Cidade:", key="cmp_bairro")
            _cq = st.selectbox("Quartos:", [1,2,3,4,5], index=1, key="cmp_quartos")
            _cvg = st.selectbox("Vagas:", [0,1,2,3], key="cmp_vagas")
        with _cm3:
            _cco = st.number_input("Condomínio (R$):", min_value=0, value=500, key="cmp_condo", format="%d")
            _ces = st.selectbox("Conservação:", ["Excelente","Bom","Regular","Reforma"], key="cmp_estado")
            _cob = st.text_input("Diferencial:", key="cmp_obs")
        if st.button("➕ ADICIONAR", key="btn_cmp_add", use_container_width=True):
            if len(_ci)>=3: st.warning("Máximo 3 imóveis.")
            elif _cn.strip():
                _ci.append({"nome":_cn,"valor":_cv,"area":_ca2,"bairro":_cb,"quartos":_cq,"vagas":_cvg,"condo":_cco,"estado":_ces,"obs":_cob,"m2":_cv/_ca2 if _ca2>0 else 0})
                st.session_state["imoveis_comp"]=_ci; st.rerun()
            else: st.warning("Informe a identificação.")
        if _ci:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            _cols = st.columns(len(_ci))
            for _ii,(_im,_col) in enumerate(zip(_ci,_cols)):
                with _col:
                    st.markdown(f"<div class='card'><b>{_im['nome']}</b><br>💰 R$ {_im['valor']:,.0f}<br>📐 {_im['area']}m² | R$ {_im['m2']:,.0f}/m²<br>🛏️ {_im['quartos']}qts | 🚗 {_im['vagas']}vagas<br>📍 {_im['bairro']}<br>🔧 {_im['estado']}<br>🏢 R$ {_im['condo']:,.0f}/mês<br>✨ {_im['obs'] or '-'}</div>", unsafe_allow_html=True)
                    if st.button("🗑️ Remover", key=f"cmp_rem_{_ii}"):
                        _ci.pop(_ii); st.session_state["imoveis_comp"]=_ci; st.rerun()
            _sorted = sorted(_ci, key=lambda x: x["m2"])
            st.markdown("### 🏆 Ranking por preço/m²")
            for _ri,_im in enumerate(_sorted):
                st.markdown(f"**{'🥇🥈🥉'[_ri]} {_im['nome']}** — R$ {_im['m2']:,.0f}/m² — {_im['bairro']}")
            if st.button("🤖 ANÁLISE COMPARATIVA", key="btn_cmp", use_container_width=True):
                _cmp_desc = "\n".join([f"- {im['nome']}: R${im['valor']:,.0f} | {im['area']}m² | R${im['m2']:,.0f}/m² | {im['quartos']}qts | {im['bairro']} | {im['estado']}" for im in _ci])
                _cmp_p = f"""Compare {len(_ci)} imóveis:
{_cmp_desc}
Ranking Python por m²: {" > ".join([im['nome'] for im in _sorted])}
Analise: 1) Melhor custo-benefício e por quê 2) Riscos de cada um 3) Recomendação para comprador de primeira viagem 4) Potencial de valorização 5) O que falta saber 6) 🟢/🟡/🔴"""
                with st.spinner("Comparando..."):
                    _res = chamar_ia(_cmp_p)
                    st.session_state["res_cmp"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Comparador","resumo":f"{len(_ci)} imóveis","conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico; st.rerun()
            if st.session_state.get("res_cmp"):
                st.markdown(f"<div class='card'>{st.session_state['res_cmp']}</div>", unsafe_allow_html=True)

    # ══ CONTRATO ══
    with _tab_co:
        st.header("📄 Análise de Contrato")
        st.markdown("*Checklist jurídico — a IA identifica pontos de atenção. Não substitui advogado.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _co_tipo = st.selectbox("Tipo:", ["Compra e Venda","Locação","Promessa de C&V","Financiamento","Permuta","Outro"], key="co_tipo")
        _co_texto = st.text_area("Cole o contrato:", height=220, key="co_texto", placeholder="Cole as cláusulas ou trechos que geraram dúvida...")
        _co_foco = st.multiselect("Foco:", ["Multas","Prazo entrega","Reajuste","Reformas","Garantias","Rescisão","Vícios ocultos","Identificação partes","Valores","IPTU/Condomínio","Analisar tudo"], default=["Analisar tudo"], key="co_foco")
        if st.button("📄 ANALISAR", key="btn_co", use_container_width=True):
            if _co_texto.strip():
                _co_p = f"""Analise este contrato de {_co_tipo} como checklist jurídico:
Foco: {", ".join(_co_foco)}

{_co_texto}

Estruture em:
🟢 SEM ALERTA — adequado
🟡 ATENÇÃO — explique e o que negociar
🔴 REVISÃO PROFISSIONAL — risco identificado

Verifique: identificação partes, valores e correção, multas (proporcional?), quem paga IPTU/condo/escritura/registro, prazo entrega e penalidades, cláusulas vagas, o que está FALTANDO.
Recomendação final + 🟢/🟡/🔴. SEMPRE ressalve que não substitui advogado."""
                with st.spinner("Analisando..."):
                    _res = chamar_ia(_co_p)
                    st.session_state["res_co"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Contrato","resumo":_co_tipo,"conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico; st.rerun()
            else: st.warning("Cole o contrato.")
        if st.session_state.get("res_co"):
            st.markdown(f"<div class='card'>{st.session_state['res_co']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_co"], file_name="contrato.txt", key="dl_co")

    # ══ DOCUMENTAÇÃO ══
    with _tab_doc:
        st.header("📋 Checklist de Documentação")
        st.markdown("*Documentos necessários por tipo de operação — não esqueça nada.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _doc_tipo = st.selectbox("Operação:", ["Compra de imóvel usado","Compra na planta","Aluguel — locatário","Aluguel — proprietário","Financiamento bancário"], key="doc_tipo")
        _doc_sit = st.multiselect("Sua situação:", ["Primeiro imóvel","Casado/União estável","Pessoa jurídica","FGTS envolvido","Fiador"], key="doc_sit")
        _chklst = {
            "Compra de imóvel usado": [
                ("📋 Documentos do Imóvel",["Matrícula atualizada (máx 30 dias)","Certidão de ônus reais","Certidão de ações reais","Certidão negativa IPTU","Certidão negativa condomínio","Habite-se (se casa)","Averbação da construção"]),
                ("👤 Documentos do Vendedor",["RG e CPF","Certidão de casamento ou nascimento","Certidão negativa de protestos","Certidão negativa trabalhista","Certidão negativa federal"]),
                ("👤 Documentos do Comprador",["RG e CPF","Comprovante de renda","Comprovante de residência","Certidão de estado civil"]),
            ],
            "Compra na planta": [
                ("🏢 Construtora",["Registro de incorporação imobiliária","Memorial descritivo","Certidão de patrimônio de afetação","CNPJ e contrato social","Certidão negativa da empresa"]),
                ("📋 Contrato",["Cronograma físico-financeiro","Prazo de entrega com tolerância","Condições de distrato (Lei 13.786/2018)","Índice de correção durante obra","Condições de financiamento pós-entrega"]),
            ],
            "Aluguel — locatário": [
                ("👤 Documentos Pessoais",["RG e CPF","Comprovante de renda (3x o aluguel)","Comprovante de residência","Referências pessoais"]),
                ("🔐 Garantia",["Fiador: RG, CPF, renda e matrícula do imóvel","ou Seguro-fiança","ou Depósito caução (máx 3 meses)"]),
                ("📋 Na Assinatura",["Laudo de vistoria assinado","Fotos do imóvel antes da entrada","Seguro incêndio"]),
            ],
        }
        _lista = _chklst.get(_doc_tipo, [])
        if _lista:
            for _cat, _docs in _lista:
                st.markdown(f"**{_cat}**")
                for _d in _docs:
                    st.checkbox(_d, key=f"chk_{_d[:25].replace(' ','_').replace('/','')}")
        else:
            st.info("Oriente pela IA para esta operação.")
        if st.button("🤖 ORIENTAÇÃO PERSONALIZADA", key="btn_doc", use_container_width=True):
            _doc_p = f"""Oriente sobre documentação para {_doc_tipo}.
Situação: {", ".join(_doc_sit) or "padrão"}
Explique: 1) O que cada documento comprova 2) Onde obter e prazo médio 3) Custos aproximados 4) O que pode dar problema se faltar 5) Dicas para agilizar 6) 🟢/🟡/🔴 — informe que prazos variam por município"""
            with st.spinner("Orientando..."):
                _res = chamar_ia(_doc_p)
                st.session_state["res_doc"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Documentação","resumo":_doc_tipo,"conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_doc"):
            st.markdown(f"<div class='card'>{st.session_state['res_doc']}</div>", unsafe_allow_html=True)

    # ══ INVESTIMENTO ══
    with _tab_iv:
        st.header("📈 Rentabilidade — Investimento em Imóveis")
        st.markdown("*ROI, Cap Rate e yield calculados em Python — a IA interpreta e compara.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.info("🔢 Indicadores calculados em Python. A IA interpreta e compara com alternativas.")
        _iv1,_iv2 = st.columns(2)
        with _iv1:
            _iv_tipo = st.selectbox("Tipo:", ["Comprar para alugar","Comprar para revender","Planta para revenda","Flipping (reforma+venda)"], key="iv_tipo")
            _iv_valor = st.number_input("Valor do imóvel (R$):", min_value=50000, value=400000, step=10000, key="iv_valor", format="%d")
            _iv_aluguel = st.number_input("Aluguel esperado (R$/mês):", min_value=0, value=2500, step=100, key="iv_aluguel", format="%d")
            _iv_vacancia = st.slider("Vacância estimada (%):", 0, 20, 5, key="iv_vacancia")
        with _iv2:
            _iv_condo = st.number_input("Condomínio + IPTU mensal (R$):", min_value=0, value=1200, step=100, key="iv_condo", format="%d")
            _iv_manut = st.number_input("Manutenção anual (R$):", min_value=0, value=3000, step=500, key="iv_manut", format="%d")
            _iv_selic = st.number_input("Selic atual (% a.a.):", min_value=1.0, value=13.75, step=0.25, key="iv_selic")
            _iv_horiz = st.selectbox("Horizonte:", ["1-2 anos","3-5 anos","5-10 anos","Mais de 10 anos"], key="iv_horiz")
        _iv_roi = roi_imovel(_iv_valor, _iv_aluguel, _iv_condo+_iv_manut/12, _iv_vacancia)
        _iv_vs = _iv_roi["cap_rate"]-_iv_selic
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _ivc1,_ivc2,_ivc3,_ivc4 = st.columns(4)
        _ivc1.metric("Cap Rate líquido", f"{_iv_roi['cap_rate']:.2f}% a.a.")
        _ivc2.metric("Yield mensal", f"{_iv_roi['yield_mensal']:.2f}%")
        _ivc3.metric("Receita líquida/ano", f"R$ {_iv_roi['receita_anual']:,.0f}")
        _ivc4.metric("Payback", f"{_iv_roi['payback_anos']:.1f} anos")
        _cc = "card-green" if _iv_vs>0 else "card-red"
        st.markdown(f"<div class='{_cc}'>{'✅' if _iv_vs>0 else '⚠️'} vs Selic ({_iv_selic}%): imóvel rende <b>{_iv_vs:+.2f}%</b> {'acima' if _iv_vs>0 else 'abaixo'}</div>", unsafe_allow_html=True)
        st.caption("⚠️ Baseado nos dados informados. Resultados reais variam.")
        _iv_obs = st.text_area("Contexto:", height=60, key="iv_obs", placeholder="Ex: Já tenho imóvel próprio, região em expansão...")
        if st.button("📈 ANÁLISE DA IA", key="btn_iv", use_container_width=True):
            _iv_p = f"""Interprete os indicadores de investimento:
{_iv_tipo} | Valor R${_iv_valor:,.0f} | Aluguel R${_iv_aluguel:,.0f}/mês | Vacância {_iv_vacancia}% | Custos R${_iv_condo:,.0f}/mês | Manutenção R${_iv_manut:,.0f}/ano | Horizonte {_iv_horiz}
PYTHON: Cap Rate {_iv_roi['cap_rate']:.2f}% | Receita anual R${_iv_roi['receita_anual']:,.0f} | Payback {_iv_roi['payback_anos']:.1f}a | vs Selic {_iv_vs:+.2f}%
Obs: {_iv_obs or "nenhuma"}
Analise: 1) Vale a pena? 2) Compare com FIIs e renda fixa honestamente 3) Cenários otimista/base/pessimista 4) Riscos 5) 🟢/🟡/🔴"""
            with st.spinner("Analisando..."):
                _res = chamar_ia(_iv_p)
                st.session_state["res_iv"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Investimento","resumo":f"R${_iv_valor:,.0f}/{_iv_roi['cap_rate']:.1f}%","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_iv"):
            st.markdown(f"<div class='card'>{st.session_state['res_iv']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_iv"], file_name="investimento.txt", key="dl_iv")

    # ══ NA PLANTA ══
    with _tab_pl:
        st.header("🏗️ Imóvel na Planta")
        st.markdown("*Checklist completo + pesquisa da construtora na web.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _pl1,_pl2 = st.columns(2)
        with _pl1:
            _pl_const = st.text_input("Construtora:", key="pl_const", placeholder="Ex: MRV, Cyrela...")
            _pl_preco = st.number_input("Valor total (R$):", min_value=50000, value=350000, step=10000, key="pl_preco", format="%d")
            _pl_entrada = st.number_input("Entrada durante obra (R$):", min_value=0, value=70000, step=5000, key="pl_entrada", format="%d")
        with _pl2:
            _pl_prazo = st.text_input("Prazo de entrega:", key="pl_prazo", placeholder="Ex: Dezembro de 2027")
            _pl_tipo = st.selectbox("Tipo:", ["Apartamento","Casa em condomínio","Loteamento"], key="pl_tipo")
            _pl_fin = st.selectbox("Financiamento pós-obra:", ["Banco (SBPE)","MCMV","Pela construtora","Não definido"], key="pl_fin")
        _pl_preoc = st.multiselect("Preocupações:", ["Construtora desconhecida","Atraso","Qualidade","Distrato","Parcela pós-entrega","Documentação terreno","Patrimônio de afetação"], key="pl_preoc")
        _pl_obs = st.text_area("Informações:", height=60, key="pl_obs", placeholder="Ex: 58m², 2 quartos, 8º andar...")
        if st.button("🏗️ ANALISAR + PESQUISAR CONSTRUTORA", key="btn_pl", use_container_width=True):
            _pl_p = f"""Analise esta compra na planta{'e PESQUISE sobre ' + _pl_const if _pl_const else ''}:
Construtora: {_pl_const or "não informada"} | {_pl_tipo} | R$ {_pl_preco:,.0f} | Entrada R$ {_pl_entrada:,.0f} | Entrega: {_pl_prazo} | Pós-obra: {_pl_fin}
Preocupações: {", ".join(_pl_preoc) or "geral"} | Obs: {_pl_obs or "nenhuma"}
{"Busque: '" + _pl_const + " reclamações', '" + _pl_const + " Reclame Aqui', '" + _pl_const + " atraso entrega'. Cite APENAS o que encontrar." if _pl_const else ""}
Oriente: 1) Checklist antes de assinar (RGI, alvará, memorial, patrimônio afetação) 2) Direitos em atraso (Lei 13.786/2018) 3) Como calcular parcela pós-entrega 4) {'Sobre a construtora: o que encontrou' if _pl_const else 'Como pesquisar a construtora'} 5) Cláusulas que não podem mudar 6) 🟢/🟡/🔴"""
            with st.spinner("Analisando e pesquisando..."):
                _res = chamar_ia(_pl_p)
                st.session_state["res_pl"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Na Planta","resumo":f"{_pl_const} R${_pl_preco:,.0f}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_pl"):
            st.markdown(f"<div class='card'>{st.session_state['res_pl']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_pl"], file_name="planta.txt", key="dl_pl")

    # ══ ARMADILHAS ══
    with _tab_am:
        st.header("⚠️ Armadilhas Comuns")
        st.markdown("*Erros do seu momento específico — como identificar e se proteger.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _am1,_am2 = st.columns(2)
        with _am1:
            _am_mom = st.selectbox("Seu momento:", ["Procurando para comprar","Prestes a assinar compra","Procurando para alugar","Prestes a assinar aluguel","Comprando na planta","Negociando financiamento","Acabei de comprar","Pensando em vender"], key="am_mom")
            _am_tipo = st.selectbox("Tipo:", ["Apartamento","Casa","Terreno","Comercial"], key="am_tipo")
        with _am2:
            _am_preoc = st.multiselect("Preocupações:", ["Golpes","Cláusulas abusivas","Documentação irregular","Dívidas escondidas","Construtora problemática","Corretor desonesto","Preço superfaturado","Financiamento com pegadinha"], key="am_preoc")
        if st.button("⚠️ VER ARMADILHAS", key="btn_am", use_container_width=True):
            _am_p = f"""Liste armadilhas para: {_am_mom} | {_am_tipo} | {", ".join(_am_preoc) or "geral"}
Para cada: nome, como acontece, sinal de alerta, como se proteger, o que fazer se já caiu.
Baseie em legislação brasileira vigente e casos reais. 🟢/🟡/🔴"""
            with st.spinner("Listando..."):
                _res = chamar_ia(_am_p)
                st.session_state["res_am"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Armadilhas","resumo":_am_mom,"conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_am"):
            st.markdown(f"<div class='card'>{st.session_state['res_am']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_am"], file_name="armadilhas.txt", key="dl_am")

    # ══ NEGOCIAÇÃO ══
    with _tab_ng:
        st.header("💡 Estratégia de Negociação")
        st.markdown("*Passo a passo para conseguir o melhor preço e condições.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _ng1,_ng2 = st.columns(2)
        with _ng1:
            _ng_preco = st.number_input("Preço pedido (R$):", min_value=10000, value=400000, step=5000, key="ng_preco", format="%d")
            _ng_meta = st.number_input("Meta (R$):", min_value=10000, value=370000, step=5000, key="ng_meta", format="%d")
            _ng_tempo = st.selectbox("Tempo no mercado:", ["Acabou de sair","1-3 meses","3-6 meses","Mais de 6 meses","Não sei"], key="ng_tempo")
        with _ng2:
            _ng_motiv = st.selectbox("Motivação vendedor:", ["Não sei","Urgência","Mudança de cidade","Necessidade financeira","Sem urgência","Inventário"], key="ng_motiv")
            _ng_pagto = st.selectbox("Pagamento:", ["À vista","Financiamento","FGTS+financiamento","Parcelado com vendedor"], key="ng_pagto")
            _ng_extras = st.multiselect("Além do preço:", ["Mobília","Pintura","Reparos","Prazo entrega","Isenção ITBI"], key="ng_extras")
        _ng_obs = st.text_area("Contexto:", height=60, key="ng_obs", placeholder="Ex: Visitei 3x, dono mora fora, 8 meses no mercado...")
        _ng_desc = (_ng_preco-_ng_meta)/_ng_preco*100 if _ng_preco>0 else 0
        st.markdown(f"<div class='card-blue'>📊 Desconto pretendido: <b>{_ng_desc:.1f}%</b> (R$ {_ng_preco-_ng_meta:,.0f})</div>", unsafe_allow_html=True)
        if st.button("💡 MONTAR ESTRATÉGIA", key="btn_ng", use_container_width=True):
            _ng_p = f"""Estratégia de negociação:
Pedido R${_ng_preco:,.0f} | Meta R${_ng_meta:,.0f} ({_ng_desc:.1f}%) | Mercado {_ng_tempo} | Vendedor: {_ng_motiv}
Pagamento: {_ng_pagto} | Extras: {", ".join(_ng_extras) or "só preço"} | Contexto: {_ng_obs or "nenhum"}
Forneça: 1) Poder de barganha 2) Estratégia passo a passo 3) Primeira oferta e justificativa 4) Como apresentar 5) Respostas para contrapropostas 6) Quando aceitar 7) 🟢/🟡/🔴"""
            with st.spinner("Montando estratégia..."):
                _res = chamar_ia(_ng_p)
                st.session_state["res_ng"] = _res
                historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Negociação","resumo":f"R${_ng_preco:,.0f}→R${_ng_meta:,.0f}","conteudo":_res})
                st.session_state.historico_consultor_imoveis = historico; st.rerun()
        if st.session_state.get("res_ng"):
            st.markdown(f"<div class='card'>{st.session_state['res_ng']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_ng"], file_name="negociacao.txt", key="dl_ng")

    # ══ SIMULAÇÕES ══
    with _tab_sm:
        st.header("📊 Simulações Comparativas")
        st.markdown("*Compare cenários com números reais — o sistema calcula, a IA explica.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        _sm_tipo = st.selectbox("Cenário:", ["Comprar à vista vs financiado","Comprar vs alugar + investir a diferença","SAC vs PRICE","Comprar agora vs esperar 2 anos"], key="sm_tipo")
        _sm_desc = st.text_area("Descreva os números:", height=130, key="sm_desc", placeholder="Ex: Tenho R$400mil. Opção 1: comprar à vista. Opção 2: dar R$80mil e financiar em 30 anos a 10,5% enquanto invisto R$320mil a 13%...")
        if st.button("📊 SIMULAR", key="btn_sm", use_container_width=True):
            if _sm_desc.strip():
                _sm_p = f"""Compare: {_sm_tipo}
{_sm_desc}
Se houver números claros, use-os. Mostre premissas.
Forneça: 1) Tabela comparativa com números 2) Custo total em 5, 10 e 20 anos 3) Ponto de equilíbrio 4) Vantagens/desvantagens 5) Recomendação 6) 🟢/🟡/🔴 — honesto sobre premissas"""
                with st.spinner("Simulando..."):
                    _res = chamar_ia(_sm_p)
                    st.session_state["res_sm"] = _res
                    historico.append({"data":datetime.now().strftime("%d/%m %H:%M"),"aba":"Simulação","resumo":_sm_tipo,"conteudo":_res})
                    st.session_state.historico_consultor_imoveis = historico; st.rerun()
            else: st.warning("Descreva os cenários.")
        if st.session_state.get("res_sm"):
            st.markdown(f"<div class='card'>{st.session_state['res_sm']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar", data=st.session_state["res_sm"], file_name="simulacao.txt", key="dl_sm")

# ── RODAPÉ ──
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Consultor de Imóveis IA · Quiz Com Prêmios · <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
