
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Atendimentos SUS – Ceará",
    page_icon=":material/health_and_safety:",
    layout="wide",
)

# ── Carregar dados ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)

@st.cache_data
def carregar():
    path = os.path.join(BASE_DIR, "dados", "dados_com_cluster.csv")
    return pd.read_csv(path)

df = carregar()

# ── Header ───────────────────────────────────────────────────────────────────
st.title(":material/health_metrics: Atendimentos SUS — Ceará")
st.caption("Análise enriquecida com dados IBGE (Censo 2022) · 204.579 registros")

# ── Abas principais ──────────────────────────────────────────────────────────
aba1, aba2, aba3, aba4 = st.tabs([
    ":material/analytics: Visão Geral",
    ":material/location_city: Por Município",
    ":material/map: Mapa",
    ":material/person_search: Modelo de Perfis",
])

# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ════════════════════════════════════════════════════════════════════════════
with aba1:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de atendimentos", f"{df['total_atendimentos'].sum():,}")
    c2.metric("Municípios analisados", f"{len(df)}")
    c3.metric("Média atend./100k hab.", f"{df['atend_por_100k'].mean():,.0f}")
    c4.metric("IDH médio do estado", f"{df['idh'].mean():.3f}")

    st.divider()

    # Volume por região
    st.subheader("Volume de atendimentos por região")
    regiao = (
        df.groupby("regiao")
        .agg(atendimentos=("total_atendimentos", "sum"), municipios=("municipio", "count"))
        .reset_index()
        .sort_values("atendimentos", ascending=True)
    )

    fig_regiao = px.bar(
        regiao,
        x="atendimentos",
        y="regiao",
        orientation="h",
        color="atendimentos",
        color_continuous_scale="Blues",
        text="atendimentos",
        labels={"regiao": "Região", "atendimentos": "Atendimentos"},
    )
    fig_regiao.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_regiao.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
    st.plotly_chart(fig_regiao, use_container_width=True)

    # Proporção por 100k por região
    st.subheader("Atendimentos por 100 mil habitantes — média por região")
    regiao_100k = (
        df.groupby("regiao")["atend_por_100k"]
        .mean()
        .reset_index()
        .sort_values("atend_por_100k", ascending=True)
    )

    fig_100k = px.bar(
        regiao_100k,
        x="atend_por_100k",
        y="regiao",
        orientation="h",
        color="atend_por_100k",
        color_continuous_scale="Oranges",
        text="atend_por_100k",
        labels={"regiao": "Região", "atend_por_100k": "Atend./100k hab."},
    )
    fig_100k.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_100k.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
    st.plotly_chart(fig_100k, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — POR MUNICÍPIO
# ════════════════════════════════════════════════════════════════════════════
with aba2:
    st.subheader("Ranking: municípios com maior e menor atendimento proporcional")

    col_top, col_bot = st.columns(2)

    top10 = df.nlargest(10, "atend_por_100k")[["municipio", "atend_por_100k", "populacao", "regiao"]]
    bot10 = df.nsmallest(10, "atend_por_100k")[["municipio", "atend_por_100k", "populacao", "regiao"]]

    with col_top:
        st.markdown("#### :material/keyboard_arrow_up: Top 10 — maior proporção")
        fig_top = px.bar(
            top10.sort_values("atend_por_100k"),
            x="atend_por_100k", y="municipio",
            orientation="h",
            color="atend_por_100k",
            color_continuous_scale="Reds",
            text="atend_por_100k",
            labels={"atend_por_100k": "Atend./100k", "municipio": ""},
        )
        fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_top.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_bot:
        st.markdown("#### :material/keyboard_arrow_down: Bottom 10 — menor proporção")
        fig_bot = px.bar(
            bot10.sort_values("atend_por_100k", ascending=False),
            x="atend_por_100k", y="municipio",
            orientation="h",
            color="atend_por_100k",
            color_continuous_scale="Blues",
            text="atend_por_100k",
            labels={"atend_por_100k": "Atend./100k", "municipio": ""},
        )
        fig_bot.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_bot.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_bot, use_container_width=True)

    st.divider()
    st.subheader("Relação entre IDH e atendimentos proporcionais")

    regioes = ["Todas"] + sorted(df["regiao"].unique().tolist())
    regiao_sel = st.selectbox("Filtrar por região:", regioes)

    df_scatter = df if regiao_sel == "Todas" else df[df["regiao"] == regiao_sel]

    fig_scatter = px.scatter(
        df_scatter,
        x="idh",
        y="atend_por_100k",
        size="populacao",
        color="regiao",
        hover_name="municipio",
        hover_data={"populacao": ":,", "total_atendimentos": ":,"},
        labels={"idh": "IDH (2010)", "atend_por_100k": "Atend./100k hab.", "regiao": "Região"},
        title="Cada bolha = 1 município | Tamanho = população",
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader(":material/table: Tabela completa")
    st.dataframe(
        df[["municipio", "regiao", "populacao", "idh", "total_atendimentos", "atend_por_100k", "rank_proporcional"]]
        .sort_values("total_atendimentos", ascending=False)
        .reset_index(drop=True)
        .rename(columns={
            "municipio": "Município",
            "regiao": "Região",
            "populacao": "População",
            "idh": "IDH",
            "total_atendimentos": "Atendimentos",
            "atend_por_100k": "Atend./100k",
            "rank_proporcional": "Ranking",
        }),
        use_container_width=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# ABA 3 — MAPA
# ════════════════════════════════════════════════════════════════════════════
with aba3:
    st.subheader("Mapa interativo — Municípios do Ceará")
    st.info(":material/lightbulb: Passe o mouse sobre os pontos para ver detalhes de cada município.")

    # Coordenadas aproximadas dos municípios do CE (centroide por nome normalizado)
    # Usamos um dicionário com os principais municípios + fallback por região
    COORDS = {
        "FORTALEZA": (-3.7172, -38.5433), "CAUCAIA": (-3.7369, -38.6564),
        "JUAZEIRO DO NORTE": (-7.2133, -39.3153), "MARACANAÚ": (-3.7814, -38.6249),
        "SOBRAL": (-3.6861, -40.3490), "CRATO": (-7.2342, -39.4095),
        "ITAPIPOCA": (-3.4922, -39.5785), "MARANGUAPE": (-3.8889, -38.6827),
        "IGUATU": (-6.3600, -39.2990), "QUIXADÁ": (-4.9709, -39.0150),
        "TIANGUÁ": (-3.7281, -40.9929), "CANINDÉ": (-4.3570, -39.3139),
        "PACAJUS": (-4.1731, -38.4606), "AQUIRAZ": (-3.9011, -38.3906),
        "RUSSAS": (-4.9406, -37.9764), "LIMOEIRO DO NORTE": (-5.1467, -38.0992),
        "MORADA NOVA": (-5.1086, -38.3726), "CAMOCIM": (-2.9017, -40.8411),
        "ARACATI": (-4.5625, -37.7706), "BARBALHA": (-7.3100, -39.3010),
        "BREJO SANTO": (-7.4914, -38.9894), "CRATEÚS": (-5.1775, -40.6740),
        "ICÓ": (-6.4010, -38.8617), "TAUÁ": (-5.9889, -40.2938),
        "BOA VIAGEM": (-5.1237, -39.7280), "QUIXERAMOBIM": (-5.1982, -39.2841),
        "CASCAVEL": (-4.1334, -38.2358), "PACATUBA": (-3.9780, -38.6167),
        "ITAPAJÉ": (-3.6869, -39.5836), "TRAIRI": (-3.2784, -39.2687),
        "ITAREMA": (-2.9239, -39.9105), "ACARAÚ": (-2.8853, -40.1197),
        "BATURITÉ": (-4.3283, -38.8817), "HORIZONTE": (-4.1012, -38.4914),
        "EUSÉBIO": (-3.8892, -38.4547), "REDENÇÃO": (-4.2253, -38.7282),
        "GUARAMIRANGA": (-4.2706, -38.9361), "GRANJA": (-3.1153, -40.8286),
        "MASSAPÊ": (-3.5250, -40.3392), "SÃO BENEDITO": (-4.0492, -40.8672),
        "GUARACIABA DO NORTE": (-4.1650, -40.7469), "TIANGUÁ": (-3.7281, -40.9929),
        "UBAJARA": (-3.8536, -40.9197), "IBIAPINA": (-3.9231, -40.8894),
        "VIÇOSA DO CEARÁ": (-3.5628, -41.0933), "BELA CRUZ": (-2.9939, -40.1694),
        "AMONTADA": (-3.3639, -39.8281), "JIJOCA DE JERICOACOARA": (-2.7939, -40.5097),
        "BEBERIBE": (-4.1786, -38.1283), "PINDORETAMA": (-4.0178, -38.3072),
        "CHOROZINHO": (-4.3050, -38.4967), "GUAIÚBA": (-4.0525, -38.6267),
        "SÃO GONÇALO DO AMARANTE": (-3.6025, -38.9753),
        "ITAITINGA": (-3.9706, -38.5247), "OCARA": (-4.4869, -38.5944),
        "PARAIPABA": (-3.4325, -39.1494), "PARACURU": (-3.4114, -39.0278),
        "JAGUARIBE": (-5.8939, -38.6194), "LIMOEIRO DO NORTE": (-5.1467, -38.0992),
        "JAGUARUANA": (-4.8339, -37.7819), "TABULEIRO DO NORTE": (-5.2406, -38.1178),
        "QUIXERÉ": (-5.0722, -37.9775), "RUSSAS": (-4.9406, -37.9764),
        "MORADA NOVA": (-5.1086, -38.3726), "IRACEMA": (-5.8197, -38.3572),
        "CAMPOS SALES": (-7.0686, -40.3719), "ARARIPE": (-7.2072, -40.1297),
        "SALITRE": (-7.3086, -40.4456), "MISSÃO VELHA": (-7.2492, -39.1428),
        "AURORA": (-6.9489, -38.9750), "BARRO": (-7.1742, -38.7872),
        "MAURITI": (-7.3856, -38.7663), "CARIRIAÇU": (-7.0381, -39.2817),
        "JARDIM": (-7.0811, -39.3083), "ALTANEIRA": (-7.0108, -39.3619),
        "NOVA OLINDA": (-7.0867, -39.6736), "SANTANA DO CARIRI": (-7.1850, -39.7400),
        "ABAIARA": (-7.3472, -39.0430), "PENAFORTE": (-7.8083, -39.0156),
        "GRANJEIRO": (-6.8997, -39.2156), "POTENGI": (-7.0781, -39.0453),
        "JATI": (-7.6936, -38.9225), "PORTEIRAS": (-7.5267, -39.1083),
        "SENADOR POMPEU": (-5.5825, -39.3681), "PEDRA BRANCA": (-5.4594, -39.7217),
        "MOMBAÇA": (-5.7422, -39.6264), "SOLONÓPOLE": (-5.7181, -39.0019),
        "PIQUET CARNEIRO": (-5.7453, -39.4131), "DEPUTADO IRAPUAN PINHEIRO": (-5.8731, -39.2897),
        "CARIDADE": (-4.2261, -39.1883), "CAPISTRANO": (-4.4681, -38.9111),
        "ARACOIABA": (-4.3569, -38.8150), "ARATUBA": (-4.4122, -39.0492),
        "MULUNGU": (-4.3094, -38.9992), "PACOTI": (-4.2261, -38.9272),
        "PALMÁCIA": (-4.1461, -38.8544), "ITATIRA": (-4.5319, -39.6178),
        "MADALENA": (-4.8608, -39.5686), "BANABUIÚ": (-5.3150, -38.8819),
        "BOA VIAGEM": (-5.1237, -39.7280), "CANINDÉ": (-4.3570, -39.3139),
        "SANTA QUITÉRIA": (-4.3356, -40.1483), "CARIRÉ": (-3.9481, -40.4719),
        "SOBRAL": (-3.6861, -40.3490), "FORQUILHA": (-3.8047, -40.2578),
        "MERUOCA": (-3.5444, -40.4547), "ALCÂNTARAS": (-3.5772, -40.5514),
        "SANTANA DO ACARAÚ": (-3.4614, -40.2094), "URUOCA": (-3.3256, -40.5458),
        "COREAÚ": (-3.5439, -40.6478), "SENADOR SÁ": (-3.3494, -40.4764),
        "MORAÚJO": (-3.4647, -40.6783), "CHAVAL": (-3.0131, -41.2383),
        "BARROQUINHA": (-3.0286, -41.1358), "CAMOCIM": (-2.9017, -40.8411),
        "MARTINÓPOLE": (-3.2100, -40.6981), "FRECHEIRINHA": (-3.7581, -40.8153),
        "MUCAMBO": (-3.9028, -40.7408), "GRAÇA": (-4.0492, -40.7514),
        "CARNAUBAL": (-4.1681, -40.9336), "CROATA": (-4.4089, -40.9022),
        "PORANGA": (-4.7419, -40.9269), "NOVA RUSSAS": (-4.7108, -40.5650),
        "RERIUTABA": (-4.1553, -40.5736), "GROAÍRAS": (-3.9308, -40.4153),
        "MASSAPÊ": (-3.5250, -40.3392), "IRAUÇUBA": (-3.7444, -39.7869),
        "APUIARÉS": (-3.9489, -39.4111), "TEJUÇUOCA": (-3.9908, -39.5819),
        "GENERAL SAMPAIO": (-4.0508, -39.4578), "ITAPAJÉ": (-3.6869, -39.5836),
        "PENTECOSTE": (-3.7908, -39.2703), "UMIRIM": (-3.6881, -39.3408),
        "URUBURETAMA": (-3.6481, -39.5136), "SÃO LUÍS DO CURU": (-3.6719, -39.2336),
        "PARAMOTI": (-4.0978, -39.2881), "TURURU": (-3.4647, -39.4461),
        "TRAIRI": (-3.2784, -39.2687), "PARACURU": (-3.4114, -39.0278),
        "PARAIPABA": (-3.4325, -39.1494), "ACOPIARA": (-6.0978, -39.4528),
        "JUCÁS": (-6.5194, -39.5236), "ORÓS": (-6.2433, -38.9092),
        "VÁRZEA ALEGRE": (-6.8008, -39.2936), "ICÓ": (-6.4010, -38.8617),
        "IPAUMIRIM": (-6.7917, -38.7175), "BAIXIO": (-6.9989, -38.5606),
        "LAVRAS DA MANGABEIRA": (-6.7531, -38.9719), "UMARI": (-6.6469, -38.7092),
        "CEDRO": (-6.5992, -39.0522), "SABOEIRO": (-6.5344, -39.9031),
        "AIUABA": (-6.5719, -40.0869), "ARNEIROZ": (-6.3569, -40.0733),
        "TARRAFAS": (-6.6331, -39.8381), "CATARINA": (-6.1281, -39.8800),
        "QUIXELÔ": (-6.2508, -39.1511), "ANTONINA DO NORTE": (-6.7772, -39.9653),
        "ERERÊ": (-6.0236, -38.3694), "IRACEMA": (-5.8197, -38.3572),
        "JAGUARETAMA": (-5.6122, -38.7714), "JAGUARIBARA": (-5.6019, -38.4814),
        "IBICUITINGA": (-5.0494, -38.6272), "PEREIRO": (-6.0356, -38.4542),
        "POTIRETAMA": (-5.6836, -38.0611), "ITATIRA": (-4.5319, -39.6178),
        "ITAIÇABA": (-4.8275, -37.8319), "PALHANO": (-4.7436, -37.9714),
        "FORTIM": (-4.4553, -37.7975), "ICAPUÍ": (-4.7147, -37.3597),
        "ARACATI": (-4.5625, -37.7706), "JAGUARUANA": (-4.8339, -37.7819),
        "MORRINHOS": (-3.2344, -40.1247), "MARCO": (-2.7272, -40.1358),
        "BELA CRUZ": (-2.9939, -40.1694), "CRUZ": (-2.9281, -40.1706),
        "JIJOCA DE JERICOACOARA": (-2.7939, -40.5097),
        "HIDROLÂNDIA": (-4.4094, -40.4381), "IPÚ": (-4.3214, -40.7133),
        "VARJOTA": (-4.1931, -40.4697), "PIRES FERREIRA": (-4.2392, -40.6494),
        "CATUNDA": (-4.6489, -40.2011), "INDEPENDÊNCIA": (-5.3936, -40.3169),
        "TAMBORIL": (-5.0631, -40.3167), "IPAPORANGA": (-4.9461, -40.7658),
        "MONSENHOR TABOSA": (-4.7928, -40.0569), "PARAMBU": (-6.2264, -40.6967),
        "QUITERIANÓPOLIS": (-5.6533, -40.8069), "NOVO ORIENTE": (-5.5267, -40.7794),
        "NOVA RUSSAS": (-4.7108, -40.5650), "CROATÁ": (-4.4089, -40.9022),
        "IBARETAMA": (-4.8178, -38.9956), "CHORÓ": (-4.8436, -39.1267),
        "MIRAÍMA": (-3.5639, -39.9683), "AMONTADA": (-3.3639, -39.8281),
        "ITAREMA": (-2.9239, -39.9105), "ACARAPE": (-4.2236, -38.7031),
        "BARREIRA": (-4.2883, -38.6408), "GUAIÚBA": (-4.0525, -38.6267),
        "MARACANAÚ": (-3.7814, -38.6249), "ITAITINGA": (-3.9706, -38.5247),
        "HORIZONTE": (-4.1012, -38.4914), "PACAJUS": (-4.1731, -38.4606),
        "PINDORETAMA": (-4.0178, -38.3072), "CASCAVEL": (-4.1334, -38.2358),
        "BEBERIBE": (-4.1786, -38.1283), "FORTIM": (-4.4553, -37.7975),
        "PITOMBEIRAS": (-5.8981, -37.9267), "MILHÃ": (-5.7594, -39.1900),
        "IBICUITINGA": (-5.0494, -38.6272), "PIQUET CARNEIRO": (-5.7453, -39.4131),
        "FARIAS BRITO": (-6.9278, -39.5669), "CARIRIAÇU": (-7.0381, -39.2817),
        "ITAPAJÉ": (-3.6869, -39.5836),
        "SANTA QUITÉRIA": (-4.3356, -40.1483),
    }

    # Fallback: centróide por região
    CENTROIDE_REGIAO = {
        "Região Metropolitana de Fortaleza": (-3.85, -38.55),
        "Litoral Norte": (-3.0, -39.8),
        "Litoral Leste": (-4.6, -38.0),
        "Serra da Ibiapaba": (-4.0, -40.8),
        "Maciço de Baturité": (-4.3, -38.9),
        "Sertão Central": (-5.2, -39.4),
        "Sertão dos Inhamuns": (-5.5, -40.5),
        "Noroeste": (-3.7, -40.4),
        "Norte": (-3.8, -39.4),
        "Jaguaribe": (-5.5, -38.3),
        "Centro-Sul": (-6.4, -39.2),
        "Cariri": (-7.2, -39.3),
        "Região Metropolitana do Cariri": (-7.2, -39.3),
    }

    def get_coords(row):
        nome = row["municipio"].upper()
        if nome in COORDS:
            return COORDS[nome]
        return CENTROIDE_REGIAO.get(row["regiao"], (-5.0, -39.5))

    df["lat"] = df.apply(lambda r: get_coords(r)[0], axis=1)
    df["lon"] = df.apply(lambda r: get_coords(r)[1], axis=1)

    metrica_map = st.radio(
        "Colorir por:",
        ["Total de atendimentos", "Atend. por 100k hab.", "IDH"],
        horizontal=True,
    )

    col_map = {
        "Total de atendimentos": "total_atendimentos",
        "Atend. por 100k hab.": "atend_por_100k",
        "IDH": "idh",
    }[metrica_map]

    fig_map = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color=col_map,
        size="total_atendimentos",
        hover_name="municipio",
        hover_data={
            "regiao": True,
            "populacao": ":,",
            "total_atendimentos": ":,",
            "atend_por_100k": ":.0f",
            "idh": ":.3f",
            "lat": False,
            "lon": False,
        },
        color_continuous_scale="YlOrRd",
        size_max=40,
        zoom=6,
        center={"lat": -5.1, "lon": -39.3},
        mapbox_style="carto-positron",
        height=600,
        labels={col_map: metrica_map},
    )
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# ABA 4 — MODELO DE PERFIS (K-MEANS)
# ════════════════════════════════════════════════════════════════════════════
with aba4:
    st.subheader("🤖 Modelo de Perfis — K-Means Clustering")

    st.markdown("""
    O modelo agrupa os **184 municípios do Ceará** em 4 perfis de utilização do SUS,
    com base em 3 variáveis:

    | Variável | Significado |
    |---|---|
    | `atend_por_100k` | Intensidade proporcional de uso do SUS |
    | `populacao` (log) | Porte do município |
    | `idh` | Nível de desenvolvimento humano |

    > **Por que K-Means?** Não temos série temporal, então não é possível prever demanda futura.
    > O clustering permite identificar padrões estruturais — municípios com comportamentos
    > semelhantes — o que é mais honesto e útil com os dados disponíveis.
    """)

    st.divider()

    # Resumo dos clusters
    resumo = (
        df.groupby("perfil")
        .agg(
            Municípios=("municipio", "count"),
            Pop_média=("populacao", "mean"),
            IDH_médio=("idh", "mean"),
            Atend_100k_médio=("atend_por_100k", "mean"),
        )
        .round(2)
        .reset_index()
        .rename(columns={
            "perfil": "Perfil",
            "Pop_média": "Pop. média",
            "IDH_médio": "IDH médio",
            "Atend_100k_médio": "Atend./100k médio",
        })
    )
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    st.divider()

    # Scatter 3D
    st.subheader("Visualização dos clusters")
    # Mapeamento estrito de cores associado aos rótulos do seu K-Means
    mapa_cores = {
        "🔵 Baixa utilização": "#3b82f6",      # Azul
        "🟢 Utilização moderada": "#22c55e",   # Verde
        "🟡 Alta utilização": "#eab308",       # Amarelo
        "🔴 Altíssima utilização": "#ef4444"   # Vermelho
    }
    ordem_desejada = [
        "🔴 Altíssima utilização",
        "🟡 Alta utilização",
        "🟢 Utilização moderada",
        "🔵 Baixa utilização"
    ]
    fig_cluster = px.scatter_3d(
        df,
        x="idh",
        y="populacao",
        z="atend_por_100k",
        color="perfil",
        color_discrete_map=mapa_cores,
        category_orders={"perfil": ordem_desejada},
        hover_name="municipio",
        labels={
            "idh": "IDH",
            "populacao": "População",
            "atend_por_100k": "Atend./100k",
            "perfil": "Perfil",
        },
        title="Clusters em 3D — cada ponto é um município",
        height=550,
    )
    st.plotly_chart(fig_cluster, use_container_width=True)

    st.divider()

    # Municípios por cluster com filtro
    st.subheader("Municípios por perfil")
    perfil_sel = st.selectbox("Selecionar perfil:", sorted(df["perfil"].unique()))
    df_perfil = df[df["perfil"] == perfil_sel][
        ["municipio", "regiao", "populacao", "idh", "total_atendimentos", "atend_por_100k"]
    ].sort_values("atend_por_100k", ascending=False).reset_index(drop=True)
    df_perfil.columns = ["Município", "Região", "População", "IDH", "Atendimentos", "Atend./100k"]
    st.dataframe(df_perfil, use_container_width=True)
