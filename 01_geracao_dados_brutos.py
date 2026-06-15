# =============================================================================
# FASE 2 - PROJETO BI & ANALYTICS | PUCRS Online
# Estudante: Leticia Ayumi Akaichi
# Script 01: Geração de Bases de Dados Brutos Simulados
# Descrição: Gera dois arquivos CSV simulando fontes heterogêneas de dados —
#            o sistema de vendas (OMS) e o sistema de rastreamento logístico (TMS).
#            Inclui anomalias intencionais para validação do pipeline de ETL.
# =============================================================================

# ── Célula 1: Instalação e Importações ───────────────────────────────────────
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Semente global para reprodutibilidade dos experimentos
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

print("✅ Bibliotecas carregadas com sucesso.")
print(f"   Pandas  : {pd.__version__}")
print(f"   NumPy   : {np.__version__}")


# ── Célula 2: Parâmetros Globais de Simulação ─────────────────────────────────
N_REGISTROS     = 1000          # Volume de registros para treino do modelo
DATA_INICIO     = datetime(2024, 1, 1)
DATA_FIM        = datetime(2024, 12, 31)

# Transportadoras (id 0, 1, 2)
TRANSPORTADORAS = {
    0: "TransRapido Logistica Ltda",
    1: "Carrier Brasil S.A.",
    2: "EntregaMax Transportes ME",   # Transportadora com atraso estrutural
}

# Regiões de destino codificadas (0=Sul, 1=Sudeste, 2=Norte, 3=Nordeste)
REGIOES = [0, 1, 2, 3]

print("✅ Parâmetros de simulação configurados.")


# ── Célula 3: Funções Auxiliares ──────────────────────────────────────────────
def gerar_data_aleatoria(inicio: datetime, fim: datetime) -> datetime:
    """Retorna um datetime aleatório dentro do intervalo [inicio, fim]."""
    delta = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, delta))


def calcular_lead_time(id_transportadora: int, regiao: int, dt_compra: datetime) -> datetime:
    """
    Calcula a data de entrega efetiva simulando atrasos estruturais.
    Regra de negócio:
      - Transportadora 2 em regiões >= 2: lead_time entre 6 e 12 dias (ATRASO)
      - Demais combinações: lead_time entre 1 e 5 dias (DENTRO DO SLA)
    """
    if id_transportadora == 2 and regiao >= 2:
        dias_transito = random.randint(6, 12)   # Atraso intencional > 5 dias
    else:
        dias_transito = random.randint(1, 5)    # Dentro do SLA contratual
    return dt_compra + timedelta(days=dias_transito)


print("✅ Funções auxiliares definidas.")


# ── Célula 4: Geração de dados_vendas_brutos.csv ─────────────────────────────
print("\n📦 Gerando base de vendas (OMS)...")

ids_pedido     = [f"PED-{str(i).zfill(5)}" for i in range(1, N_REGISTROS + 1)]
ids_cliente    = [f"CLI-{random.randint(1000, 9999)}" for _ in range(N_REGISTROS)]
nomes_cliente  = [f"Cliente_{i}" for i in range(N_REGISTROS)]

cidades_estados = [
    ("Porto Alegre", "RS"), ("São Paulo", "SP"), ("Curitiba", "PR"),
    ("Salvador", "BA"), ("Fortaleza", "CE"), ("Manaus", "AM"),
    ("Belém", "PA"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Recife", "PE"),
]
localidades = [random.choice(cidades_estados) for _ in range(N_REGISTROS)]
cidades      = [loc[0] for loc in localidades]
estados      = [loc[1] for loc in localidades]

# Mapeamento estado → região de destino
mapa_regiao = {
    "RS": 0, "PR": 0, "SC": 0,                          # Sul
    "SP": 1, "RJ": 1, "MG": 1, "ES": 1,                 # Sudeste
    "AM": 2, "PA": 2, "RO": 2, "AC": 2, "RR": 2,        # Norte
    "BA": 3, "CE": 3, "PE": 3, "MA": 3, "PI": 3,        # Nordeste
}
regioes_destino = [mapa_regiao.get(e, random.randint(0, 3)) for e in estados]

ids_transportadora      = [random.choice([0, 1, 2]) for _ in range(N_REGISTROS)]
datas_compra            = [gerar_data_aleatoria(DATA_INICIO, DATA_FIM) for _ in range(N_REGISTROS)]
vlr_frete_pago          = np.round(np.random.uniform(8.0, 55.0, N_REGISTROS), 2)
qtd_itens               = np.random.randint(1, 10, N_REGISTROS)
volume_fila_estoque     = np.random.randint(0, 500, N_REGISTROS)
dia_semana_faturamento  = [d.weekday() for d in datas_compra]   # 0=Seg ... 6=Dom

df_vendas = pd.DataFrame({
    "id_pedido_oms":           ids_pedido,
    "id_cliente":              ids_cliente,
    "nome_cliente":            nomes_cliente,
    "cidade":                  cidades,
    "estado":                  estados,
    "regiao_destino":          regioes_destino,
    "id_transportadora":       ids_transportadora,
    "dt_compra":               datas_compra,
    "vlr_frete_pago":          vlr_frete_pago,
    "qtd_itens":               qtd_itens,
    "volume_fila_estoque":     volume_fila_estoque,
    "dia_semana_faturamento":  dia_semana_faturamento,
})

# ── Anomalia Intencional: Registro de teste para ser removido no ETL ──────────
registro_teste = {
    "id_pedido_oms":          "PED-TESTE",
    "id_cliente":             "CLI-0000",
    "nome_cliente":           "USUARIO TESTE QA",
    "cidade":                 "N/A",
    "estado":                 "N/A",
    "regiao_destino":         -1,
    "id_transportadora":      -1,
    "dt_compra":              datetime(2000, 1, 1),
    "vlr_frete_pago":         0.0,
    "qtd_itens":              0,
    "volume_fila_estoque":    0,
    "dia_semana_faturamento": 0,
}
df_vendas = pd.concat(
    [df_vendas, pd.DataFrame([registro_teste])], ignore_index=True
)

df_vendas.to_csv("dados_vendas_brutos.csv", index=False, encoding="utf-8-sig")
print(f"   ✅ 'dados_vendas_brutos.csv' gerado com {len(df_vendas)} registros "
      f"(incluindo 1 registro PED-TESTE).")


# ── Célula 5: Geração de dados_logistica_brutos.csv ──────────────────────────
print("\n🚛 Gerando base de logística (TMS)...")

# Gera a data de entrega para cada pedido com base nas regras de atraso
datas_entrega = [
    calcular_lead_time(
        df_vendas.loc[i, "id_transportadora"],
        df_vendas.loc[i, "regiao_destino"],
        df_vendas.loc[i, "dt_compra"],
    )
    for i in range(N_REGISTROS)      # Exclui o registro PED-TESTE (índice 1000)
]

# Custo real de frete pago pela empresa à transportadora
vlr_custo_frete_real = np.round(np.random.uniform(5.0, 45.0, N_REGISTROS), 2)

# Razão social associada ao id da transportadora de cada pedido
razoes_sociais = [
    TRANSPORTADORAS[df_vendas.loc[i, "id_transportadora"]]
    for i in range(N_REGISTROS)
]

df_logistica = pd.DataFrame({
    "cod_pedido_entrega":    ids_pedido,          # Chave de conciliação com OMS
    "razao_social":          razoes_sociais,
    "dt_entrega_efetiva":   datas_entrega,
    "vlr_custo_frete_real":  vlr_custo_frete_real,
})

# ── Anomalia 1: Inserir 2 valores nulos em dt_entrega_efetiva ────────────────
indices_nulos = random.sample(range(len(df_logistica)), 2)
df_logistica.loc[indices_nulos, "dt_entrega_efetiva"] = np.nan
print(f"   ⚠️  Valores nulos inseridos nos índices: {indices_nulos}")

# ── Anomalia 2: Inserir 1 registro duplicado ─────────────────────────────────
idx_duplicata = random.randint(10, 50)
linha_duplicada = df_logistica.iloc[idx_duplicata].copy()
df_logistica = pd.concat(
    [df_logistica, pd.DataFrame([linha_duplicada])], ignore_index=True
)
print(f"   ⚠️  Registro duplicado inserido (índice original: {idx_duplicata}). "
      f"Pedido: {linha_duplicada['cod_pedido_entrega']}")

# Embaralha para que a duplicata não fique óbvia no final do arquivo
df_logistica = df_logistica.sample(frac=1, random_state=SEED).reset_index(drop=True)

df_logistica.to_csv("dados_logistica_brutos.csv", index=False, encoding="utf-8-sig")
print(f"   ✅ 'dados_logistica_brutos.csv' gerado com {len(df_logistica)} registros "
      f"(2 nulos + 1 duplicata incluídos).")


# ── Célula 6: Resumo da Geração ───────────────────────────────────────────────
print("\n" + "="*60)
print("📊 RESUMO DA GERAÇÃO DE DADOS BRUTOS")
print("="*60)
print(f"\n[dados_vendas_brutos.csv]")
print(f"  Registros totais  : {len(df_vendas)}")
print(f"  Colunas           : {list(df_vendas.columns)}")
print(f"  Anomalia inserida : 1 registro 'PED-TESTE'\n")
print(f"[dados_logistica_brutos.csv]")
print(f"  Registros totais  : {len(df_logistica)}")
print(f"  Colunas           : {list(df_logistica.columns)}")
print(f"  Anomalias inseridas: 2 nulos em 'dt_entrega_efetiva', 1 linha duplicada")
print("\n✅ Etapa 1 concluída. Arquivos prontos para o pipeline de ETL.")
