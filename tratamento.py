"""
tratamento.py
-------------
Lê os atendimentos SUS (DADOS.txt), enriquece com dados do IBGE
e gera o arquivo 'dados_enriquecidos.csv' usado pelo painel e pelo modelo.

Execute uma vez antes de rodar o app:
    python tratamento.py
"""

import pandas as pd
import unicodedata
import os

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DADOS_PATH = os.path.join(BASE_DIR, "dados", "DADOS.txt")
IBGE_PATH  = os.path.join(BASE_DIR, "dados", "ibge_municipios_ce.csv")
OUT_PATH   = os.path.join(BASE_DIR, "dados", "dados_enriquecidos.csv")

# ── Helpers ──────────────────────────────────────────────────────────────────
def normalizar(texto: str) -> str:
    """Remove acentos e padroniza para maiúsculas sem espaços extras."""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")

# Corrigir grafias divergentes entre a base de atendimento e o IBGE
CORRECOES = {
    "ITAPAGE": "ITAPAJE",   # ITAPAGÉ → ITAPAJÉ
}

# ── 1. Carregar atendimentos ─────────────────────────────────────────────────
print("▶ Carregando atendimentos SUS...")
df = pd.read_csv(DADOS_PATH)
df.columns = df.columns.str.strip()
df["MUNICÍPIO"] = df["MUNICÍPIO"].str.strip()

print(f"   {len(df):,} registros carregados.")
print(f"   Municípios únicos: {df['MUNICÍPIO'].nunique()}")

# ── 2. Carregar IBGE ─────────────────────────────────────────────────────────
print("\n▶ Carregando dados IBGE...")
ibge = pd.read_csv(IBGE_PATH)
print(f"   {len(ibge)} municípios do Ceará.")

# ── 3. Normalizar nomes para o join ─────────────────────────────────────────
df["mun_norm"]   = df["MUNICÍPIO"].apply(normalizar).replace(CORRECOES)
ibge["mun_norm"] = ibge["municipio"].apply(normalizar)

# ── 4. Contar atendimentos por município ────────────────────────────────────
print("\n▶ Contando atendimentos por município...")
contagem = (
    df.groupby("mun_norm")
    .agg(total_atendimentos=("ID", "count"))
    .reset_index()
)

# ── 5. Join com IBGE ─────────────────────────────────────────────────────────
print("▶ Cruzando com dados IBGE...")
merged = contagem.merge(ibge, on="mun_norm", how="left")

# Verificar municípios sem correspondência
sem_match = merged[merged["populacao"].isna()]
if not sem_match.empty:
    print(f"   ⚠️  {len(sem_match)} município(s) sem match no IBGE:")
    print(f"   {sem_match['mun_norm'].tolist()}")
else:
    print("   ✅ 100% dos municípios encontrados no IBGE.")

# ── 6. Métricas derivadas ────────────────────────────────────────────────────
print("\n▶ Calculando métricas...")

merged["atend_por_100k"] = (
    merged["total_atendimentos"] / merged["populacao"] * 100_000
).round(2)

# Validação: municípios com mais atendimentos que habitantes?
anomalos = merged[merged["total_atendimentos"] > merged["populacao"]]
print(f"   Municípios com atendimentos > população: {len(anomalos)}")
if not anomalos.empty:
    print(anomalos[["municipio", "total_atendimentos", "populacao"]])

# Rankings
merged["rank_proporcional"] = merged["atend_por_100k"].rank(
    ascending=False, method="min"
).astype(int)

# ── 7. Salvar ────────────────────────────────────────────────────────────────
colunas_finais = [
    "municipio", "regiao", "populacao", "idh",
    "total_atendimentos", "atend_por_100k", "rank_proporcional", "cod_ibge"
]
merged[colunas_finais].to_csv(OUT_PATH, index=False)

print(f"\n✅ Arquivo salvo: {OUT_PATH}")
print(f"   Shape: {merged.shape}")
print("\nPreview:")
print(merged[colunas_finais].sort_values("total_atendimentos", ascending=False).head(10).to_string(index=False))
