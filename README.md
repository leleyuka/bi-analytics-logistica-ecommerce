# Business Intelligence Aplicado à Otimização Logística e Satisfação do Cliente no Varejo Digital (E-commerce)

**Projeto em Business Intelligence e Analytics — Fase 2**
**Estudante:** Leticia Ayumi Akaichi
**Instituição:** PUCRS Online — Graduação

---

## 1. Visão Geral do Projeto

Este repositório contém a implementação prática da Fase 2 do projeto de BI & Analytics, cujo objetivo é **unificar os dados do sistema de vendas (OMS)** e do **sistema de rastreamento das transportadoras (TMS)** em um modelo analítico confiável (Star Schema), capaz de:

- Eliminar relatórios conflitantes entre os setores de Vendas e SAC (atendimento ao cliente);
- Auditar e calcular o indicador **Order Lead Time** (tempo total do ciclo do pedido);
- Identificar **estouros de SLA** (entregas com lead time superior a 5 dias);
- Treinar um modelo preditivo (**Random Forest**) para antecipar o risco de atraso logístico antes da expedição.

A solução segue o ciclo de vida de projetos de BI proposto por Ralph Kimball (modelagem dimensional / Star Schema), com etapas claras de ETL, Data Quality, modelagem dimensional e Analytics (Machine Learning).

---

## 2. Arquitetura da Solução

```
┌──────────────────────┐     ┌──────────────────────────┐
│  dados_vendas_brutos  │     │  dados_logistica_brutos   │
│   (OMS - Sistema de   │     │  (TMS - Rastreamento das  │
│        Vendas)        │     │      Transportadoras)     │
└──────────┬────────────┘     └────────────┬──────────────┘
           │                                │
           └───────────────┬────────────────┘
                            ▼
                  ┌────────────────────┐
                  │   STAGING AREA      │
                  │  (Pandas DataFrame) │
                  └─────────┬───────────┘
                             ▼
                  ┌────────────────────────────┐
                  │   DATA QUALITY / ETL        │
                  │  - Remoção de PED-TESTE     │
                  │  - Deduplicação (keep=last) │
                  │  - Conversão de datas       │
                  │  - Imputação estocástica    │
                  │    de nulos (+4 dias)       │
                  │  - Cálculo de lead_time_dias│
                  │  - Flag flg_atraso (SLA>5d) │
                  └─────────┬────────────────────┘
                             ▼
              ┌──────────────────────────────────┐
              │   MODELO DIMENSIONAL (STAR SCHEMA)│
              │                                    │
              │   dim_cliente   dim_transportadora │
              │        \             /             │
              │         \           /              │
              │        fato_pedidos                │
              └─────────────────┬──────────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │   ANALYTICS (MACHINE LEARNING) │
                  │   RandomForestClassifier       │
                  │   Predição de flg_atraso       │
                  │   (estouro de SLA)              │
                  └─────────────┬──────────────────┘
                                 ▼
                  ┌──────────────────────────────┐
                  │  DASHBOARD GERENCIAL (BI)      │
                  │  Google Looker Studio          │
                  └────────────────────────────────┘
```

---

## 3. Ferramentas e Plataformas

| Camada | Ferramenta |
|---|---|
| Linguagem | Python 3.x (Google Colab) |
| ETL e Modelagem Dimensional | Pandas, NumPy |
| Machine Learning | Scikit-Learn (RandomForestClassifier) |
| Visualização de resultados do modelo | Matplotlib, Seaborn |
| Dashboard de BI (gerencial) | Google Looker Studio |
| Repositório de dados | Arquivos CSV locais |

---

## 4. Estrutura do Repositório

```
.
├── README.md                          # Este arquivo
├── 01_geracao_dados_brutos.py         # Geração das bases simuladas OMS e TMS
├── 02_pipeline_etl_star_schema.py     # Pipeline de ETL, Data Quality e Star Schema
├── 03_motor_analytics_ml.py           # Motor de Analytics (Random Forest)
├── docs/
│   ├── fase2_projeto_BI_relatorio.docx
│   └── apresentacao_executiva_fase2.pptx
└── data/
    ├── dados_vendas_brutos.csv         # gerado pelo script 01
    ├── dados_logistica_brutos.csv      # gerado pelo script 01
    ├── dim_cliente.csv                 # gerado pelo script 02
    ├── dim_transportadora.csv          # gerado pelo script 02
    ├── fato_pedidos.csv                # gerado pelo script 02
    └── analytics_model_results.png     # gerado pelo script 03
```

> Os arquivos CSV e o gráfico de resultados **não estão versionados previamente** — eles são gerados ao executar os scripts na ordem abaixo.

---

## 5. Como Executar (Google Colab)

A execução deve seguir **estritamente a ordem abaixo**, pois cada script depende dos artefatos gerados pelo anterior.

### Passo 1 — Gerar as bases de dados brutos
Abra e execute `01_geracao_dados_brutos.py` no Google Colab.

Saída gerada:
- `dados_vendas_brutos.csv` (1.001 registros, incluindo 1 registro `PED-TESTE` intencional)
- `dados_logistica_brutos.csv` (1.001 registros, incluindo 2 valores nulos e 1 duplicata intencionais)

### Passo 2 — Executar o pipeline de ETL e Modelagem Dimensional
Faça upload dos dois arquivos gerados no Passo 1 para o ambiente do Colab (ou utilize a mesma sessão) e execute `02_pipeline_etl_star_schema.py`.

Saída gerada:
- `dim_cliente.csv`
- `dim_transportadora.csv`
- `fato_pedidos.csv`

O script imprime um relatório de auditoria de qualidade de dados (registros removidos, duplicatas eliminadas, nulos imputados) e a distribuição da variável alvo `flg_atraso`.

### Passo 3 — Treinar e avaliar o modelo preditivo
Faça upload de `fato_pedidos.csv` (gerado no Passo 2) e execute `03_motor_analytics_ml.py`.

Saída gerada:
- Métricas no console: Acurácia Global, Matriz de Confusão, Classification Report (Precision/Recall/F1-Score)
- Ranking de importância das variáveis (`feature_importances_`)
- `analytics_model_results.png` — gráfico com a matriz de confusão e a importância das variáveis

---

## 6. Modelo Dimensional (Star Schema)

### Tabela Fato — `fato_pedidos`
| Coluna | Descrição |
|---|---|
| `sk_pedido` | Chave substituta do pedido (PK) |
| `sk_cliente` | Chave substituta do cliente (FK → dim_cliente) |
| `sk_transportadora` | Chave substituta da transportadora (FK → dim_transportadora) |
| `id_pedido_oms` | Identificador original do pedido no sistema de vendas |
| `dt_compra` | Data da compra |
| `dt_entrega_efetiva` | Data da entrega efetiva (real ou imputada) |
| `vlr_frete_pago` | Valor de frete pago pelo cliente |
| `vlr_custo_frete_real` | Custo real de frete pago pela empresa à transportadora |
| `qtd_itens` | Quantidade de itens do pedido |
| `volume_fila_estoque` | Volume da fila de separação no estoque no momento da compra |
| `dia_semana_faturamento` | Dia da semana do faturamento (0 = segunda ... 6 = domingo) |
| `flg_atraso` | Flag binária — 1 se `lead_time_dias > 5`, senão 0 |

### Dimensão — `dim_cliente`
`sk_cliente` (PK), `id_cliente`, `nome_cliente`, `cidade`, `estado`, `regiao_destino` (0=Sul, 1=Sudeste, 2=Norte, 3=Nordeste)

### Dimensão — `dim_transportadora`
`sk_transportadora` (PK), `id_transportadora`, `razao_social`

---

## 7. KPIs do Negócio

- **Order Lead Time (OLT)** — tempo total entre `dt_compra` e `dt_entrega_efetiva`. Meta: ≤ 5 dias.
- **Taxa de Estouro de SLA** — percentual de pedidos com `flg_atraso = 1`. Meta: < 10%.
- **Custo Logístico por Pedido (CLP)** — diferença entre `vlr_custo_frete_real` e `vlr_frete_pago`, por transportadora.
- **Precisão Preditiva do Modelo (F1-Score, classe "Em Atraso")** — meta: F1 ≥ 0,80.
- **Volume de Fila de Estoque Médio (VFE)** — média de `volume_fila_estoque` por dia da semana e transportadora.

---

## 8. Modelo Preditivo (Analytics)

- **Algoritmo:** `RandomForestClassifier` (Scikit-Learn), 100 árvores, `random_state=42`
- **Variáveis explicativas (X):** `sk_transportadora`, `dia_semana_faturamento`, `volume_fila_estoque`
- **Variável alvo (y):** `flg_atraso`
- **Divisão:** 70% treino / 30% teste, estratificada
- **Avaliação:** Acurácia global, Matriz de Confusão, Classification Report e ranking de `feature_importances_`

Resultados detalhados (valores numéricos da acurácia, matriz de confusão e importâncias) constam na seção de Resultados do relatório (`docs/fase2_projeto_BI_relatorio.docx`) e na apresentação executiva (`docs/apresentacao_executiva_fase2.pptx`), populados a partir da execução do script `03_motor_analytics_ml.py`.

---

## 9. Dashboard de BI

O dashboard gerencial foi publicado no **Google Looker Studio**, com fonte de dados conectada ao arquivo `fato_pedidos.csv` exportado pelo pipeline de ETL. Ele apresenta:

- Lead time médio por região e transportadora;
- Taxa de estouro de SLA por período;
- Volumetria de atrasos por parceiro logístico;
- Comparativo entre custo de frete pago e custo real (CLP).

> Link do dashboard: *adicionar aqui o link público de visualização do Looker Studio.*

---

## 10. Documentação Adicional

- `docs/fase2_projeto_BI_relatorio.docx` — Relatório completo da Fase 2 (KPIs, arquitetura, solução de BI/Analytics)
- `docs/apresentacao_executiva_fase2.pptx` — Apresentação executiva (storytelling) com os principais resultados e recomendações

---

## 11. Referências

- KIMBALL, R.; ROSS, M. *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. 3rd ed. New York: John Wiley & Sons, 2013.
- INMON, W. H. *Building the Data Warehouse*. 4th ed. New York: John Wiley & Sons, 2005.
