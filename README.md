![Rondoscópio: OSINT Rondônia](assets/banner.svg)

# OSINT Rondônia

Catálogo público de fontes de dados, ferramentas e referências para pesquisa, jornalismo, investigação e fiscalização cidadã em Rondônia, com fontes brasileiras e internacionais. Parte do [Rondoscópio](https://github.com/Rondoscopio).

[![CSV, SQLite e Data Package](https://img.shields.io/badge/Dados-CSV%20%7C%20SQLite%20%7C%20Data%20Package%20v2-2563eb?style=for-the-badge&labelColor=0b1120)](datapackage.json)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-AGPL--3.0--or--later-2563eb?style=for-the-badge&labelColor=0b1120&logo=gnu&logoColor=white)](LICENSE)

[![Último Commit](https://img.shields.io/github/last-commit/Rondoscopio/osint-rondonia/main?label=%C3%9Altimo%20Commit&style=flat-square&labelColor=0b1120&color=b45309&logo=git&logoColor=white)](https://github.com/Rondoscopio/osint-rondonia/commits/main)
[![Commits por Mês](https://img.shields.io/github/commit-activity/m/Rondoscopio/osint-rondonia?label=Commits%20por%20M%C3%AAs&style=flat-square&labelColor=0b1120&color=b45309&logo=git&logoColor=white)](https://github.com/Rondoscopio/osint-rondonia/graphs/commit-activity)
[![PRs Abertas](https://img.shields.io/github/issues-pr/Rondoscopio/osint-rondonia?label=PRs%20Abertas&style=flat-square&labelColor=0b1120&color=b45309&logo=github&logoColor=white)](https://github.com/Rondoscopio/osint-rondonia/pulls)
[![Issues Abertas](https://img.shields.io/github/issues/Rondoscopio/osint-rondonia?label=Issues%20Abertas&style=flat-square&labelColor=0b1120&color=b45309&logo=github&logoColor=white)](https://github.com/Rondoscopio/osint-rondonia/issues)
[![Forks](https://img.shields.io/github/forks/Rondoscopio/osint-rondonia?label=Forks&style=flat-square&labelColor=0b1120&color=b45309&logo=github&logoColor=white)](https://github.com/Rondoscopio/osint-rondonia/forks)
[![Feito no 🇧🇷 Brasil](https://img.shields.io/badge/Feito%20no-%F0%9F%87%A7%F0%9F%87%B7%20Brasil-009440?style=flat-square&labelColor=0b1120)](https://pt.wikipedia.org/wiki/Brasil)

## Catálogo de dados

O catálogo de fontes OSINT, ferramentas, APIs e inventários está disponível nestas distribuições:

- [SQLite relacional](data/exports/catalog.sqlite), com tabelas e chaves estrangeiras.
- [CSV e Data Package v2](datapackage.json); os CSV em [data/](data/) são a fonte canônica.

A consulta por ID de categoria, a arquitetura e os comandos estão em [docs/catalogo-relacional.md](docs/catalogo-relacional.md).

### Objetivo e pendências de desenvolvimento

Este repositório acompanha a proposta de construir uma interface pública para consultar os dados do OSINT Rondônia. As pendências antigas podem estar desatualizadas; as tarefas foram mantidas aqui para orientar decisões futuras.

O objetivo registrado é criar uma interface SPA/SSG, preferencialmente com SvelteKit e geração estática, a partir dos dados versionados neste repositório. O catálogo deverá permitir navegação por categorias e abrangência, busca, filtros, tabelas, gráficos e consulta de fontes individuais. A interface não deve ser a fonte de verdade dos registros. Os sete projetos que serviram de referência de produto, arquitetura, organização de dados e curadoria estão cadastrados como fontes pendentes nos CSV. Devem ser estudados antes de adotar ou reutilizar código. As imagens ilustrativas e os parâmetros de rastreamento das URLs não fazem parte desta lista.

No TODO original, o contexto, o objetivo e as 12 atividades tinham `status_triagem=pendente`; todas as atividades estavam desmarcadas.

As atividades abaixo continuam abertas (`status_triagem=pendente`; nenhuma está concluída):

- [ ] Separar claramente fontes públicas de investigação, ferramentas OSINT e referências técnicas de implementação.
- [ ] Migrar os registros JSON existentes sem descartar campos, preservando origem, histórico, status de validação e identificadores.
- [ ] Comparar os sete projetos quanto a licenças, manutenção, arquitetura, acessibilidade, desempenho e experiência de navegação.
- [ ] Adicionar validação automática de esquema, URLs, duplicidades e integridade referencial no CI.
- [ ] Implementar busca textual, filtros combináveis, ordenação, tabelas, gráficos e páginas de detalhe, com indicadores de cobertura e atualização.
- [ ] Gerar exportações CSV, JSON e SQLite reproduzíveis a partir da fonte de dados versionada.
- [ ] Configurar geração e publicação automática do site após alterações aprovadas.
- [ ] Projetar um esquema normalizado, preferencialmente até a terceira forma normal, para fontes, categorias, organizações, localidades, abrangências, tags, links e relacionamentos.
- [ ] Avaliar licenças e condições de uso de cada projeto antes de reutilizar código ou dados de terceiros.
- [ ] Definir a arquitetura SSG/SPA e avaliar SvelteKit com adapter-static e hospedagem por GitHub Pages ou Cloudflare Pages.
- [ ] Documentar as funcionalidades interessantes de cada referência e selecionar quais serão implementadas no catálogo.
- [ ] Avaliar navegação por árvore, coleções e favoritos, com parâmetros de busca e filtros compartilháveis por URL.

### Tarefas do inventário histórico

A lista conserva o texto e o estado de conclusão registrados na época.

#### Monitoramento por rádio SDR

- [ ] Estudar a viabilidade técnica e jurídica de receber e registrar sinais de rádio com SDR (*software-defined radio*) em Rondônia.
- [ ] Identificar frequências e protocolos de recepção permitida, prioritariamente sinais públicos de telemetria, meteorologia e dados aeronáuticos de difusão aberta; não interceptar comunicações privadas ou protegidas.
- [ ] Definir hardware, antenas, cobertura territorial, relógio sincronizado, armazenamento de metadados e, somente quando permitido, sinais IQ/áudio.
- [ ] Definir política de privacidade, retenção de gravações, segurança, licenças e referências às regras aplicáveis da Anatel e demais autoridades.
- [ ] Construir prova de conceito isolada e documentar limitações de alcance, interferência e qualidade dos sinais.

#### Rastreamento de aeronaves e Flightradar24

- [ ] Estudar a integração de dados de tráfego aéreo e histórico de voos relativos a Rondônia, começando pelo [Flightradar24](https://www.flightradar24.com/).
- [ ] Avaliar condições e custos da [API oficial do Flightradar24](https://www.flightradar24.com/terms-of-service), incluindo restrições de coleta, armazenamento, cache e redistribuição; **não** fazer scraping da interface pública.
- [ ] Comparar com fontes já catalogadas, como OpenSky Network, para assegurar licenças e cobertura regional adequadas.
- [ ] Considerar recepção local de ADS-B por SDR e registro de sinais públicos de posicionamento, sujeitos à verificação de regras e privacidade.
- [ ] Propor painel de tráfego aéreo e métricas agregadas para a região, distinguindo observações reais, lacunas de cobertura e dados inferidos.

#### Remuneração e cargos nos poderes e órgãos autônomos

- [ ] Validar e registrar endpoints específicos, campos e periodicidade das folhas do TJRO, TCE-RO e MPRO, incluindo mudanças de sistemas e arquivos históricos.
- [ ] Inventariar separadamente as câmaras municipais e os órgãos dos 52 municípios, além dos poderes Executivo e Legislativo estaduais.
- [ ] Avaliar comparabilidade de servidores efetivos, comissionados, cedidos, magistrados, membros, aposentados, pensionistas, verbas indenizatórias e diárias.
- [ ] Registrar origem, competência, vigência da tabela, gratificações e regras de publicidade; não expor identificadores pessoais protegidos.

#### Expansão nacional de fontes OSINT

- [ ] Extrair com autorização e conferir os 959 links de documentação do [catálogo ChelfoIA/Manus](https://www.chelfoapi.com/). Seu quadro detalhado é carregado via JavaScript e não foi acessível nesta rodada; não afirmar que foram importados 959 registros.
- [ ] Deduplicar por URL os links recém-importados em relação aos registros históricos do catálogo e testar acessibilidade e licenças; novos cadastros são apenas candidatos, não fontes auditadas.
- [ ] Priorizar validação de portais de tribunais, contratos e sanções de todos os estados e municípios; manter status de processos, decisões e sanções com temporalidade e presunção de inocência.

#### Diretório OSINT ampliado — acompanhamento

- [x] Adotar o nome `osint-rondonia` e documentar que o catálogo abrange fontes, ferramentas, serviços e consultas.
- [x] Criar fichas para cada um dos 1275 links do inventário OSINT Brazuca e 1394 links do Awesome OSINT, preservando as fichas já existentes.
- [ ] Obter uma exportação licenciada ou mecanismo autorizado de acesso às 959 fichas da ChelfoIA (pesquisa Manus AI), para completar os registros individuais sem fabricar URLs.
- [ ] Validar disponibilidade, regras de coleta, licenças, precisão, classificação de ferramenta versus fonte e duplicidades históricas entre as fichas existentes.
- [ ] Construir um gerador que derive automaticamente README e relatórios de cobertura dos catálogos tipados.

### Desenvolvimento e exportação

Requer Docker com Compose e [Just](https://just.systems/). Python e Frictionless rodam exclusivamente no contêiner.

```bash
just build
just validate
just test
just sqlite
```

## License

**SPDX-License-Identifier:** `AGPL-3.0-or-later`

[![GNU AGPLv3 Image](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.html)

This project is Free Software: You can use, study, share and improve it at your
will. Specifically, you can redistribute and/or modify it under the terms of the
[GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Third-party sources and materials remain subject to their respective licenses and terms of use.

---
