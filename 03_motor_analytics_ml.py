# =============================================================================
# FASE 2 - PROJETO BI & ANALYTICS | PUCRS Online
# Estudante: Leticia Ayumi Akaichi
# Script 03: Motor de Analytics — Classificador Preditivo de Atraso Logístico
# Descrição: Treina um modelo Random Forest sobre a tabela fato para predizer
#            a probabilidade de estouro de SLA (flg_atraso = 1).
#            Avalia o modelo com métricas padrão de classificação e exibe a
#            importância de cada variável explicativa para a tomada de decisão.
# Pré-requisito: Executar o Script 02 para gerar 'fato_pedidos.csv'.
# =============================================================================

# ── Célula 1: Instalação e Importações ───────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)

# Configurações visuais
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

SEED = 42
print("✅ Bibliotecas carregadas.")


# ── Célula 2: Ingestão da Tabela Fato ────────────────────────────────────────
print("\n📥 Carregando 'fato_pedidos.csv'...")

fato_pedidos = pd.read_csv("fato_pedidos.csv", encoding="utf-8-sig")

print(f"   Registros carregados : {len(fato_pedidos)}")
print(f"   Colunas disponíveis  : {list(fato_pedidos.columns)}")
print(f"\n   Prévia dos dados:\n{fato_pedidos.head(3).to_string(index=False)}")


# ── Célula 3: Definição das Variáveis do Modelo ───────────────────────────────
print("\n🎯 Definindo features (X) e variável alvo (y)...")

# Variáveis explicativas — sinais observáveis no momento da compra
FEATURES = [
    "sk_transportadora",       # Qual transportadora foi selecionada
    "dia_semana_faturamento",  # Pedidos no fim de semana tendem a atrasar
    "volume_fila_estoque",     # Gargalo interno antes da expedição
]

# Variável alvo — flag binária de estouro de SLA
TARGET = "flg_atraso"

X = fato_pedidos[FEATURES]
y = fato_pedidos[TARGET]

print(f"   Features (X) : {FEATURES}")
print(f"   Target   (y) : '{TARGET}'")
print(f"\n   Distribuição do target:")
print(f"   {y.value_counts().rename({0: 'No prazo (0)', 1: 'Em atraso (1)'}).to_string()}")
print(f"   Balanceamento: {y.mean()*100:.1f}% de atrasos")


# ── Célula 4: Divisão Treino/Teste (70% / 30%) ───────────────────────────────
print("\n✂️  Dividindo dados em treino (70%) e teste (30%)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size    = 0.30,
    random_state = SEED,
    stratify     = y,          # Preserva a proporção de atrasos em ambos os conjuntos
)

print(f"   Treino : {len(X_train)} registros ({len(X_train)/len(X)*100:.0f}%)")
print(f"   Teste  : {len(X_test)} registros ({len(X_test)/len(X)*100:.0f}%)")
print(f"   Taxa de atraso no treino : {y_train.mean()*100:.1f}%")
print(f"   Taxa de atraso no teste  : {y_test.mean()*100:.1f}%")


# ── Célula 5: Treinamento do Modelo — Random Forest ──────────────────────────
print("\n🌳 Treinando RandomForestClassifier (n_estimators=100)...")

modelo_rf = RandomForestClassifier(
    n_estimators = 100,        # 100 árvores de decisão em ensemble
    random_state = SEED,
    n_jobs       = -1,         # Usar todos os núcleos disponíveis
)

modelo_rf.fit(X_train, y_train)
print("   ✅ Modelo treinado com sucesso.")


# ── Célula 6: Predição e Avaliação do Modelo ─────────────────────────────────
print("\n📈 Avaliando desempenho no conjunto de teste...")

y_pred = modelo_rf.predict(X_test)

# ── 6.1: Acurácia Global
acuracia = accuracy_score(y_test, y_pred)
print(f"\n{'='*55}")
print(f"  ACURÁCIA GLOBAL DO MODELO : {acuracia * 100:.2f}%")
print(f"{'='*55}")

# ── 6.2: Matriz de Confusão
print("\n📊 MATRIZ DE CONFUSÃO:")
cm = confusion_matrix(y_test, y_pred)
print(f"\n  Labels   : [No Prazo (0)] [Em Atraso (1)]")
print(f"\n  {'':15} Predito 0   Predito 1")
print(f"  Real 0 (Prazo)  :   {cm[0,0]:5d}       {cm[0,1]:5d}")
print(f"  Real 1 (Atraso) :   {cm[1,0]:5d}       {cm[1,1]:5d}")

tn, fp, fn, tp = cm.ravel()
print(f"\n  Verdadeiros Negativos (TN) : {tn}  — no prazo corretamente identificados")
print(f"  Falsos Positivos      (FP) : {fp}  — alarmes falsos de atraso")
print(f"  Falsos Negativos      (FN) : {fn}  — atrasos não detectados (crítico!)")
print(f"  Verdadeiros Positivos (TP) : {tp}  — atrasos corretamente identificados")

# ── 6.3: Classification Report
print(f"\n📋 CLASSIFICATION REPORT (Precision / Recall / F1-Score):")
print("-" * 55)
print(classification_report(
    y_test, y_pred,
    target_names=["No Prazo (0)", "Em Atraso (1)"]
))


# ── Célula 7: Importância das Variáveis (Feature Importances) ────────────────
print("\n🔍 IMPORTÂNCIA DAS VARIÁVEIS EXPLICATIVAS NO RISCO DE ATRASO:")
print("-" * 55)

importancias = pd.Series(
    modelo_rf.feature_importances_,
    index=FEATURES
).sort_values(ascending=False)

for feature, importancia in importancias.items():
    barra = "█" * int(importancia * 50)
    print(f"  {feature:<30} {importancia:.4f}  {barra}")

print(f"\n  Variável de maior impacto : '{importancias.idxmax()}' "
      f"({importancias.max()*100:.1f}% de importância)")


# ── Célula 8: Visualizações ──────────────────────────────────────────────────
print("\n🎨 Gerando visualizações do modelo...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(
    "Motor de Analytics — Predição de Atraso Logístico\nRandom Forest Classifier",
    fontsize=13, fontweight="bold"
)

# Plot 1: Matriz de Confusão normalizada
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["No Prazo (0)", "Em Atraso (1)"]
)
disp.plot(ax=axes[0], colorbar=False, cmap="Blues")
axes[0].set_title("Matriz de Confusão", fontsize=11, fontweight="bold")
axes[0].set_xlabel("Predição do Modelo", fontsize=10)
axes[0].set_ylabel("Valor Real", fontsize=10)

# Plot 2: Importância das variáveis
cores = ["#1a6e9a" if i == 0 else "#3badd6" for i in range(len(importancias))]
axes[1].barh(importancias.index[::-1], importancias.values[::-1], color=cores[::-1])
axes[1].set_title("Importância das Variáveis\n(Feature Importances)", fontsize=11, fontweight="bold")
axes[1].set_xlabel("Importância Relativa", fontsize=10)
axes[1].set_xlim(0, importancias.max() * 1.25)
for i, v in enumerate(importancias.values[::-1]):
    axes[1].text(v + 0.005, i, f"{v:.4f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("analytics_model_results.png", bbox_inches="tight", dpi=150)
plt.show()
print("   ✅ Gráfico salvo em 'analytics_model_results.png'.")


# ── Célula 9: Síntese Executiva ───────────────────────────────────────────────
print("\n" + "="*60)
print("📌 SÍNTESE EXECUTIVA — RESULTADOS DO MOTOR DE ANALYTICS")
print("="*60)
print(f"""
Modelo     : Random Forest Classifier (100 árvores)
Features   : {FEATURES}
Target     : '{TARGET}' (1 = estouro de SLA > 5 dias)

Desempenho:
  Acurácia Global  : {acuracia*100:.2f}%
  Registros treino : {len(X_train)}
  Registros teste  : {len(X_test)}

Top variável preditora de atraso:
  '{importancias.idxmax()}' ({importancias.max()*100:.1f}% de peso)

Recomendação estratégica:
  Os resultados indicam que a escolha da transportadora e o volume
  de fila no estoque são os fatores com maior influência no risco
  de atraso. A diretoria pode usar este modelo para priorizar
  auditorias em contratos com transportadoras de alto risco e
  otimizar a capacidade de separação em períodos de pico.
""")

print("✅ Etapa 3 concluída. Pipeline de BI Analytics operacional.")
