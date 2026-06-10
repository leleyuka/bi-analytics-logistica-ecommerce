# bi-analytics-logistica-ecommerce

Dicionário de Dados do Data Mart (Modelagem Star Schema)
Para garantir a governança e o entendimento das regras de negócio, a estrutura do repositório analítico dimensional foi mapeada conforme o dicionário abaixo:

Tabela Fato: Fato_Pedidos
sk_pedido (INT - Chave Primária/Surrogate Key): Identificador único do ciclo do pedido no ambiente analítico.

nk_pedido (VARCHAR - Natural Key): Número original do pedido gerado pelo sistema de vendas (OMS).

fk_cliente (INT - Chave Estrangeira): Relacionamento com a tabela Dim_Cliente.

fk_transportadora (INT - Chave Estrangeira): Relacionamento com a tabela Dim_Transportadora.

fk_tempo_aprovacao (INT - Chave Estrangeira): Data de aprovação do pagamento (Dim_Tempo).

fk_tempo_entrega (INT - Chave Estrangeira): Data da entrega física efetiva (Dim_Tempo).

vlr_frete_pago (DECIMAL): Valor do frete cobrado do cliente.

vlr_frete_custo (DECIMAL): Valor real do frete faturado pela transportadora.

flg_atraso (BIT/INT): Indicador binário de atraso (0 = No Prazo, 1 = Atrasado).

qtd_itens (INT): Quantidade de produtos no pedido.

Tabelas Dimensão:
Dim_Cliente: sk_cliente (PK), nk_id_cliente, nm_cliente, cidade_destino, estado_destino, regiao.

Dim_Transportadora: sk_transportadora (PK), nk_id_transportadora, razao_social, modalidade_frete (Expresso/Econômico).

Dim_Tempo: sk_tempo (PK/INT AAAAMMDD), dt_completa, num_ano, num_mes, nm_mes, num_trimestre, flg_dia_util.

3.2 Estrutura do Código-Fonte e Documentação no GitHub
O código-fonte da solução foi construído em Python (Jupyter Notebooks) e estruturado no GitHub sob o seguinte índice de arquivos de engenharia de dados:

1. Arquivo: notebooks/1_ingestao_e_limpeza_dados.ipynb
Finalidade: Realiza a extração dos dados brutos armazenados na Staging Area. O script efetua o tratamento de valores nulos nas datas de rastreamento através de técnicas de imputação baseadas na média histórica de trânsito da rota.

Processamento executado: Eliminação de registros de testes internos, conversão de fusos horários padronizados para o horário de Brasília, remoção de duplicidades de registros XML de transporte e carga final nas tabelas Dimensão e Fato utilizando a biblioteca pandas e conexões otimizadas via SQLAlchemy.

2. Arquivo: notebooks/2_analise_preditiva_analytics.ipynb
Finalidade: Engine de Machine Learning e Advanced Analytics exigida no escopo da Fase 2.

Algoritmo utilizado: Implementação do modelo de classificação Random Forest Classifier utilizando a biblioteca scikit-learn.

Objetivo do Modelo: Prever se um novo pedido sofrerá atraso (Target: flg_atraso = 1) no momento em que ele é faturado, utilizando como variáveis preditivas (features): a transportadora selecionada, a região macro do destino, o dia da semana do faturamento e a volumetria total de pedidos pendentes na fila do estoque operacional.

Métricas de Avaliação do Modelo: Mapeamento detalhado dos resultados apresentando a Matriz de Confusão, acurácia, precisão, recall e a curva ROC/AUC para mitigar falsos negativos.
