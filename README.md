# OSINT Rondônia — Rondoscópio

Catálogo de **fontes, ferramentas, serviços, consultas e referências OSINT** relevantes para pesquisa, fiscalização cidadã e investigação documental. Rondônia é o território inicial de interesse, mas a cobertura abrange Brasil e exterior. A inclusão de um recurso não comprova confiabilidade, acesso ou autorização para coleta automatizada.

## Organização

As **fontes** continuam representadas por um JSON nas pastas de origem/abrangência. Os registros importados da ChelfoAPI estão separados em `chelfoapi/`, mantendo identificadores originais e os nove campos de origem; não são contabilizados novamente na tabela histórica abaixo. Ferramentas, consultas e referências editoriais agora têm fichas separadas para não serem confundidas com dados oficiais:

| Pasta | Fontes |
| --- | ---: |
| `agregadores/` | 728 |
| `estaduais/` | 132 |
| `federais/` | 713 |
| `internacionais/` | 138 |
| `jornalismo/` | 9 |
| `municipais/` | 25 |
| `outros-estados/` | 281 |
| `outros-municipios/` | 19 |
| **Total** | **2045** |

| Outros recursos catalogados | Novas fichas |
| --- | ---: |
| `ferramentas/` | 979 |
| `consultas/` | 162 |
| `referencias/` | 60 |
| **Novos registros tipados** | **1201** |

Os novos arquivos de ferramentas e referências usam um nome normalizado e um identificador derivado da URL, preservando a origem e evitando colisões de nomes.

## Fontes agrícolas, econômicas e ambientais

- [Fontes originais de agricultura, commodities, câmbio e queimadas](FONTES-AGROPECUARIA-QUEIMADAS.md). Apenas serviços e instituições de origem, com indicação das fichas já presentes no catálogo; sem referências a projetos ou produtos derivados.

## Monitoramento climático ENSO — NOAA/CPC

- [Diagnóstico ENSO: boletim oficial de El Niño e La Niña](internacionais/noaa-diagnostico-enso.json), já catalogado.
- [Monitoramento ENSO: condições atuais, previsões, séries históricas e materiais técnicos](internacionais/noaa-cpc-monitoramento-enso.json).
- [DOS ENSO Platform: painel de monitoramento e impactos climáticos](internacionais/noaa-dos-plataforma-enso.json).

As três fontes pertencem ao Climate Prediction Center da NOAA. Prognósticos e probabilidades são temporais e não asseguram impactos locais específicos em Rondônia. O antigo endereço do painel DOS ENSO retornou erro 404 e foi substituído pelo endereço oficial encontrado.

## Educação, ciência e tecnologia

- [Fontes detalhadas de IDEB, ENEM, Enamed, e-MEC, conceitos do Inep, CAPES, CNPq, artigos científicos e inovação](FONTES-EDUCACAO-CIENCIA-TECNOLOGIA.md). Organizadas por área e com referência às fichas preexistentes, sem duplicações.

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

## Catálogo ampliado e cobertura das três origens

- [**Ferramentas e serviços**](FERRAMENTAS-DIRETORIOS-OSINT.md): fichas individuais organizadas por categoria.
- [**Onze ferramentas OSINT selecionadas**](FERRAMENTAS-OSINT-SELECIONADAS.md): acesso direto aos repositórios e às fichas, com reaproveitamento dos cadastros existentes.
- [**Referências e consultas**](REFERENCIAS-DIRETORIOS-OSINT.md): guias, consultas pré-definidas e materiais que não são bases governamentais.
- [**Inventário OSINT Brazuca**](inventarios/osint-brazuca-links.json): **1275 de 1275 links** vinculados a uma ficha.
- [**Inventário Awesome OSINT**](inventarios/awesome-osint-links.json): **1394 de 1394 links** vinculados a uma ficha.
- [**Inventário completo da ChelfoAPI**](inventarios/chelfoapi-apis.json): **959 de 959 registros** transcritos do JavaScript do painel; [fichas individuais](chelfoapi/) com metadados originais. URLs e endpoints ainda não verificados.
- [**Famílias federais documentadas da ChelfoIA**](inventarios/chelfoapi-familias-documentadas.json): 15 famílias previamente identificadas; arquivo histórico complementar.
- [**Auditoria de cobertura**](COBERTURA-OSINT.md): critérios, números e limitações da importação.

**Cobertura de catálogo:** 1275 referências do OSINT Brazuca, 1394 do Awesome OSINT e 959 registros da ChelfoAPI possuem referências individualizadas. A existência e acessibilidade dos serviços não foram verificadas.

## Escopo

O catálogo também abrange ferramentas e serviços que não são fontes públicas, bem como instituições fora de Rondônia. A pesquisa não se limita a instituições sediadas em Rondônia. Fontes nacionais, internacionais e de outros territórios são relevantes quando permitem investigar acontecimentos ou decisões com possíveis efeitos no estado, como transferências de recursos, contratações, relações empresariais, clima, hidrologia, comércio e cadeias produtivas.

**Importante:** inclusão no catálogo não significa que todos os links, APIs ou conjuntos de dados tenham sido testados individualmente. Nem toda fonte é uma API ou disponibiliza dados estruturados. Notícias e portais institucionais funcionam como pontos de partida para apuração, não como evidência conclusiva.

## Catálogo OSINT: 100 fontes verificáveis

A seleção de 100 fontes está mapeada individualmente em [OSINT-100-FONTES.md](OSINT-100-FONTES.md). Cada item aponta para um JSON presente neste catálogo, incluindo fontes que já estavam cadastradas.

## Ferramentas de OSINT (100 referências)

Estas são **ferramentas**, não fontes oficiais. Estão listadas para pesquisa, avaliação e eventual integração, sem indicação de que estejam instaladas ou autorizadas para coleta indiscriminada. Licença, preços, limites de uso e permissões devem ser avaliados caso a caso.

### Pesquisa e acompanhamento (1–10)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 1 | [Google Advanced Search](https://www.google.com/advanced_search) | Pesquisa avançada e operadores |
| 2 | [Bing](https://www.bing.com/) | Busca na internet |
| 3 | [DuckDuckGo](https://duckduckgo.com/) | Mecanismo de pesquisa |
| 4 | [Brave Search](https://search.brave.com/) | Mecanismo de pesquisa |
| 5 | [Startpage](https://www.startpage.com/) | Pesquisa com foco em privacidade |
| 6 | [SearXNG](https://docs.searxng.org/) | Metabuscador auto-hospedável |
| 7 | [Marginalia Search](https://search.marginalia.nu/) | Busca em páginas menos comerciais |
| 8 | [Google Alerts](https://www.google.com/alerts) | Alertas por palavras-chave |
| 9 | [Google Trends](https://trends.google.com/trends/) | Tendências de pesquisas |
| 10 | [RSSHub](https://docs.rsshub.app/) | Geração de feeds RSS |

### Preservação e arquivamento (11–20)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 11 | [Wayback Machine](https://web.archive.org/) | Histórico de páginas |
| 12 | [Archive.today](https://archive.today/) | Captura de páginas |
| 13 | [ArchiveBox](https://archivebox.io/) | Arquivamento auto-hospedado |
| 14 | [ArchiveWeb.page](https://archiveweb.page/) | Captura de sessões web |
| 15 | [SingleFile](https://github.com/gildas-lormeau/SingleFile) | Salvar páginas em HTML |
| 16 | [Hunchly](https://www.hunch.ly/) | Registro de investigação e navegação |
| 17 | [changedetection.io](https://changedetection.io/) | Monitoramento de mudanças |
| 18 | [Bellingcat Auto Archiver](https://github.com/bellingcat/auto-archiver) | Preservação automatizada de páginas |
| 19 | [Browsertrix Crawler](https://browsertrix.com/) | Arquivamento de sites |
| 20 | [ReplayWeb.page](https://replayweb.page/) | Reprodução de arquivos WARC e WACZ |

### Identidades e perfis públicos (21–30)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 21 | [Sherlock](https://github.com/sherlock-project/sherlock) | Pesquisa de nomes de usuário |
| 22 | [Maigret](https://github.com/soxoj/maigret) | Pesquisa de perfis públicos |
| 23 | [WhatsMyName](https://whatsmyname.app/) | Verificação de nomes de usuário |
| 24 | [Blackbird](https://github.com/p1ngul1n0/blackbird) | Busca de perfis públicos |
| 25 | [Namechk](https://namechk.com/) | Disponibilidade de nomes de usuário |
| 26 | [GHunt](https://github.com/mxrch/GHunt) | Pesquisa de metadados públicos Google |
| 27 | [theHarvester](https://github.com/laramies/theHarvester) | Descoberta de domínios e informações expostas |
| 28 | [PhoneInfoga](https://github.com/sundowndev/phoneinfoga) | Pesquisa sobre numeração telefônica |
| 29 | [Holehe](https://github.com/megadose/holehe) | Verificação de vinculação de e-mails |
| 30 | [Social Analyzer](https://github.com/qeeqbox/social-analyzer) | Investigação de perfis públicos |

### Domínios e infraestrutura (31–40)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 31 | [Shodan](https://www.shodan.io/) | Busca de serviços expostos |
| 32 | [Censys](https://search.censys.io/) | Pesquisa de ativos de rede |
| 33 | [SecurityTrails](https://securitytrails.com/) | Histórico DNS |
| 34 | [DNSDumpster](https://dnsdumpster.com/) | Visualização DNS |
| 35 | [crt.sh](https://crt.sh/) | Certificados TLS públicos |
| 36 | [urlscan.io](https://urlscan.io/) | Inspeção de páginas web |
| 37 | [VirusTotal](https://www.virustotal.com/) | Análise de URLs e arquivos |
| 38 | [RIPEstat](https://stat.ripe.net/) | Consultas de roteamento e ASN |
| 39 | [Hurricane Electric BGP](https://bgp.he.net/) | Prefixos e sistemas autônomos |
| 40 | [Netlas](https://netlas.io/) | Busca de infraestrutura de internet |

### Imagens, vídeo e autenticidade (41–50)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 41 | [ExifTool](https://exiftool.org/) | Metadados de imagens e arquivos |
| 42 | [InVID-WeVerify](https://www.invid-project.eu/) | Verificação de imagens e vídeos |
| 43 | [Google Lens](https://lens.google/) | Pesquisa reversa de imagens |
| 44 | [TinEye](https://tineye.com/) | Busca reversa de imagens |
| 45 | [Yandex Images](https://yandex.com/images/) | Pesquisa de imagens |
| 46 | [FotoForensics](https://fotoforensics.com/) | Inspeção de imagens |
| 47 | [Forensically](https://29a.ch/photo-forensics/) | Filtros de análise visual |
| 48 | [FFmpeg](https://ffmpeg.org/) | Processamento de áudio e vídeo |
| 49 | [MediaInfo](https://mediaarea.net/en/MediaInfo) | Metadados de mídias |
| 50 | [VLC](https://www.videolan.org/vlc/) | Reprodução e inspeção de mídias |

### Geolocalização e satélites (51–60)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 51 | [QGIS](https://qgis.org/) | Análise geoespacial |
| 52 | [GDAL](https://gdal.org/) | Processamento de formatos geográficos |
| 53 | [Google Earth Pro](https://www.google.com/earth/about/versions/) | Exploração temporal de imagens |
| 54 | [JOSM](https://josm.openstreetmap.de/) | Editor de OpenStreetMap |
| 55 | [Overpass Turbo](https://overpass-turbo.eu/) | Consultas ao OpenStreetMap |
| 56 | [Mapillary](https://www.mapillary.com/) | Fotos públicas georreferenciadas |
| 57 | [SunCalc](https://www.suncalc.org/) | Posição do Sol e sombras |
| 58 | [Copernicus Browser](https://dataspace.copernicus.eu/browser/) | Visualização Sentinel |
| 59 | [Kepler.gl](https://kepler.gl/) | Visualização geográfica |
| 60 | [NASA Worldview](https://worldview.earthdata.nasa.gov/) | Imagens orbitais e camadas temporais |

### Extração e processamento de dados (61–70)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 61 | [OpenRefine](https://openrefine.org/) | Limpeza e reconciliação |
| 62 | [pandas](https://pandas.pydata.org/) | Análise tabular |
| 63 | [DuckDB](https://duckdb.org/) | SQL analítico em arquivos |
| 64 | [SQLite](https://sqlite.org/) | Banco de dados embutido |
| 65 | [PostgreSQL](https://www.postgresql.org/) | Banco relacional e extensões |
| 66 | [Apache NiFi](https://nifi.apache.org/) | Fluxos de dados |
| 67 | [Airbyte](https://airbyte.com/) | Integrações de dados |
| 68 | [dbt](https://www.getdbt.com/) | Transformações e testes |
| 69 | [DVC](https://dvc.org/) | Versionamento de dados |
| 70 | [Datasette](https://datasette.io/) | Publicação de bases SQLite |

### Vínculos e visualização (71–80)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 71 | [Maltego](https://www.maltego.com/) | Análise de vínculos |
| 72 | [Gephi](https://gephi.org/) | Visualização de grafos |
| 73 | [Cytoscape](https://cytoscape.org/) | Análise de redes |
| 74 | [Linkurious](https://linkurious.com/) | Exploração de relacionamentos |
| 75 | [Graphistry](https://www.graphistry.com/) | Visualização de grafos grandes |
| 76 | [Neo4j Bloom](https://neo4j.com/product/bloom/) | Exploração de grafos Neo4j |
| 77 | [Kumu](https://kumu.io/) | Mapeamento de sistemas |
| 78 | [Flourish](https://flourish.studio/) | Visualizações interativas |
| 79 | [Apache Superset](https://superset.apache.org/) | Business Intelligence |
| 80 | [Metabase](https://www.metabase.com/) | Dashboards e SQL |

### PDFs e documentos (81–90)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 81 | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) | OCR de imagens |
| 82 | [OCRmyPDF](https://ocrmypdf.readthedocs.io/) | OCR para PDFs |
| 83 | [Apache Tika](https://tika.apache.org/) | Extração de texto e metadados |
| 84 | [pdfminer.six](https://github.com/pdfminer/pdfminer.six) | Extração de texto PDF |
| 85 | [PyMuPDF](https://pymupdf.readthedocs.io/) | Análise e leitura de PDF |
| 86 | [Tabula](https://tabula.technology/) | Extração de tabelas PDF |
| 87 | [Camelot](https://camelot-py.readthedocs.io/) | Extração tabular de PDF |
| 88 | [Docling](https://github.com/docling-project/docling) | Estruturação de documentos |
| 89 | [Unstructured](https://github.com/Unstructured-IO/unstructured) | Extração de documentos |
| 90 | [pdfplumber](https://github.com/jsvine/pdfplumber) | Extração de tabelas PDF |

### Coleta e automação (91–100)

| Nº | Ferramenta | Finalidade |
| ---: | --- | --- |
| 91 | [Scrapy](https://scrapy.org/) | Coletores web |
| 92 | [Playwright](https://playwright.dev/) | Automação de navegadores |
| 93 | [Selenium](https://www.selenium.dev/) | Automação de interfaces |
| 94 | [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) | Análise de HTML |
| 95 | [Apify](https://apify.com/) | Plataforma de coletores |
| 96 | [n8n](https://n8n.io/) | Orquestração de automações |
| 97 | [GitHub Actions](https://github.com/features/actions) | Execução automatizada |
| 98 | [Apache Airflow](https://airflow.apache.org/) | Pipelines agendados |
| 99 | [Prefect](https://www.prefect.io/) | Orquestração de fluxos |
| 100 | [SpiderFoot](https://github.com/smicallef/spiderfoot) | Correlação OSINT automatizada |

## Catálogos OSINT de outros estados e países

Foram incorporadas referências do [OSINT Brazuca](https://github.com/osintbrazuca/osint-brazuca) e do [Awesome OSINT](https://github.com/jivoi/awesome-osint). O [relatório de importação](IMPORTACOES-OSINT.md) apresenta escopo e limites, e os inventários registram **todos os links extraídos** dos dois repositórios: [Brazuca](inventarios/osint-brazuca-links.json) e [Awesome OSINT](inventarios/awesome-osint-links.json). Nem todo link é uma base: dorks, guias e ferramentas permanecem apenas no inventário e não devem ser usados para coleta de dados pessoais.

## Navegação por estado e ferramentas adicionais

- [Fontes cadastradas de outros estados e municípios](FONTES-OUTROS-ESTADOS.md)
- [Ferramentas e referências adicionais do Awesome OSINT](FERRAMENTAS-DIRETORIOS-OSINT.md)

O README mantém a seleção inicial de 100 ferramentas. A lista extensa do diretório fica em documento separado para não dificultar a leitura da página inicial.

## Tarefas de investigação e integração

As pesquisas e integrações futuras, incluindo SDR, tráfego aéreo e a cobertura completa das folhas de pagamento, estão em [TODO.md](TODO.md).

## Contribuições

Ao adicionar uma fonte, crie um único arquivo `.json` com **um objeto** contendo os quatro campos indicados. Use a pasta correspondente à categoria da abrangência e evite duplicar fontes existentes. Prefira páginas oficiais, documentações estáveis e informações verificáveis.

Este repositório é um catálogo de fontes, não uma atribuição de irregularidades a instituições ou pessoas.
