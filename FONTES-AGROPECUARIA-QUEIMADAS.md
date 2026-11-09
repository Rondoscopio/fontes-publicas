# Fontes de dados agrícolas, econômicos e de queimadas em Rondônia

Este índice registra apenas as **fontes originais de dados e relatórios** utilizadas em análises sobre lavouras, soja, milho e focos de calor em Rondônia. Não inclui projetos derivados, dashboards, códigos ou cópias de dados. Fontes já cadastradas são apontadas para suas fichas preexistentes, sem duplicação.

| Fonte original | Endereço | Dados utilizados ou citados | Ficha existente |
| --- | --- | --- | --- |
| IBGE — SIDRA / PAM (lavouras temporárias e permanentes) | [Acessar fonte](https://sidra.ibge.gov.br/) | Produção, área, valor e rendimento agrícola por município; tabelas 1612 e 1613. | [Catálogo](federais/ibge-sidra.json) |
| IBGE — Malhas Territoriais | [Acessar fonte](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/) | Limites e geometrias municipais usados em mapas. | [Catálogo](federais/ibge-malhas-territoriais.json) |
| Banco Central — SGS (séries econômicas) | [Acessar fonte](https://www3.bcb.gov.br/sgspub/) | Séries 1 (câmbio utilizado no projeto) e 7456 (índice de fertilizantes); conferir metadados e metodologia de cada série. | — |
| Banco Central — API BCData/SGS | [Acessar fonte](https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json) | Consulta à série de câmbio pelo serviço oficial, sujeita a limites de intervalo. | — |
| CONAB — Custos de Produção | [Acessar fonte](https://www.conab.gov.br/info-agro/custos-de-producao) | Custos agropecuários e séries conforme produto, safra e região. | — |
| CONAB — Portal de Informações | [Acessar fonte](https://portaldeinformacoes.conab.gov.br/) | Custos, safras, preços agropecuários e relatórios de produção. | — |
| INPE — BDQueimadas | [Acessar fonte](https://data.inpe.br/queimadas/bdqueimadas/) | Focos de calor com recortes por satélite, município e período. | [Catálogo](federais/inpe-bdqueimadas-mapa-e-acervo.json) |
| INPE — Dados Abertos de Queimadas | [Acessar fonte](https://data.inpe.br/queimadas/portal/pages/secao_downloads/dados-abertos/) | Arquivos de focos de calor, séries e geodados. | [Catálogo](federais/inpe-programa-queimadas-dados-abertos.json) |
| USDA/FAS — GAIN e relatórios agrícolas | [Acessar fonte](https://www.fas.usda.gov/data) | Relatórios setoriais usados como referência de comércio e logística agrícola. | — |
| USDA/FAS — PSD Online | [Acessar fonte](https://apps.fas.usda.gov/psdonline/app/index.html) | Estatísticas internacionais de produção e comércio agrícola. | — |
| CEPEA/ESALQ-USP — Indicadores de preços | [Acessar fonte](https://www.cepea.esalq.usp.br/) | Indicadores agropecuários e referências de mercado para soja e milho. | — |
| ABIOVE — Associação Brasileira das Indústrias de Óleos Vegetais | [Acessar fonte](https://abiove.org.br/) | Estatísticas e boletins do complexo soja usados como referências setoriais. | — |
| Yahoo Finance — futuros agrícolas CBOT | [Acessar fonte](https://finance.yahoo.com/) | Fonte não oficial de cotações dos contratos de soja e milho utilizada na coleta de mercado; condições de acesso variáveis. | — |

As informações de produção de origem IBGE consultadas nos projetos têm referência principalmente em 2023, e o estudo histórico de queimadas utiliza 2018–2022. Esses períodos descrevem as análises consultadas, não a disponibilidade atual das fontes. Uma ocorrência de foco de calor não representa automaticamente área queimada, crime ambiental ou responsabilidade individual. O acesso ou a existência de uma URL não garantem a atualidade dos dados.
