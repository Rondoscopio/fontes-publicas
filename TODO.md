# TODO

Este arquivo acompanha a proposta de construir uma interface pública para consultar os dados do OSINT Rondônia. As pendências antigas, que podem estar desatualizadas, continuam documentadas em [pendências históricas](inventarios/pendencias-historicas.json).

## Catálogo web pesquisável

Criar uma interface SPA/SSG, preferencialmente com SvelteKit e geração estática, a partir dos dados versionados neste repositório. O catálogo deverá permitir navegação por categorias e abrangência, busca, filtros, tabelas, gráficos e consulta de fontes individuais. A interface não deve ser a fonte de verdade dos registros.

### Projetos de referência para estudar

Os sete projetos abaixo são referências de produto, arquitetura, organização de dados e curadoria. Estudar antes de adotar ou reutilizar código. As imagens ilustrativas e os parâmetros de rastreamento das URLs não fazem parte desta lista.

#### Interfaces de catálogos e padrões de dados

- **Open App Scout**
  - Site: https://openappscout.com/
  - Código-fonte e dataset: https://github.com/tortuvshin/open-apps
  - Tecnologias e abordagem: Astro, registros em Markdown/YAML, geração estática e hospedagem na Cloudflare.
  - Estudar: busca, categorias, filtros, páginas individuais, coleções, metadados do GitHub, atualização automatizada e revisão de contribuições.
- **Awesome Self-Hosted**
  - Site: https://awesome-selfhosted.net/
  - Dataset: https://github.com/awesome-selfhosted/awesome-selfhosted-data
  - Gerador HTML: https://github.com/awesome-selfhosted/awesome-selfhosted-html
  - Abordagem: dados estruturados versionados no GitHub, separados do HTML gerado.
  - Estudar: publicação do mesmo catálogo em formatos legíveis por máquina e em interface estática, validação, taxonomias e manutenção de registros.
- **Awesome Tools**
  - Site: https://kritagyadubey.github.io/awesome-tools/
  - Repositório consultado: https://github.com/NeoPanic/awesome-tools-4
  - Tecnologias e abordagem: Markdown como origem do conteúdo, GitHub Pages e interface web estática.
  - Estudar: busca instantânea, filtros, ordenação, favoritos e geração do diretório a partir de listas Markdown.
  - Pendente: confirmar a correspondência entre a demonstração e o repositório indicado, além da manutenção e licença.

#### Diretórios OSINT e curadoria investigativa

- **OSINT Framework**
  - Site: https://osintframework.com/
  - Código-fonte e dados: https://github.com/lockfale/OSINT-Framework
  - Tecnologias e abordagem: catálogo JSON publicado como site estático e navegação hierárquica.
  - Estudar: árvore de categorias, subcategorias e navegação por grupos de fontes e ferramentas OSINT.
- **Bellingcat Investigation Toolkit**
  - Site: https://bellingcat.gitbook.io/toolkit
  - Repositório: https://github.com/bellingcat/toolkit
  - Tecnologias e abordagem: conteúdo em Markdown, GitBook, automações com GitHub Actions e exportações CSV.
  - Estudar: curadoria investigativa, organização temática, descrições, guias, qualidade de metadados, revisão e geração de formatos reutilizáveis.

#### Geradores e frameworks reutilizáveis

- **Awesome Website**
  - Demonstração: https://raideno.github.io/awesome/
  - Código-fonte: https://github.com/raideno/awesome
  - Template: https://github.com/raideno/easy-awesome
  - Tecnologias e abordagem: registros em YAML, geração por GitHub Actions e publicação no GitHub Pages.
  - Estudar: transformação de arquivos estruturados em catálogo navegável, tags, grupos, filtros e fluxo de atualização.
  - Pendente: conferir a disponibilidade atual da demonstração e a compatibilidade do modelo de dados.
- **Grove**
  - Site: https://withgrove.dev/
  - Código-fonte: https://github.com/tortuvshin/grove
  - Tecnologias e abordagem: Astro, conteúdo Markdown/YAML, geração estática e framework reutilizável orientado a Git.
  - Estudar: schemas, taxonomias, busca, filtros, páginas individuais, coleções, metadados do GitHub, validação de registros e geração de README.

### Atividades

- [ ] Comparar os sete projetos quanto a licenças, manutenção, arquitetura, acessibilidade, desempenho e experiência de navegação.
- [ ] Documentar as funcionalidades interessantes de cada referência e selecionar quais serão implementadas no catálogo.
- [ ] Definir a arquitetura SSG/SPA e avaliar SvelteKit com adapter-static e hospedagem por GitHub Pages ou Cloudflare Pages.
- [ ] Projetar um esquema normalizado, preferencialmente até a terceira forma normal, para fontes, categorias, organizações, localidades, abrangências, tags, links e relacionamentos.
- [ ] Migrar os registros JSON existentes sem descartar campos, preservando origem, histórico, status de validação e identificadores.
- [ ] Gerar exportações CSV, JSON e SQLite reproduzíveis a partir da fonte de dados versionada.
- [ ] Implementar busca textual, filtros combináveis, ordenação, tabelas, gráficos e páginas de detalhe, com indicadores de cobertura e atualização.
- [ ] Avaliar navegação por árvore, coleções e favoritos, com parâmetros de busca e filtros compartilháveis por URL.
- [ ] Adicionar validação automática de esquema, URLs, duplicidades e integridade referencial no CI.
- [ ] Configurar geração e publicação automática do site após alterações aprovadas.
- [ ] Separar claramente fontes públicas de investigação, ferramentas OSINT e referências técnicas de implementação.
- [ ] Avaliar licenças e condições de uso de cada projeto antes de reutilizar código ou dados de terceiros.

Os links acima são referências para avaliação, não dependências aprovadas nem fontes de investigação já auditadas.
