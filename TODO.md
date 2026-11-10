# TODO

Este arquivo acompanha a proposta de construir uma interface pública para consultar os dados do OSINT Rondônia. As pendências antigas, que podem estar desatualizadas, continuam documentadas em [pendências históricas](inventarios/pendencias-historicas.json).

## Catálogo web pesquisável

Criar uma interface SPA/SSG, preferencialmente com SvelteKit e geração estática, a partir dos dados versionados neste repositório. O catálogo deverá permitir navegação por categorias e abrangência, busca, filtros, tabelas, gráficos e consulta de fontes individuais. A interface não deve ser a fonte de verdade dos registros.

### Projetos para estudar

#### Interfaces de catálogos e padrões de dados

- [Open App Scout](https://openappscout.com/) | [Repositório](https://github.com/tortuvshin/open-apps). Referência de busca, filtros, categorias, coleções e páginas individuais.
- [Awesome Self-Hosted](https://awesome-selfhosted.net/) | [Dados](https://github.com/awesome-selfhosted/awesome-selfhosted-data) | [HTML](https://github.com/awesome-selfhosted/awesome-selfhosted-html). Referência de separação entre dataset estruturado e apresentação gerada.
- [Awesome Tools](https://kritagyadubey.github.io/awesome-tools/) | [Repositório](https://github.com/NeoPanic/awesome-tools-4). Referência de diretório interativo derivado de uma lista em Markdown, com busca, filtros e ordenação. Confirmar disponibilidade da demonstração antes de adotá-la.

#### Diretórios OSINT e curadoria investigativa

- [OSINT Framework](https://osintframework.com/) | [Repositório](https://github.com/lockfale/OSINT-Framework). Referência de navegação hierárquica por categorias e subcategorias.
- [Bellingcat Online Investigation Toolkit](https://bellingcat.gitbook.io/toolkit) | [Repositório](https://github.com/bellingcat/toolkit). Referência de organização, revisão e descrição de ferramentas investigativas, incluindo exportações em CSV.

#### Geradores e frameworks reutilizáveis

- [Awesome Website](https://raideno.github.io/awesome/) | [Repositório](https://github.com/raideno/awesome) | [Template](https://github.com/raideno/easy-awesome). Referência de geração de site a partir de YAML usando GitHub Actions e GitHub Pages. Confirmar disponibilidade da demonstração antes de adotá-la.
- [Grove](https://withgrove.dev/) | [Repositório](https://github.com/tortuvshin/grove). Referência de framework Astro para catálogos Git-first, taxonomias, busca, filtros, páginas individuais e saídas estruturadas.

### Atividades

- [ ] Comparar os projetos, suas licenças, manutenção, arquitetura, acessibilidade e experiência de navegação.
- [ ] Definir a arquitetura SSG/SPA e avaliar SvelteKit com adapter-static e hospedagem por GitHub Pages ou Cloudflare Pages.
- [ ] Projetar um esquema normalizado, preferencialmente até a terceira forma normal, para fontes, categorias, organizações, localidades, abrangências, tags, links e relacionamentos.
- [ ] Migrar os registros JSON existentes sem descartar campos, preservando origem, histórico, status de validação e identificadores.
- [ ] Gerar exportações CSV, JSON e SQLite reproduzíveis a partir da fonte de dados versionada.
- [ ] Implementar busca textual, filtros combináveis, ordenação, tabelas, gráficos e páginas de detalhe, com indicadores de cobertura e atualização.
- [ ] Adicionar validação automática de esquema, URLs, duplicidades e integridade referencial no CI.
- [ ] Configurar geração e publicação automática do site após alterações aprovadas.
- [ ] Separar claramente fontes públicas de investigação, ferramentas OSINT e referências técnicas de implementação.
- [ ] Avaliar licenças e condições de uso de cada projeto antes de reutilizar código ou dados de terceiros.

Os links acima são referências para avaliação, não dependências aprovadas nem fontes de investigação já auditadas.
