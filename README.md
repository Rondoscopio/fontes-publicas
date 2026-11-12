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

A arquitetura, as regras de manutenção e os comandos estão em [docs/catalogo-relacional.md](docs/catalogo-relacional.md).

### Objetivo e pendências de desenvolvimento

Este repositório acompanha a proposta de construir uma interface pública para consultar os dados do OSINT Rondônia. As pendências antigas podem estar desatualizadas; o conteúdo que não é fonte, inventário ou link foi mantido aqui para orientar decisões futuras.

O objetivo registrado é criar uma interface SPA/SSG, preferencialmente com SvelteKit e geração estática, a partir dos dados versionados neste repositório. O catálogo deverá permitir navegação por categorias e abrangência, busca, filtros, tabelas, gráficos e consulta de fontes individuais. A interface não deve ser a fonte de verdade dos registros. Os sete projetos que serviram de referência de produto, arquitetura, organização de dados e curadoria estão cadastrados como fontes pendentes nos CSV. Devem ser estudados antes de adotar ou reutilizar código. As imagens ilustrativas e os parâmetros de rastreamento das URLs não fazem parte desta lista.

O link de rótulo “pendências históricas” apontava para `inventarios/pendencias-historicas.json`; esse caminho continua registrado como origem do inventário em [`data/inventario.csv`](data/inventario.csv).

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
