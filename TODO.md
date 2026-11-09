# TODO — Fontes públicas e monitoramento

Tarefas propostas para pesquisa e desenvolvimento do Rondoscópio. **Não estão implementadas**. O cadastro de um serviço no catálogo não implica permissão para coleta automática, armazenamento ou redistribuição.

## Monitoramento por rádio SDR

- [ ] Estudar a viabilidade técnica e jurídica de receber e registrar sinais de rádio com SDR (*software-defined radio*) em Rondônia.
- [ ] Identificar frequências e protocolos de recepção permitida, prioritariamente sinais públicos de telemetria, meteorologia e dados aeronáuticos de difusão aberta; não interceptar comunicações privadas ou protegidas.
- [ ] Definir hardware, antenas, cobertura territorial, relógio sincronizado, armazenamento de metadados e, somente quando permitido, sinais IQ/áudio.
- [ ] Definir política de privacidade, retenção de gravações, segurança, licenças e referências às regras aplicáveis da Anatel e demais autoridades.
- [ ] Construir prova de conceito isolada e documentar limitações de alcance, interferência e qualidade dos sinais.

## Rastreamento de aeronaves e Flightradar24

- [ ] Estudar a integração de dados de tráfego aéreo e histórico de voos relativos a Rondônia, começando pelo [Flightradar24](https://www.flightradar24.com/).
- [ ] Avaliar condições e custos da [API oficial do Flightradar24](https://www.flightradar24.com/terms-of-service), incluindo restrições de coleta, armazenamento, cache e redistribuição; **não** fazer scraping da interface pública.
- [ ] Comparar com fontes já catalogadas, como OpenSky Network, para assegurar licenças e cobertura regional adequadas.
- [ ] Considerar recepção local de ADS-B por SDR e registro de sinais públicos de posicionamento, sujeitos à verificação de regras e privacidade.
- [ ] Propor painel de tráfego aéreo e métricas agregadas para a região, distinguindo observações reais, lacunas de cobertura e dados inferidos.

## Remuneração e cargos nos poderes e órgãos autônomos

- [ ] Validar e registrar endpoints específicos, campos e periodicidade das folhas do TJRO, TCE-RO e MPRO, incluindo mudanças de sistemas e arquivos históricos.
- [ ] Inventariar separadamente as câmaras municipais e os órgãos dos 52 municípios, além dos poderes Executivo e Legislativo estaduais.
- [ ] Avaliar comparabilidade de servidores efetivos, comissionados, cedidos, magistrados, membros, aposentados, pensionistas, verbas indenizatórias e diárias.
- [ ] Registrar origem, competência, vigência da tabela, gratificações e regras de publicidade; não expor identificadores pessoais protegidos.

