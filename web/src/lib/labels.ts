const words: Record<string, string> = {
  acervo: 'acervo',
  agregador: 'agregador',
  agroambiental: 'agroambiental',
  arquivo: 'arquivo',
  atas: 'atas',
  atividade: 'atividade',
  cadastro: 'cadastro',
  ciencias: 'ciências',
  cientifico: 'científico',
  comercial: 'comercial',
  consulta: 'consulta',
  condicoes: 'condições',
  dados: 'dados',
  diario: 'diário',
  documentacao: 'documentação',
  documento: 'documento',
  download: 'download',
  economia: 'economia',
  eleitoral: 'eleitoral',
  ferramenta: 'ferramenta',
  fonte: 'fonte',
  historico: 'histórico',
  ibge: 'IBGE',
  institucional: 'institucional',
  jornalistico: 'jornalístico',
  legislativo: 'legislativo',
  licenca: 'licença',
  monitoramento: 'monitoramento',
  municipal: 'municipal',
  noticias: 'notícias',
  oficial: 'oficial',
  opiniao: 'opinião',
  orientacoes: 'orientações',
  painel: 'painel',
  parlamentar: 'parlamentar',
  plataforma: 'plataforma',
  publica: 'pública',
  predefinida: 'predefinida',
  publico: 'público',
  pesquisa: 'pesquisa',
  proveniencia: 'proveniência',
  referencia: 'referência',
  relatorios: 'relatórios',
  repositorio: 'repositório',
  radio: 'rádio',
  saude: 'saúde',
  servico: 'serviço',
  sessoes: 'sessões',
  social: 'social',
  tecnica: 'técnica',
  transparencia: 'transparência',
  terceiros: 'terceiros',
  uf: 'UF',
  uso: 'uso',
  url: 'URL',
};

const lowercaseWords = new Set(['da', 'das', 'de', 'do', 'dos', 'e', 'ou']);
const exactLabels: Record<string, string> = {
  acervo_digital: 'Acervo Digital',
  agregador_terceiros: 'Agregador de Terceiros',
  atas_pautas: 'Atas e Pautas',
  ciencias_sociais: 'Ciências Sociais',
  curadoria: 'Curadoria',
  diario_oficial: 'Diário Oficial',
  download_dados: 'Download de Dados',
  economia_agroambiental: 'Economia Agroambiental',
  ferramenta_ou_servico: 'Ferramenta ou Serviço',
  atas: 'Atas',
  relatorios: 'Relatórios',
  sessoes: 'Sessões',
  original: 'Original',
  painel_transparencia: 'Painel de Transparência',
  pendente: 'Pendente',
  portal_de_noticias: 'Portal de Notícias',
  portal_de_noticias_e_radio: 'Portal de Notícias e Rádio',
  principal: 'Principal',
  pesquisa_de_opiniao: 'Pesquisa de Opinião',
  registro_oficial_de_pesquisa: 'Registro Oficial de Pesquisa',
  saude_publica: 'Saúde Pública',
  sapl: 'SAPL',
  secao_todo: 'Seção do TODO',
  origem_cadastro: 'Origem do Cadastro',
};

export function displayLabel(value: string): string {
  if (exactLabels[value]) return exactLabels[value];
  if (!/^[a-z0-9]+(?:_[a-z0-9]+)*$/.test(value)) return value;

  return value
    .split('_')
    .map((part, index) => {
      const word = words[part] ?? part;
      if (index > 0 && lowercaseWords.has(part)) return word;
      return word.charAt(0).toLocaleUpperCase('pt-BR') + word.slice(1);
    })
    .join(' ');
}

export function displayText(value: string): string {
  return value.replace(
    /https?:\/\/[^\s<>()]+|[a-z0-9]+(?:_[a-z0-9]+)+/gi,
    (token) => (/^https?:\/\//i.test(token) ? token : displayLabel(token)),
  );
}
