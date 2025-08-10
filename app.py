import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- CSS Customizado ---
st.markdown("""
    <style>
    /* Fundo geral */
    .main {
        background-color: #0E1117;
        color: white;
    }
    /* Título grande */
    .big-title {
        font-size: 38px;
        font-weight: bold;
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    /* KPIs estilizados */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363D;
    }
    /* Tabelas */
    div[data-testid="stDataFrame"] {
        border: 1px solid #30363D;
        border-radius: 8px;
        overflow: hidden;
    }
    /* Avisos */
    .stAlert {
        background-color: #20232A;
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# --- Carregamento dos dados ---
df = pd.read_csv(
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Título ---
st.markdown("<h1 class='big-title'>📊 Dashboard de Salários na Área de Dados</h1>", unsafe_allow_html=True)
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("📌 Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Salário médio", f"${salario_medio:,.0f}")
col2.metric("📈 Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("📊 Total de registros", f"{total_registros:,}")
col4.metric("👔 Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Ajustes visuais padrão Plotly ---
px.defaults.template = "plotly_dark"
px.defaults.color_continuous_scale = "viridis"

# --- Análises Visuais ---
st.subheader("📊 Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        if not df_ds.empty:
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(
                media_ds_pais,
                locations='residencia_iso3',
                color='usd',
                title='Salário Médio de Cientista de Dados por País',
                labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'},
                projection='natural earth',
                hover_name='residencia_iso3',
                hover_data={'usd': ':.2f'}
            )
            grafico_paises.update_layout(
                title_x=0.1,
                margin=dict(l=0, r=0, t=50, b=0),
                coloraxis_colorbar=dict(
                    title="Salário (USD)",
                    tickprefix="$",
                    ticks="outside"
                )
            )
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.warning("Nenhum dado de Data Scientist para exibir no mapa.")
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Display numérico ---
if not df_filtrado.empty:
    df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
    if not df_ds.empty:
        salario_medio_global = df_ds['usd'].mean()
        display_salario = go.Figure(go.Indicator(
            mode="number+delta",
            value=salario_medio_global,
            number={'prefix': "$", 'valueformat': ".2f"},
            delta={
                'reference': df_ds['usd'].median(),
                'relative': True,
                'valueformat': ".1%"
            },
            title={"text": "Salário Médio Global<br><span style='font-size:0.8em;color:gray'>Data Scientist</span>"}
        ))
        display_salario.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=250
        )
        st.plotly_chart(display_salario, use_container_width=True)
    else:
        st.warning("Nenhum dado de Data Scientist para exibir no display.")
else:
    st.warning("Nenhum dado para exibir no display.")

# --- Tabela ---
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado)
