## Relatório Técnico: Engenharia de Dados Climáticos (Capitais do Brasil)
Esse projeto foi desenvolvido com o objetivo de exercitar habilidades técnicas de orquestração de dados e infraestrura como código e evoluiu  para auditoria técnica da análise climática histórica das 27 capitais brasileiras. O objetivo central foi sair de uma coleta simples e pontual para um sistema capaz de processar volumes massivos de dados com milhares de registros por execução de forma automatizada com o objetivo de atingir integridade e facilidade de consumo visual. 

### O que o projeto faz?
Através de uma pipeline ETL, é efetuada uma extração de dados em massa da API da Open-Meteo contendo diversos dados climaticos. A definição do escopo foi extrair os dados climáticos de todas as capitais brasileiras de hora em hora durante o verão de 2025/2026 para tornar possível uma comparação direta entre as capitais e identificar diferenças de fluxos e comparar o desenvolvimento de temperatura durante a estação.
Deste modo, desenvolvi um Python notebook para fazer todo o processo de ETL de ponta a ponta, extraindo da API, fazendo todas as transformações necessárias para normalizar os dados e ingerindo na database, possibilitando o consumo pelo dashboard com o streamlit.

 ## Arquitetura e Capacidade Técnica
A solução foi desenhada para ser totalmente reprodutível e isolada, utilizando as melhores práticas de mercado:

Infraestrutura como Código (IaC): Uso de Terraform e Docker para provisionar volumes e redes, garantindo que o ambiente seja idêntico em qualquer máquina utilizando a conteinerização de código para formar uma bloco único.

Orquestração de Ponta a Ponta: Apache Airflow gerenciando o pipeline, com suporte a parâmetros dinâmicos para "viagens no tempo" (coleta de qualquer período histórico).

Armazenamento de Alta Performance: Utilização de Parquet como camada intermediária para atingir eficiência de compressão, e PostgreSQL 18 como a base de dados final, operando com inserções em lotes para suportar grandes volumes sem gargalos de memória devido a extração em massa de dezenas/centenas de milhares de registros em um curto intervalo de tempo.

Interface Analítica: Dashboard em Streamlit otimizado com cache de dados para facilitar o processo de consulta dos dados em um dashboard automatizado.

## Decisões Críticas e Evolução
O projeto passou por pontos de desenvolvimento estratégicos que definiram sua maturidade atual:

1. Escalabilidade de Dados: OpenWeather vs. Open-Meteo
A decisão mais impactante foi a migração da API OpenWeather para a Open-Meteo já que inicialmente utilizei a API da OpenWeather que limitava a coleta de dados histórica e exigia uma chave de API que restringia a quantidade de requisições com limites baixos que não permitiam uma coleta massiva de informações. Por conta dessa barreira decidi alternar para a API da Open-Meteo que permite uma extração massiva de hora em hora de anos inteiros em uma única chamada de rede, sem custo e com maior precisão.

2. Refinamento de Granularidade (Data/Hora)
Diferente de modelos simples que salvam apenas o timestamp, optei por separar logicamente Data e Horário no banco de dados para facilitar a consulta aos dados e poder realizar comparativos de hora em hora para cada cidade. Isso permite análises granulares no Dashboard (ex: comparar temperaturas apenas ao meio-dia entre duas cidades), facilitando a geração de insights sem processamento pesado.

3. Modo de Segurança (Dry Run)
Implementei uma mecânica de Dry Run via Airflow Params, que permite testar a integridade de novas extrações históricas (como verões de 10 anos atrás) sem o risco de corromper ou duplicar dados no banco de dados de produção antes da validação final.

## Capacidades e Insights Gerados
Atualmente, o sistema entrega uma visão analítica profunda do clima urbano brasileiro, analisando os extremos ao Identificar recordes de temperatura e picos de precipitação acumulada em todo o território nacional. O visual tem a capacidade de confrontar o comportamento térmico e pluviométrico de duas capitais simultaneamente (ex: o contraste entre a seca de Boa Vista e a chuva de Curitiba no mesmo período).

Consumo de Dados Otimizado: O dashboard processa mais de 50.000 registros de forma fluida, oferecendo métricas de tendência (médias) e picos diários de calor/frio.

## Stack Tecnológica
Linguagem: Python (Pandas, SQLAlchemy)
Infraestrutura: Docker, Terraform
Orquestração: Apache Airflow
Banco de Dados: PostgreSQL 18
Visualização: Streamlit, Plotly
Qualidade: Pytest (Mocks para isolamento total)

Desenvolvido por: Vitor Hugo Ferreira Sousa
