# Fontes públicas — Rondoscópio

Catálogo de fontes de informação relevantes para a investigação, a fiscalização cidadã e o acompanhamento de Rondônia e de seus municípios. Inclui órgãos públicos, bases de dados, instituições privadas e internacionais, agregadores e veículos jornalísticos.

## Organização

Cada fonte é representada por **um arquivo JSON** dentro da pasta correspondente à categoria principal de sua `abrangencia`:

| Pasta | Fontes |
| --- | ---: |
| `agregadores/` | 36 |
| `estaduais/` | 76 |
| `federais/` | 174 |
| `internacionais/` | 56 |
| `jornalismo/` | 9 |
| `municipais/` | 23 |
| **Total** | **374** |

Os nomes dos arquivos são derivados dos nomes das fontes, em minúsculas, sem acentos e separados por hífens.

## Estrutura de cada fonte

```json
{
  "nome": "IBGE — SIDRA",
  "descricao": "Banco de tabelas estatísticas e séries históricas de censos e pesquisas, com recortes territoriais.",
  "abrangencia": "Federal / Brasil, com recorte para Rondônia",
  "url": "https://sidra.ibge.gov.br/"
}
```

- `nome`: identificação da fonte ou do serviço.
- `descricao`: finalidade e tipos de informação disponíveis.
- `abrangencia`: categoria principal e recorte geográfico ou institucional.
- `url`: endereço de referência.

## Escopo

O catálogo não se limita a instituições sediadas em Rondônia. Fontes nacionais, internacionais e de outros territórios são relevantes quando permitem investigar acontecimentos ou decisões com possíveis efeitos no estado, como transferências de recursos, contratações, relações empresariais, clima, hidrologia, comércio e cadeias produtivas.

**Importante:** inclusão no catálogo não significa que todos os links, APIs ou conjuntos de dados tenham sido testados individualmente. Nem toda fonte é uma API ou disponibiliza dados estruturados. Notícias e portais institucionais funcionam como pontos de partida para apuração, não como evidência conclusiva.

## Contribuições

Ao adicionar uma fonte, crie um único arquivo `.json` com **um objeto** contendo os quatro campos indicados. Use a pasta correspondente à categoria da abrangência e evite duplicar fontes existentes. Prefira páginas oficiais, documentações estáveis e informações verificáveis.

Este repositório é um catálogo de fontes, não uma atribuição de irregularidades a instituições ou pessoas.
