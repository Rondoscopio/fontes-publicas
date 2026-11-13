export type InstitutionalPage = 'sobre' | 'legal' | 'creditos';

const pageMetadata: Record<
  InstitutionalPage,
  {
    title: string;
    description: string;
    eyebrow: string;
    heading: string;
    lead: string;
  }
> = {
  sobre: {
    title: 'Sobre o catálogo · Rondoscópio',
    description:
      'Conheça o propósito, o escopo e os limites do catálogo OSINT Rondônia.',
    eyebrow: 'O projeto',
    heading: 'Sobre o catálogo',
    lead: 'O OSINT Rondônia reúne fontes públicas, ferramentas e referências para pesquisa, jornalismo, investigação e fiscalização cidadã.',
  },
  legal: {
    title: 'Informações legais e privacidade · Rondoscópio',
    description:
      'Licenças, condições de uso, limitações e informações de privacidade do catálogo OSINT Rondônia.',
    eyebrow: 'Transparência',
    heading: 'Informações legais',
    lead: 'Licenças, limites do catálogo e funcionamento da interface.',
  },
  creditos: {
    title: 'Créditos e proveniência · Rondoscópio',
    description:
      'Créditos do projeto, dados territoriais, proveniência e software do catálogo OSINT Rondônia.',
    eyebrow: 'Atribuição',
    heading: 'Créditos',
    lead: 'Quem mantém o projeto e de onde vêm os dados de referência.',
  },
};

export function createInstitutionalViewModel(page: InstitutionalPage) {
  return pageMetadata[page];
}
