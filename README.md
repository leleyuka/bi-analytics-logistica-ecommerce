# Business Intelligence Aplicado à Otimização Logística e Satisfação do Cliente no Varejo Digital

**Projeto em Business Intelligence e Analytics - Fase 2**  
**Estudante:** Leticia Ayumi Akaichi  
**Instituição:** PUCRS Online - Graduação

---

## 1. Visão Geral

Este repositório implementa a Fase 2 do projeto planejado no arquivo `Overleaf_Fase_1.pdf`. O contexto é uma empresa de varejo digital de médio porte que possui relatórios conflitantes entre Vendas e SAC: o OMS indica pedidos expedidos no prazo, enquanto o SAC registra reclamações de clientes por atraso na entrega física.

A solução proposta integra dados do sistema de vendas (OMS) e do sistema de rastreamento logístico (TMS), aplica rotinas de qualidade de dados, organiza as informações em um modelo dimensional Star Schema e disponibiliza indicadores em um dashboard gerencial offline. Além do BI descritivo, a solução inclui uma camada de Analytics com machine learning para prever risco de estouro de SLA.

---

## 2. Métricas Estratégicas do Negócio

| KPI | Descrição | Meta / Uso Gerencial |
|---|---|---|
| Order Lead Time (OLT) | Tempo total entre `dt_compra` e `dt_entrega_efetiva`. | Meta: até 5 dias. Mede a experiência real do cliente. |
| Taxa de Estouro de SLA | Percentual de pedidos com `flg_atraso = 1`. | Meta: menor que 10%. Mostra a proporção de entregas críticas. |
| Custo Logístico por Pedido (CLP) | Diferença entre `vlr_custo_frete_real` e `vlr_frete_pago`. | Identifica subsídio ou perda por transportadora. |
| Volume de Fila de Estoque Médio (VFE) | Média de `volume_fila_estoque` por dia e transportadora. | Indica gargalo interno de separação. |
| F1-Score do Modelo Preditivo | Equilíbrio entre precisão e recall para a classe "em atraso". | Meta: F1 maior ou igual a 0,80. Avalia a utilidade do alerta preditivo. |

---

## 3. Arquitetura da Solução

O diagrama completo está disponível em:

[architecture_diagram.svg](./architecture_diagram.svg)

Fluxo implementado:

1. **Fontes operacionais:** geração ou coleta de dados do OMS (`dados_vendas_brutos.csv`) e TMS (`dados_logistica_brutos.csv`).
2. **Staging Area:** leitura dos arquivos com Pandas para uma área intermediária de processamento.
3. **Qualidade de Dados e ETL:** remoção de registros de teste, eliminação de duplicidades, conversão de datas e imputação de entregas sem data.
4. **Conciliação:** junção entre OMS e TMS pela chave natural do pedido.
5. **Modelo dimensional:** criação de `dim_cliente`, `dim_transportadora` e `fato_pedidos`.
6. **Analytics:** treinamento de um `RandomForestClassifier` para prever `flg_atraso`.
7. **BI:** dashboard HTML offline com KPIs, filtros, matriz de SLA e visualizações.
8. **Repositório:** documentação, scripts, dashboard e diagrama no GitHub.

---

## 4. Ferramentas e Dependências

| Camada | Ferramenta |
|---|---|
| Linguagem | Python 3.x / Google Colab |
| Preparação e limpeza | Pandas e NumPy |
| Modelagem dimensional | Star Schema com arquivos CSV |
| Machine Learning | Scikit-Learn - RandomForestClassifier |
| Visualização auxiliar | Matplotlib e Seaborn |
| Dashboard de BI | HTML, CSS e JavaScript puro |
| Publicação | GitHub / GitHub Pages opcional |

O dashboard entregue não depende de banco de dados, API, Looker Studio, Power BI, servidor local, CDN ou conexão externa.

---

## 5. Estrutura do Repositório

```text
.
├── README.md
├── Overleaf_Fase_1.pdf
├── architecture_diagram.svg
├── dashboard.html
├── prep_dashboard_data.py
├── 01_geracao_dados_brutos.py
├── 02_pipeline_etl_star_schema.py
├── 03_motor_analytics_ml.py
├── fase2_projeto_BI_relatorio.docx
└── apresentacao_executiva_fase2.pptx
```

---

## 6. Como Executar no Google Colab

1. Execute `01_geracao_dados_brutos.py` para gerar as bases simuladas do OMS e TMS.
2. Execute `02_pipeline_etl_star_schema.py` para aplicar qualidade de dados, conciliar as fontes e gerar o Star Schema.
3. Execute `03_motor_analytics_ml.py` para treinar e avaliar o modelo preditivo.
4. Abra `dashboard.html` diretamente no navegador para consultar o dashboard estático.

O arquivo `prep_dashboard_data.py` é opcional. Ele serve apenas para recalcular agregações do dashboard caso os CSVs sejam regenerados.

---

## 7. Modelo Dimensional

### Tabela Fato - `fato_pedidos`

| Campo | Descrição |
|---|---|
| `sk_pedido` | Chave substituta do pedido. |
| `sk_cliente` | Chave estrangeira para `dim_cliente`. |
| `sk_transportadora` | Chave estrangeira para `dim_transportadora`. |
| `id_pedido_oms` | Identificador original do pedido. |
| `dt_compra` | Data da compra. |
| `dt_entrega_efetiva` | Data real ou imputada da entrega. |
| `lead_time_dias` | Diferença em dias entre compra e entrega. |
| `vlr_frete_pago` | Frete pago pelo cliente. |
| `vlr_custo_frete_real` | Custo real pago à transportadora. |
| `qtd_itens` | Quantidade de itens do pedido. |
| `volume_fila_estoque` | Volume da fila de separação no estoque. |
| `dia_semana_faturamento` | Dia da semana do faturamento. |
| `flg_atraso` | Flag de atraso: 1 quando o lead time é maior que 5 dias. |

### Dimensões

`dim_cliente`: cliente, cidade, estado e região de destino.  
`dim_transportadora`: código e razão social da transportadora.

---

## 8. Solução de BI

O dashboard [dashboard.html](./dashboard.html) apresenta:

- KPIs principais: OLT médio, taxa de estouro de SLA, CLP, F1-Score e VFE.
- Matriz de SLA por transportadora e região.
- Distribuição de pedidos no prazo versus em atraso.
- Volumetria de atrasos por transportadora.
- Evolução mensal da taxa de estouro de SLA.
- Importância das variáveis do modelo preditivo.
- Filtros por transportadora e região.

A matriz evidencia que a **EntregaMax Transportes ME** concentra atrasos estruturais nas regiões **Norte** e **Nordeste**, com lead time médio acima do SLA de 5 dias. Esse resultado confirma a hipótese da Fase 1 de que a divergência entre Vendas e SAC ocorre porque o OMS considera o pedido expedido, enquanto o cliente considera a entrega física final.

---

## 9. Solução de Analytics

O script `03_motor_analytics_ml.py` treina um modelo Random Forest para prever se um pedido irá estourar o SLA.

| Item | Configuração |
|---|---|
| Algoritmo | RandomForestClassifier |
| Variável alvo | `flg_atraso` |
| Variáveis explicativas | `sk_transportadora`, `dia_semana_faturamento`, `volume_fila_estoque` |
| Divisão dos dados | 70% treino e 30% teste, com estratificação |
| Métricas | Acurácia, matriz de confusão, precision, recall, F1-Score e importância das variáveis |

A camada de Analytics amplia o BI porque não apenas explica atrasos passados, mas também permite antecipar pedidos com maior risco de atraso antes da expedição.

---

## 10. Resultados e Recomendações

As análises indicam três ações prioritárias para a diretoria:

1. Renegociar SLA ou redistribuir rotas da EntregaMax nas regiões Norte e Nordeste.
2. Usar a previsão de atraso para acionar comunicação proativa com clientes e SAC.
3. Monitorar a fila de estoque para separar gargalos internos de problemas de transporte terceirizado.

Com a integração OMS + TMS, a empresa passa a trabalhar com uma única versão da verdade, reduzindo divergências entre áreas e apoiando decisões de investimento em logística.

---

## 11. Referências

KIMBALL, R.; ROSS, M. *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*. 3rd ed. New York: John Wiley & Sons, 2013.

INMON, W. H. *Building the Data Warehouse*. 4th ed. New York: John Wiley & Sons, 2005.

---

## Repositório

**GitHub:** [leleyuka/bi-analytics-logistica-ecommerce](https://github.com/leleyuka/bi-analytics-logistica-ecommerce)
