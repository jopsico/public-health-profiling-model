
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os, warnings

warnings.filterwarnings("ignore")

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
IN_PATH   = os.path.join(BASE_DIR, "dados", "dados_enriquecidos.csv")
OUT_PATH  = os.path.join(BASE_DIR, "dados", "dados_com_cluster.csv")

# ── 1. Carregar dados ────────────────────────────────────────────────────────
print(" Carregando dados enriquecidos...")
df = pd.read_csv(IN_PATH)

print(f"   {len(df)} municípios prontos para a modelagem.")

# ── 2. Features para clustering ──────────────────────────────────────────────
# ── 2. Features para clustering ──────────────────────────────────────────────
FEATURES = ["atend_por_100k", "populacao", "idh"]

# 🔧 PROGRAMAÇÃO DEFENSIVA: Agora sim a variável FEATURES existe na memória
df = df.dropna(subset=FEATURES)

X = df[FEATURES].copy()

# Log na população para reduzir distorção (Fortaleza vs municípios pequenos)
X["populacao"] = np.log1p(X["populacao"])

# Normalizar
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── 3. Escolher K pelo método do cotovelo + Silhouette ────────────────────────
print("\n▶ Avaliando número de clusters...")
inertias, silhouettes = [], []

for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))
    print(f"   k={k} | Inércia: {km.inertia_:,.0f} | Silhouette: {silhouette_score(X_scaled, labels):.3f}")

# Escolhemos k=4 — boa separação e silhouette competitivo
K_FINAL = 4
print(f"\n    K escolhido: {K_FINAL}")

# ── 4. Treinar modelo final ──────────────────────────────────────────────────
print("\n▶ Treinando K-Means final...")
km_final = KMeans(n_clusters=K_FINAL, random_state=42, n_init=10)
df["cluster"] = km_final.fit_predict(X_scaled)

# ── 5. Rotular os clusters de forma legível ──────────────────────────────────
# Ordena clusters pela média de atend_por_100k (do menor para o maior)
ordem = (
    df.groupby("cluster")["atend_por_100k"]
    .mean()
    .sort_values()
    .index.tolist()
)

rotulos = {
    ordem[0]: "🔵 Baixa utilização",
    ordem[1]: "🟢 Utilização moderada",
    ordem[2]: "🟡 Alta utilização",
    ordem[3]: "🔴 Altíssima utilização",
}

df["perfil"] = df["cluster"].map(rotulos)

# ── 6. Resumo por cluster ────────────────────────────────────────────────────
print("\n▶ Resumo dos clusters:")
resumo = (
    df.groupby("perfil")
    .agg(
        municipios=("municipio", "count"),
        pop_media=("populacao", "mean"),
        idh_medio=("idh", "mean"),
        atend_100k_medio=("atend_por_100k", "mean"),
    )
    .round(2)
)
print(resumo.to_string())

# ── 7. Salvar ────────────────────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False)
print(f"\n Arquivo salvo: {OUT_PATH}")
