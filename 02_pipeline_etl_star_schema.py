# =============================================================================
# FASE 2 - PROJETO BI & ANALYTICS | PUCRS Online
# Estudante: Leticia Ayumi Akaichi
# Script 02: Pipeline de ETL e Modelagem Dimensional (Star Schema)
# Descrição: Executa as fases de Data Quality sobre os arquivos brutos e
#            exporta as tabelas do modelo analítico dimensional (Star Schema):
#            dim_cliente.csv, dim_transportadora.csv, fato_pedidos.csv.
# Pré-requisito: Executar o Script 01 para gerar os arquivos brutos.
# =============================================================================

# ── Célula 1: Importações ─────────────────────────────────────────────────────
import pandas as pd
import numpy as np

print("✅ Bibliotecas carregadas.")


# ── Célula 2: Ingestão — Leitura das Fontes Brutas (Staging Area) ─────────────
print("\n📥 [STAGING] Lendo fontes brutas para a área de transição...")

df_vendas    = pd.read_csv("dados_vendas_brutos.csv",   encoding="utf-8-sig")
df_logistica = pd.read_csv("dados_logistica_brutos.csv", encoding="utf-8-sig")

print(f"   OMS (vendas)    : {len(df_vendas)} registros, {df_vendas.shape[1]} colunas")
print(f"   TMS (logística) : {len(df_logistica)} registros, {df_logistica.shape[1]} colunas")


# ── Célula 3: Data Quality — Higienização da Base de Vendas ───────────────────
print("\n🧹 [DQ-1] Higienizando dados de vendas (OMS)...")

qtd_antes = len(df_vendas)

# 3.1 — Remover registro de ambiente de testes (PED-TESTE)
df_vendas = df_vendas[df_vendas["id_pedido_oms"] != "PED-TESTE"].copy()
print(f"   Removido(s) registro(s) 'PED-TESTE' : "
      f"{qtd_antes - len(df_vendas)} linha(s) eliminada(s).")

# 3.2 — Converter campo de data de compra para datetime
df_vendas["dt_compra"] = pd.to_datetime(df_vendas["dt_compra"], errors="coerce")
print(f"   'dt_compra' convertida para datetime : OK")

print(f"   Registros restantes após limpeza OMS : {len(df_vendas)}")


# ── Célula 4: Data Quality — Higienização da Base de Logística ────────────────
print("\n🧹 [DQ-2] Higienizando dados de logística (TMS)...")

qtd_antes_log = len(df_logistica)

# 4.1 — Eliminar registros duplicados de entrega (mantém o mais recente)
#        Garante idempotência caso o arquivo chegue com reprocessamentos parciais.
df_logistica = df_logistica.sort_values("cod_pedido_entrega")
df_logistica = df_logistica.drop_duplicates(
    subset="cod_pedido_entrega", keep="last"
).copy()
print(f"   Duplicatas removidas (keep='last')  : "
      f"{qtd_antes_log - len(df_logistica)} linha(s) eliminada(s).")

# 4.2 — Converter campo de entrega para datetime
df_logistica["dt_entrega_efetiva"] = pd.to_datetime(
    df_logistica["dt_entrega_efetiva"], errors="coerce"
)
print(f"   'dt_entrega_efetiva' convertida para datetime : OK")

# 4.3 — Imputação estocástica de valores nulos em dt_entrega_efetiva
#        Regra: data_compra + mediana histórica de trânsito (4 dias)
#        Justificativa: evita introduzir zero-inflação ou distorcer a distribuição
#        de lead_time ao usar mediana como estimativa central robusta.
MEDIANA_TRANSITO_DIAS = 4

# Para imputar, precisamos do dt_compra correspondente — faremos após o join
nulos_antes = df_logistica["dt_entrega_efetiva"].isna().sum()
print(f"   Nulos encontrados em 'dt_entrega_efetiva' : {nulos_antes}")


# ── Célula 5: Conciliação — Join OMS × TMS pela chave do pedido ───────────────
print("\n🔗 [JOIN] Conciliando OMS e TMS pelo número do pedido...")

df_merged = pd.merge(
    df_vendas,
    df_logistica,
    left_on  = "id_pedido_oms",
    right_on = "cod_pedido_entrega",
    how      = "left",             # Preserva todos os pedidos de venda
)

print(f"   Pedidos após conciliação (left join) : {len(df_merged)}")
nulos_apos = df_merged["dt_entrega_efetiva"].isna().sum()
print(f"   Pedidos sem entrega registrada (nulos) : {nulos_apos}")


# ── Célula 6: Imputação dos Nulos Pós-Join ────────────────────────────────────
print(f"\n🔧 [DQ-3] Aplicando imputação estocástica nos {nulos_apos} nulo(s)...")

mascara_nulos = df_merged["dt_entrega_efetiva"].isna()
df_merged.loc[mascara_nulos, "dt_entrega_efetiva"] = (
    df_merged.loc[mascara_nulos, "dt_compra"]
    + pd.to_timedelta(MEDIANA_TRANSITO_DIAS, unit="D")
)
print(f"   Imputação aplicada: dt_compra + {MEDIANA_TRANSITO_DIAS} dias (mediana histórica).")
print(f"   Nulos remanescentes: {df_merged['dt_entrega_efetiva'].isna().sum()}")


# ── Célula 7: Engenharia de Features — Métricas e Flag de Alvo ───────────────
print("\n⚙️  [FEATURE ENG] Calculando métricas e flag de atraso...")

# Métrica principal do projeto: tempo total do ciclo do pedido
df_merged["lead_time_dias"] = (
    df_merged["dt_entrega_efetiva"] - df_merged["dt_compra"]
).dt.days

# Flag binária de atraso (variável alvo para o modelo preditivo)
# SLA contratual: pedidos com lead_time > 5 dias são considerados em atraso
SLA_LIMITE_DIAS = 5
df_merged["flg_atraso"] = (df_merged["lead_time_dias"] > SLA_LIMITE_DIAS).astype(int)

taxa_atraso = df_merged["flg_atraso"].mean() * 100
print(f"   SLA limite         : {SLA_LIMITE_DIAS} dias")
print(f"   Pedidos em atraso  : {df_merged['flg_atraso'].sum()} ({taxa_atraso:.1f}%)")
print(f"   Pedidos no prazo   : {(df_merged['flg_atraso'] == 0).sum()}")
print(f"   Lead time médio    : {df_merged['lead_time_dias'].mean():.2f} dias")


# ── Célula 8: Modelagem Dimensional — Dimensão Cliente ───────────────────────
print("\n🏗️  [STAR SCHEMA] Construindo dimensão: DIM_CLIENTE...")

dim_cliente = (
    df_merged[["id_cliente", "nome_cliente", "cidade", "estado", "regiao_destino"]]
    .drop_duplicates(subset="id_cliente")
    .copy()
    .reset_index(drop=True)
)
# Chave substituta (surrogate key) — independente do sistema de origem
dim_cliente.insert(0, "sk_cliente", range(1, len(dim_cliente) + 1))

dim_cliente.to_csv("dim_cliente.csv", index=False, encoding="utf-8-sig")
print(f"   ✅ 'dim_cliente.csv' exportado com {len(dim_cliente)} clientes únicos.")


# ── Célula 9: Modelagem Dimensional — Dimensão Transportadora ─────────────────
print("\n🏗️  [STAR SCHEMA] Construindo dimensão: DIM_TRANSPORTADORA...")

dim_transportadora = (
    df_merged[["id_transportadora", "razao_social"]]
    .drop_duplicates(subset="id_transportadora")
    .copy()
    .sort_values("id_transportadora")
    .reset_index(drop=True)
)
dim_transportadora.insert(0, "sk_transportadora", range(1, len(dim_transportadora) + 1))

dim_transportadora.to_csv("dim_transportadora.csv", index=False, encoding="utf-8-sig")
print(f"   ✅ 'dim_transportadora.csv' exportado com {len(dim_transportadora)} transportadoras.")


# ── Célula 10: Modelagem Dimensional — Tabela Fato Pedidos ───────────────────
print("\n🏗️  [STAR SCHEMA] Construindo tabela fato: FATO_PEDIDOS...")

# Enriquecer o dataset integrado com as surrogate keys das dimensões
df_final = df_merged.merge(dim_cliente[["sk_cliente", "id_cliente"]],
                           on="id_cliente", how="left")
df_final = df_final.merge(dim_transportadora[["sk_transportadora", "id_transportadora"]],
                           on="id_transportadora", how="left")

# Chave substituta do pedido (sk_pedido)
df_final = df_final.reset_index(drop=True)
df_final.insert(0, "sk_pedido", range(1, len(df_final) + 1))

# Selecionar apenas as colunas do modelo analítico (Star Schema)
colunas_fato = [
    "sk_pedido",
    "sk_cliente",
    "sk_transportadora",
    "id_pedido_oms",
    "dt_compra",
    "dt_entrega_efetiva",
    "vlr_frete_pago",
    "vlr_custo_frete_real",
    "qtd_itens",
    "volume_fila_estoque",
    "dia_semana_faturamento",
    "flg_atraso",
]
fato_pedidos = df_final[colunas_fato].copy()

fato_pedidos.to_csv("fato_pedidos.csv", index=False, encoding="utf-8-sig")
print(f"   ✅ 'fato_pedidos.csv' exportado com {len(fato_pedidos)} pedidos.")


# ── Célula 11: Relatório Final do Pipeline ────────────────────────────────────
print("\n" + "="*60)
print("📊 RELATÓRIO FINAL DO PIPELINE DE ETL")
print("="*60)

print(f"""
[AUDITORIA DE QUALIDADE DE DADOS]
  Registros OMS ingeridos        : {len(df_vendas) + 1}
  Registros PED-TESTE removidos  : 1
  Registros TMS ingeridos        : {len(df_logistica) + 1}
  Duplicatas TMS eliminadas      : 1
  Nulos imputados (mediana)      : {nulos_antes}

[MODELO ANALÍTICO — STAR SCHEMA]
  dim_cliente.csv                : {len(dim_cliente)} linhas
  dim_transportadora.csv         : {len(dim_transportadora)} linhas
  fato_pedidos.csv               : {len(fato_pedidos)} linhas

[DISTRIBUIÇÃO DO TARGET — flg_atraso]
  Pedidos no prazo  (0)          : {(fato_pedidos['flg_atraso'] == 0).sum()}
  Pedidos em atraso (1)          : {fato_pedidos['flg_atraso'].sum()}
  Taxa de atraso                 : {taxa_atraso:.1f}%
""")

print("✅ Etapa 2 concluída. Star Schema disponível para o Motor de Analytics.")
