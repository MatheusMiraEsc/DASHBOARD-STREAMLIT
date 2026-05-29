
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

BASE_DIR = Path(__file__).parent

# ─────────────────────────────────────────────
# CONFIGURAÇÃO GERAL DO STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mercado de Trabalho — Pernambuco Teste",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────────────────────────
# PALETA DE CORES
# ─────────────────────────────────────────────
COR_EMPREGO     = "#378ADD"
COR_INFORMAL    = "#BA7517"
COR_DESOCUPACAO = "#E24B4A"
COR_HOMENS      = "#185FA5"
COR_MULHERES    = "#D4537E"
COR_TOTAL       = "#888780"

# Layout padrão reutilizável para todos os gráficos
LAYOUT_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    font=dict(family="Arial", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=80, b=40, l=60, r=60),
)


# =============================================================================
# CARREGAMENTO E TRATAMENTO DOS DADOS
# =============================================================================

@st.cache_data
def carregar_dados():
    # ── Emprego ──────────────────────────────────────────────────────────────
    emp = pd.read_csv(BASE_DIR / "emprego.csv")
    emp.columns = ["periodo", "emp_total", "emp_homens", "emp_mulh"]
    emp["periodo"] = pd.to_datetime(emp["periodo"])
    emp["ano"] = emp["periodo"].dt.year
    emp = emp[emp["emp_total"] != 0]  # remove trimestres sem coleta

    # ── Informalidade ────────────────────────────────────────────────────────
    inf = pd.read_csv(BASE_DIR / "informalidade.csv", sep=";")
    inf.columns = ["periodo", "inf_total", "inf_homens", "inf_mulh"]
    inf["periodo"] = pd.to_datetime(inf["periodo"])
    inf["ano"] = inf["periodo"].dt.year
    inf = inf[inf["inf_total"] != 0]  # remove zeros (sem coleta antes de 2015)

    # ── Desocupação ──────────────────────────────────────────────────────────
    des = pd.read_csv(BASE_DIR / "desocupacao.csv", sep=";")
    des.columns = ["periodo", "des_total", "des_homens", "des_mulh"]
    des["periodo"] = pd.to_datetime(des["periodo"])
    des["ano"] = des["periodo"].dt.year
    des = des[des["des_total"] != 0]

    # ── Média anual e merge ───────────────────────────────────────────────────
    emp_a = emp.groupby("ano")[["emp_total","emp_homens","emp_mulh"]].mean().reset_index()
    inf_a = inf.groupby("ano")[["inf_total","inf_homens","inf_mulh"]].mean().reset_index()
    des_a = des.groupby("ano")[["des_total","des_homens","des_mulh"]].mean().reset_index()

    df = emp_a.merge(inf_a, on="ano", how="inner").merge(des_a, on="ano", how="inner")
    cols_num = [c for c in df.columns if c != "ano"]
    df[cols_num] = df[cols_num].round(2)
    return df

df = carregar_dados()

anos       = df["ano"].tolist()
anos_rec   = [a for a in anos if a >= 2022]
emp_total  = df["emp_total"].tolist()
emp_homens = df["emp_homens"].tolist()
emp_mulh   = df["emp_mulh"].tolist()
inf_total  = df["inf_total"].tolist()
inf_homens = df["inf_homens"].tolist()
inf_mulh   = df["inf_mulh"].tolist()
des_total  = df["des_total"].tolist()
des_homens = df["des_homens"].tolist()
des_mulh   = df["des_mulh"].tolist()

df_rec        = df[df["ano"].isin(anos_rec)].reset_index(drop=True)
anos_rec_list = df_rec["ano"].tolist()
des_h_r       = df_rec["des_homens"].tolist()
des_m_r       = df_rec["des_mulh"].tolist()
des_t_r       = df_rec["des_total"].tolist()
emp_t_r       = df_rec["emp_total"].tolist()
inf_t_r       = df_rec["inf_total"].tolist()


# =============================================================================
# CABEÇALHO
# =============================================================================

st.title("📊 Mercado de Trabalho em Pernambuco - Teste 2")
st.subheader("Emprego, Informalidade e Desocupação — 2015 a 2025")
st.markdown("""
> Narrativa em **4 atos** sobre o mercado de trabalho de Pernambuco, baseada em dados
> trimestrais da PNAD Contínua. Passe o mouse sobre os gráficos para ver os valores detalhados.
""")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────────────────────
ano_max = max(anos)
row_max = df[df["ano"] == ano_max].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"🟦 Emprego ({ano_max})",       f"{row_max['emp_total']:.1f}%",
            f"{row_max['emp_total'] - df[df['ano']==2015].iloc[0]['emp_total']:.1f} pp vs 2015")
col2.metric(f"🟧 Informalidade ({ano_max})",  f"{row_max['inf_total']:.1f}%",
            f"{row_max['inf_total'] - df[df['ano']==2016].iloc[0]['inf_total']:.1f} pp vs 2016",
            delta_color="inverse")
col3.metric(f"🟥 Desocupação ({ano_max})",    f"{row_max['des_total']:.1f}%",
            f"{row_max['des_total'] - df[df['ano']==2017].iloc[0]['des_total']:.1f} pp vs pico 2017",
            delta_color="inverse")
col4.metric(f"⚖️ Gap de Gênero Emprego ({ano_max})",
            f"{round(row_max['emp_homens'] - row_max['emp_mulh'], 1)} pp",
            help="Diferença entre taxa de emprego de homens e mulheres")
st.divider()


# =============================================================================
# ATO 1 — O CENÁRIO
# =============================================================================

st.header("🎬 Ato 1 · O Cenário")
st.markdown(f"""
**Uma economia aparentemente estável — mas estruturalmente informal**

> A taxa de emprego oscilou apenas **{max(emp_total) - min(emp_total):.1f} pp** em dez anos.
> Mas quase metade dos trabalhadores permanece sem vínculo formal.
> A estabilidade aparente esconde fragilidade estrutural.
""")

fig1 = go.Figure()

# Faixas de evento histórico (shapes)
fig1.add_vrect(x0=2016.5, x1=2017.5, fillcolor="#FAEEDA", opacity=0.5, layer="below",
               line_width=0, annotation_text="Pico da crise", annotation_position="top left",
               annotation_font_color=COR_INFORMAL)
fig1.add_vrect(x0=2021.5, x1=2022.5, fillcolor="#FAECE7", opacity=0.4, layer="below",
               line_width=0, annotation_text="Retomada pós-pandemia", annotation_position="top left",
               annotation_font_color="#993C1D")

fig1.add_trace(go.Scatter(
    x=anos, y=emp_total, mode="lines+markers", name="Taxa de Emprego",
    line=dict(color=COR_EMPREGO, width=2.5),
    marker=dict(size=7),
    hovertemplate="Emprego: %{y:.1f}%<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=anos, y=inf_total, mode="lines+markers", name="Taxa de Informalidade",
    line=dict(color=COR_INFORMAL, width=2.5),
    marker=dict(size=7, symbol="square"),
    hovertemplate="Informalidade: %{y:.1f}%<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=anos, y=des_total, mode="lines+markers", name="Taxa de Desocupação",
    line=dict(color=COR_DESOCUPACAO, width=2.5),
    marker=dict(size=7, symbol="triangle-up"),
    hovertemplate="Desocupação: %{y:.1f}%<extra></extra>",
))

fig1.update_layout(
    **LAYOUT_BASE,
    title="Panorama Geral do Mercado de Trabalho em Pernambuco (2015–2025)",
    yaxis=dict(ticksuffix="%", title="Taxa (%)"),
    xaxis=dict(tickmode="array", tickvals=anos, title="Ano"),
    height=420,
)
st.plotly_chart(fig1, use_container_width=True)

st.info(
    f"💡 **Insight:** A amplitude do emprego é de apenas {max(emp_total) - min(emp_total):.1f} pp "
    "ao longo de 10 anos — enquanto a informalidade se manteve estruturalmente acima de 46%. "
    "A estabilidade aparente mascara a precariedade do vínculo de trabalho."
)
st.divider()


# =============================================================================
# ATO 2 — A CRISE E O PÓS-PANDEMIA
# =============================================================================

st.header("🎬 Ato 2 · A Crise e o Pós-Pandemia")
st.markdown(f"""
**2017: o pico do desemprego. 2022: o salto da informalidade.**

> A recessão gerou o pior desemprego da série (**{max(des_total):.1f}%** em 2017).
> A retomada pós-pandemia aconteceu via trabalho informal (**{max(inf_total):.1f}%** em 2022).
""")

# Eixo duplo: barras (desocupação) + linha (informalidade)
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

bar_cores = [COR_DESOCUPACAO if a == 2017 else "#F09595" for a in anos]
fig2.add_trace(go.Bar(
    x=anos, y=des_total, name="Desocupação total",
    marker_color=bar_cores, opacity=0.85,
    hovertemplate="Desocupação: %{y:.1f}%<extra></extra>",
), secondary_y=False)

fig2.add_trace(go.Scatter(
    x=anos, y=inf_total, mode="lines+markers", name="Informalidade total",
    line=dict(color=COR_INFORMAL, width=2.5),
    marker=dict(size=8, symbol="diamond"),
    hovertemplate="Informalidade: %{y:.1f}%<extra></extra>",
), secondary_y=True)

# Anotação pico 2017
fig2.add_annotation(
    x=2017, y=max(des_total), text=f"Pico: {max(des_total):.1f}%",
    showarrow=True, arrowhead=2, ax=0, ay=-40,
    font=dict(color=COR_DESOCUPACAO, size=11, family="Arial Black"),
)
# Anotação pico informalidade
idx_inf = inf_total.index(max(inf_total))
fig2.add_annotation(
    x=anos[idx_inf], y=max(inf_total), yref="y2",
    text=f"Salto pós-pandemia: {max(inf_total):.1f}%",
    showarrow=True, arrowhead=2, ax=60, ay=-35,
    font=dict(color=COR_INFORMAL, size=11, family="Arial Black"),
)

fig2.update_layout(
    **LAYOUT_BASE,
    title="Crise (2017) e Retomada Informal (2022)",
    xaxis=dict(tickmode="array", tickvals=anos, title="Ano"),
    height=420,
    barmode="group",
)
fig2.update_yaxes(ticksuffix="%", title_text="Desocupação (%)",
                  title_font_color=COR_DESOCUPACAO, secondary_y=False)
fig2.update_yaxes(ticksuffix="%", title_text="Informalidade (%)",
                  title_font_color=COR_INFORMAL, secondary_y=True,
                  showgrid=False)
st.plotly_chart(fig2, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Pico de Desocupação (2017)",       f"{max(des_total):.1f}%",  "pior da série histórica",  delta_color="inverse")
c2.metric("Informalidade máxima (2022)",       f"{max(inf_total):.1f}%",  "retomada informal",        delta_color="inverse")
c3.metric("Queda 2017→2025",                  f"{max(des_total) - min(des_total):.1f} pp", "recuperação em curso")

st.warning(
    f"⚠️ **Atenção:** Em 2022, a informalidade atingiu {max(inf_total):.1f}% — indicando que "
    "os postos criados pós-pandemia não geraram proteção social plena."
)
st.divider()


# =============================================================================
# ATO 3 — A CLIVAGEM ESTRUTURAL DE GÊNERO
# =============================================================================

st.header("🎬 Ato 3 · A Clivagem Estrutural de Gênero")
gap_medio = sum(h - m for h, m in zip(emp_homens, emp_mulh)) / len(emp_homens)
gap_des_min = min(m - h for h, m in zip(des_homens, des_mulh))
st.markdown(f"""
**Mulheres trabalham menos, enfrentam mais desocupação e informalidade mais volátil.**

> O gap de emprego é de **~{gap_medio:.0f} pp**. O gap de desocupação nunca foi menor
> que **{gap_des_min:.1f} pp**. Essa desigualdade não é cíclica — é estrutural.
""")

col_a, col_b = st.columns(2)

# ── 3a: Emprego por gênero (barras agrupadas) ─────────────────────────────
with col_a:
    fig3a = go.Figure()
    fig3a.add_trace(go.Bar(
        x=anos, y=emp_homens, name="Homens",
        marker_color=COR_HOMENS, opacity=0.85,
        hovertemplate="Homens: %{y:.1f}%<extra></extra>",
    ))
    fig3a.add_trace(go.Bar(
        x=anos, y=emp_mulh, name="Mulheres",
        marker_color=COR_MULHERES, opacity=0.85,
        hovertemplate="Mulheres: %{y:.1f}%<extra></extra>",
    ))
    fig3a.update_layout(
        **LAYOUT_BASE,
        title="3a · Taxa de Emprego por Gênero",
        barmode="group",
        yaxis=dict(ticksuffix="%", title="%", range=[35, max(emp_homens)+7]),
        xaxis=dict(tickmode="array", tickvals=anos),
        height=380,
    )
    st.plotly_chart(fig3a, use_container_width=True)

# ── 3b: Desocupação por gênero (linhas + área) ────────────────────────────
with col_b:
    fig3b = go.Figure()
    # Área sombreada entre as duas curvas
    fig3b.add_trace(go.Scatter(
        x=anos + anos[::-1],
        y=des_mulh + des_homens[::-1],
        fill="toself", fillcolor="rgba(212,83,126,0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip", showlegend=False, name="Gap",
    ))
    fig3b.add_trace(go.Scatter(
        x=anos, y=des_homens, mode="lines+markers", name="Homens",
        line=dict(color=COR_HOMENS, width=2.5),
        marker=dict(size=7),
        hovertemplate="Homens: %{y:.1f}%<extra></extra>",
    ))
    fig3b.add_trace(go.Scatter(
        x=anos, y=des_mulh, mode="lines+markers", name="Mulheres",
        line=dict(color=COR_MULHERES, width=2.5),
        marker=dict(size=7, symbol="triangle-up"),
        hovertemplate="Mulheres: %{y:.1f}%<extra></extra>",
    ))
    fig3b.update_layout(
        **LAYOUT_BASE,
        title="3b · Desocupação por Gênero",
        yaxis=dict(ticksuffix="%", title="%", range=[5, max(des_mulh)+4]),
        xaxis=dict(tickmode="array", tickvals=anos),
        height=380,
    )
    st.plotly_chart(fig3b, use_container_width=True)

# ── 3c: Informalidade por gênero (linha inteira) ──────────────────────────
fig3c = go.Figure()
fig3c.add_trace(go.Scatter(
    x=anos + anos[::-1],
    y=inf_homens + inf_mulh[::-1],
    fill="toself", fillcolor="rgba(24,95,165,0.10)",
    line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip", showlegend=False,
))
fig3c.add_trace(go.Scatter(
    x=anos, y=inf_homens, mode="lines+markers", name="Homens",
    line=dict(color=COR_HOMENS, width=2.5),
    marker=dict(size=7),
    hovertemplate="Homens: %{y:.1f}%<extra></extra>",
))
fig3c.add_trace(go.Scatter(
    x=anos, y=inf_mulh, mode="lines+markers", name="Mulheres",
    line=dict(color=COR_MULHERES, width=2.5),
    marker=dict(size=7, symbol="triangle-up"),
    hovertemplate="Mulheres: %{y:.1f}%<extra></extra>",
))
fig3c.update_layout(
    **LAYOUT_BASE,
    title="3c · Informalidade por Gênero",
    yaxis=dict(ticksuffix="%", title="%", range=[min(inf_mulh)-2, max(inf_homens)+4]),
    xaxis=dict(tickmode="array", tickvals=anos),
    height=360,
)
st.plotly_chart(fig3c, use_container_width=True)

# Métricas de gênero
st.markdown("#### 📐 Resumo Estatístico de Gênero")
gap_emp    = round(sum(h - m for h, m in zip(emp_homens, emp_mulh)) / len(emp_homens), 1)
gap_d_min  = round(min(m - h for h, m in zip(des_homens, des_mulh)), 1)
gap_d_max  = round(max(m - h for h, m in zip(des_homens, des_mulh)), 1)
c1, c2, c3 = st.columns(3)
c1.metric("Gap médio de Emprego (H–M)",       f"{gap_emp} pp",   help="Homens sempre com taxa mais alta")
c2.metric("Gap mín. de Desocupação (M–H)",    f"{gap_d_min} pp", help="Menor diferença observada na série")
c3.metric("Gap máx. de Desocupação (M–H)",    f"{gap_d_max} pp", help="Maior diferença observada na série")

st.error(
    f"🚨 **Desigualdade estrutural:** O gap de emprego nunca foi inferior a "
    f"{min(h - m for h, m in zip(emp_homens, emp_mulh)):.1f} pp em nenhum ano da série. "
    "A desigualdade não é cíclica — não melhorou em anos de crescimento."
)
st.divider()


# =============================================================================
# ATO 4 — A RECUPERAÇÃO RECENTE
# =============================================================================

st.header("🎬 Ato 4 · A Recuperação Recente — Real, mas Não Equitativa")
ano_min_des = anos[des_total.index(min(des_total))]
inf_ultimo  = df[df["ano"] == ano_max]["inf_total"].values[0]
gap_rec     = df[df["ano"] == ano_max]["des_mulh"].values[0] - df[df["ano"] == ano_max]["des_homens"].values[0]
st.markdown(f"""
**2025: o menor desemprego da série. Mas a informalidade resiste.**

> Desocupação de **{min(des_total):.1f}%** em {ano_min_des} — mínimo histórico.
> Informalidade de **{inf_ultimo:.1f}%** mantém quase metade da força de trabalho
> sem proteção social. Diferencial de gênero ainda em **{gap_rec:.1f} pp**.
""")

col_c, col_d = st.columns(2)

# ── 4a: Desocupação recente por gênero ───────────────────────────────────
with col_c:
    fig4a = go.Figure()
    fig4a.add_trace(go.Scatter(
        x=anos_rec_list + anos_rec_list[::-1],
        y=des_m_r + des_h_r[::-1],
        fill="toself", fillcolor="rgba(212,83,126,0.10)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip", showlegend=False,
    ))
    fig4a.add_trace(go.Scatter(
        x=anos_rec_list, y=des_h_r, mode="lines+markers+text", name="Homens",
        line=dict(color=COR_HOMENS, width=3),
        marker=dict(size=10),
        text=[f"{v:.1f}%" for v in des_h_r],
        textposition="top right",
        hovertemplate="Homens: %{y:.1f}%<extra></extra>",
    ))
    fig4a.add_trace(go.Scatter(
        x=anos_rec_list, y=des_m_r, mode="lines+markers+text", name="Mulheres",
        line=dict(color=COR_MULHERES, width=3),
        marker=dict(size=10, symbol="triangle-up"),
        text=[f"{v:.1f}%" for v in des_m_r],
        textposition="bottom right",
        hovertemplate="Mulheres: %{y:.1f}%<extra></extra>",
    ))
    fig4a.add_trace(go.Scatter(
        x=anos_rec_list, y=des_t_r, mode="lines+markers", name="Total",
        line=dict(color=COR_TOTAL, width=2, dash="dash"),
        marker=dict(size=7),
        hovertemplate="Total: %{y:.1f}%<extra></extra>",
    ))
    fig4a.update_layout(
        **LAYOUT_BASE,
        title="4a · Desocupação Recente por Gênero (2022–2025)",
        yaxis=dict(ticksuffix="%", title="%", range=[5, max(des_m_r)+5]),
        xaxis=dict(tickmode="array", tickvals=anos_rec_list),
        height=400,
    )
    st.plotly_chart(fig4a, use_container_width=True)

# ── 4b: Emprego vs Informalidade (eixo duplo) ────────────────────────────
with col_d:
    fig4b = make_subplots(specs=[[{"secondary_y": True}]])
    fig4b.add_trace(go.Bar(
        x=anos_rec_list, y=emp_t_r, name="Emprego (total)",
        marker_color=COR_EMPREGO, opacity=0.75,
        hovertemplate="Emprego: %{y:.1f}%<extra></extra>",
    ), secondary_y=False)
    fig4b.add_trace(go.Scatter(
        x=anos_rec_list, y=inf_t_r, mode="lines+markers+text", name="Informalidade (total)",
        line=dict(color=COR_INFORMAL, width=3),
        marker=dict(size=10, symbol="diamond"),
        text=[f"{v:.1f}%" for v in inf_t_r],
        textposition="top center",
        hovertemplate="Informalidade: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig4b.update_layout(
        **LAYOUT_BASE,
        title="4b · Emprego vs. Informalidade (2022–2025)",
        xaxis=dict(tickmode="array", tickvals=anos_rec_list),
        height=400,
    )
    fig4b.update_yaxes(ticksuffix="%", title_text="Emprego (%)",
                       title_font_color=COR_EMPREGO,
                       range=[min(emp_t_r)-4, max(emp_t_r)+6], secondary_y=False)
    fig4b.update_yaxes(ticksuffix="%", title_text="Informalidade (%)",
                       title_font_color=COR_INFORMAL,
                       range=[min(inf_t_r)-2, max(inf_t_r)+4],
                       showgrid=False, secondary_y=True)
    st.plotly_chart(fig4b, use_container_width=True)

st.success(
    f"✅ **Progresso real:** Desocupação atingiu {min(des_total):.1f}% em {ano_min_des} — mínimo histórico. "
    "A recuperação é concreta, mas concentrada nos trabalhadores formais e mais intensa para os homens. "
    "A informalidade ainda mantém quase metade da força de trabalho sem proteção previdenciária plena."
)
st.divider()


# =============================================================================
# SÍNTESE FINAL
# =============================================================================

st.header("📋 Síntese do Data Storytelling")

col_tab, col_insight = st.columns([2, 1])

with col_tab:
    sintese = pd.DataFrame({
        "Ato": ["1 · O Cenário", "2 · Crise e Pós-Pandemia", "3 · Clivagem de Gênero", "4 · Recuperação"],
        "Mensagem-chave": [
            "Estabilidade no emprego, informalidade estrutural",
            "2017 = pico do desemprego; 2022 = salto da informalidade",
            "Gap de ~23 pp no emprego; desocupação feminina sempre acima",
            "Mínimo histórico de desemprego, mas informalidade resiste",
        ],
        "Gráfico principal": [
            "Linha tripla — emprego, informalidade, desocupação",
            "Barras + linha duplo eixo",
            "Painel 3 gráficos por indicador (gênero)",
            "Linhas por gênero + barras vs. linha",
        ],
    })
    st.dataframe(sintese, use_container_width=True, hide_index=True)

with col_insight:
    st.markdown("""
    #### 💡 Insights finais

    1. **Rigidez do emprego:** amplitude de apenas ~3 pp em 10 anos.

    2. **Informalidade pós-pandemia:** retomada de 2022 foi pelo lado informal.

    3. **Desigualdade estrutural de gênero:** independe do ciclo econômico.

    4. **Recuperação assimétrica:** homens se beneficiaram mais da queda do desemprego.
    """)

with st.expander("🔍 Ver dados brutos (médias anuais)"):
    df_display = df.copy()
    df_display.columns = [
        "Ano",
        "Emprego Total (%)", "Emprego Homens (%)", "Emprego Mulheres (%)",
        "Informalidade Total (%)", "Informalidade Homens (%)", "Informalidade Mulheres (%)",
        "Desocupação Total (%)", "Desocupação Homens (%)", "Desocupação Mulheres (%)",
    ]
    st.dataframe(df_display.set_index("Ano"), use_container_width=True)

st.markdown("---")
st.caption(
    "Fonte: PNAD Contínua — dados trimestrais de Pernambuco, 2015–2025. "
    "Análise via Python/Pandas/Plotly/Streamlit. "
    "Equipe: Maria Luísa Albuquerque, Matheus Miranda, Jorge Augusto, "
    "Maria Júlia Germano, Bruno Oliveira e Heitor Santana."
)