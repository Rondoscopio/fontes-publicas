# OSINT Rondônia — Rondoscópio

Catálogo estruturado de **fontes de dados, ferramentas, serviços, consultas e referências de OSINT** para pesquisa, jornalismo, fiscalização cidadã e análise documental, com foco inicial em Rondônia e abrangência nacional e internacional.

**Os registros estão em JSON. Este README é o único documento Markdown do repositório.** Os índices e registros auxiliares também são JSON, incluindo a migração dos links antes distribuídos por documentos Markdown.

## Estrutura e quantidade

| Categoria | Pasta | Registros |
| --- | --- | ---: |
| Fontes federais brasileiras | [federais/](federais/) | 716 |
| Fontes estaduais de Rondônia | [estaduais/](estaduais/) | 132 |
| Fontes municipais de Rondônia | [municipais/](municipais/) | 25 |
| Fontes de outros estados | [outros-estados/](outros-estados/) | 281 |
| Fontes de outros municípios | [outros-municipios/](outros-municipios/) | 19 |
| Fontes internacionais | [internacionais/](internacionais/) | 142 |
| Agregadores e portais de consulta | [agregadores/](agregadores/) | 733 |
| Jornalismo e investigação | [jornalismo/](jornalismo/) | 14 |
| **Subtotal de fontes principais** | | **2.062** |
| APIs do catálogo ChelfoAPI, importadas separadamente | [chelfoapi/](chelfoapi/) | 959 |
| **Total de cadastros de fontes** | | **3.021** |
| Ferramentas e serviços | [ferramentas/](ferramentas/) | 1.063 |
| Consultas predefinidas | [consultas/](consultas/) | 162 |
| Referências e documentação | [referencias/](referencias/) | 66 |
| **Total de ferramentas, consultas e referências** | | **1.291** |

Os números contam **fichas**, não URLs únicas. Há sobreposição de serviços entre pastas e inventários, e múltiplos registros podem apontar para uma mesma fonte. As 959 fichas da ChelfoAPI foram preservadas com seus metadados originais.

## Inventários JSON e rastreabilidade

- [Migração de links Markdown](inventarios/migracao-links-markdown.json): **1.630 URLs externas distintas**, cada uma com indicação da ficha JSON que a representa e dos documentos de origem. Os arquivos Markdown antigos foram removidos somente depois dessa preservação.
- [Seleção de 100 fontes e 100 ferramentas](inventarios/selecao-100-fontes-e-ferramentas.json): listas estruturadas com a ordem, os nomes e os respectivos registros JSON.
- [Pendências históricas](inventarios/pendencias-historicas.json): tarefas do antigo TODO, com status **histórico**, que pode estar desatualizado.
- [Links do OSINT Brazuca](inventarios/osint-brazuca-links.json): 1.275 referências classificadas e vinculadas a fichas.
- [Links do Awesome OSINT](inventarios/awesome-osint-links.json): 1.394 referências classificadas e vinculadas a fichas.
- [Inventário completo da ChelfoAPI](inventarios/chelfoapi-apis.json): 959 registros, sendo 845 URLs distintas **dentro dessa origem**.
- [Famílias históricas da ChelfoAPI](inventarios/chelfoapi-familias-documentadas.json): documentação auxiliar de 15 famílias anteriormente identificadas.

Os diretórios OSINT utilizados como referências são [OSINT Brazuca](https://github.com/osintbrazuca/osint-brazuca) e [Awesome OSINT](https://github.com/jivoi/awesome-osint). Consulte suas respectivas licenças antes de redistribuir conteúdos derivados; a licença do catálogo não autoriza coleta indiscriminada em serviços de terceiros.

## Exemplos de recortes temáticos

- **Agricultura, economia e queimadas:** IBGE/SIDRA, Banco Central/SGS, CONAB, INPE, USDA, CEPEA/ESALQ, ABIOVE e mercado de commodities. As fontes estão representadas em fichas próprias nas pastas federais, internacionais e de agregadores.
- **Educação e produção científica:** IDEB, ENEM, Saeb, Enamed, Censo Escolar, e-MEC, Enade, IDD, CPC, IGC, CAPES, CNPq, SciELO, OpenAlex, Crossref, MCTI e INPI.
- **Clima e fenômenos oceânicos:** [Diagnóstico ENSO](internacionais/noaa-diagnostico-enso.json), [Monitoramento ENSO](internacionais/noaa-cpc-monitoramento-enso.json) e [DOS ENSO Platform](internacionais/noaa-dos-plataforma-enso.json) da NOAA.
- **Fiscalização pública e vínculos documentados:** transparência, orçamento, transferências, contratos, licitações, sanções, justiça e registros institucionais, conforme disponibilidade e limitações legais.

## Estrutura de uma ficha

Uma fonte pode ter este formato simplificado:

```json
{
  "nome": "INEP — Resultados do IDEB",
  "descricao": "Resultados por escola, município, rede e ano.",
  "abrangencia": "Federal / Brasil, com recorte para Rondônia",
  "url": "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados"
}
```

Fichas de ferramentas e inventários podem apresentar outros campos, como categoria, origem, tecnologia, restrições, status de validação e identificação interna. Os identificadores e nomes dos arquivos são estáveis, sem garantia de disponibilidade atual da página externa.

## Política de cadastro de portais

Quando uma URL é enviada apenas como exemplo de um serviço, a ficha deve apontar para a **página inicial ou entrada geral da plataforma**, não para perfis de pessoas, candidaturas, doadores, empresas, pesquisas por documento ou reportagens isoladas. Remover parâmetros de rastreamento e não armazenar identificadores de alvos na ficha da fonte. Investigações específicas devem documentar separadamente finalidade, relevância pública, evidências e direito de resposta. O cadastro de um portal jornalístico não implica endosso de sua linha editorial.

## Limites e uso responsável

- **Referência não é validação.** A inclusão não comprova confiabilidade, funcionamento, licenciamento, autenticidade ou atualização de dados e endpoints.
- **Acesso público não significa coleta irrestrita.** Respeitar legislação, LGPD, termos, limitações técnicas, direitos autorais e proteção de dados pessoais.
- **Correlação não é culpa.** Relações societárias, vínculos familiares, geolocalização e coincidências estatísticas exigem interpretação, contexto e evidências adicionais.
- **Comparações devem respeitar método e tempo.** Indicadores científicos, educacionais, econômicos e ambientais não são intercambiáveis, e a ausência de dado não equivale a zero.
- **Status de fontes varia.** Algumas fichas derivam de diretórios de terceiros ou de material fornecido por colaboradores e ainda dependem de auditoria.

A catalogação não concede autoridade policial, judicial ou permissão para investigar pessoas por meios ilegais.
