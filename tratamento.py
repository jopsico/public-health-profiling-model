
import pandas as pd
import requests
import unicodedata
import os

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DADOS_PATH = os.path.join(BASE_DIR, "dados", "DADOS.txt")
IDH_PATH   = os.path.join(BASE_DIR, "dados", "dataatlas.xlsx")
OUT_PATH   = os.path.join(BASE_DIR, "dados", "dados_enriquecidos.csv")

# ── Helpers ──────────────────────────────────────────────────────────────────
def normalizar(texto: str) -> str:
    """Remove acentos e padroniza para maiúsculas sem espaços extras."""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

CORRECOES = {
    "ITAPAGE": "ITAPAJE",
}

print("▶ Iniciando pipeline de processamento...")

# ── 1. API IBGE: Municípios e Regiões ───────────────────────────────────────
print("   [1/5] Consumindo API do IBGE (Cidades e Regiões)...")
url_mun = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/23/municipios"
mun_res = requests.get(url_mun).json()

df_mun = pd.DataFrame([{
    "cod_ibge": int(m["id"]),
    "municipio": m["nome"],
    "regiao": m["microrregiao"]["mesorregiao"]["nome"],
    "mun_norm": normalizar(m["nome"])
} for m in mun_res])

# ── 2. API IBGE: População (Censo 2022) ─────────────────────────────────────
print("   [2/5] Consumindo API do IBGE (População Censo 2022)...")
url_pop = "https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93?localidades=N6[N3[23]]"
pop_res = requests.get(url_pop).json()

pop_list = []
for item in pop_res[0]['resultados'][0]['series']:
    cod_ibge = int(item['localidade']['id'])
    pop = int(item['serie']['2022'])
    pop_list.append({"cod_ibge": cod_ibge, "populacao": pop})

df_pop = pd.DataFrame(pop_list)

# Junta municípios com a população recém-extraída
df_ibge = df_mun.merge(df_pop, on="cod_ibge", how="left")

# ── 3. Arquivo Local: IDH (Excel original do Atlas Brasil) ──────────────────
print("   [3/5] Carregando dados de IDH direto do Excel (dataatlas.xlsx)...")
df_idh = pd.read_excel(IDH_PATH)
df_idh["mun_norm"] = df_idh["Territorialidade"].str.replace(" (CE)", "", regex=False).apply(normalizar)
df_idh = df_idh[["mun_norm", "IDHM"]].rename(columns={"IDHM": "idh"})

# ── 4. Arquivo Local: Atendimentos SUS ──────────────────────────────────────
print("   [4/5] Carregando e agregando atendimentos SUS...")
df_sus = pd.read_csv(DADOS_PATH)
df_sus.columns = df_sus.columns.str.strip()
df_sus["mun_norm"] = df_sus["MUNICÍPIO"].apply(normalizar).replace(CORRECOES)

contagem = (
    df_sus.groupby("mun_norm")
    .agg(total_atendimentos=("ID", "count"))
    .reset_index()
)

# ── 5. Cruzamento de Dados (Join) e Métricas ────────────────────────────────
print("   [5/5] Cruzando bases e calculando proporções...")
merged = contagem.merge(df_ibge, on="mun_norm", how="left")
merged = merged.merge(df_idh, on="mun_norm", how="left")

# Validação de quebras
sem_match = merged[merged["populacao"].isna()]
if not sem_match.empty:
    print(f"    AVISO: {len(sem_match)} município(s) do SUS sem match no IBGE: {sem_match['mun_norm'].tolist()}")

# Cálculo final de KPIs
merged["atend_por_100k"] = (
    merged["total_atendimentos"] / merged["populacao"] * 100_000
).round(2)

merged["rank_proporcional"] = merged["atend_por_100k"].rank(
    ascending=False, method="min"
).astype(int)

# ── Exportação ──────────────────────────────────────────────────────────────
colunas_finais = [
    "municipio", "regiao", "populacao", "idh",
    "total_atendimentos", "atend_por_100k", "rank_proporcional", "cod_ibge"
]

df_final = merged[colunas_finais]
df_final.to_csv(OUT_PATH, index=False)

print(f"\n Pipeline concluído com sucesso! Arquivo gerado em: {OUT_PATH}")