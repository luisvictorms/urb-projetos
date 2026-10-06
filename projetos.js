// Catálogo de projetos. Para adicionar um programa/evento novo, copie um bloco e ajuste.
// marca: URBNEWS | FUTEBORA   tipo: Programa | Evento   status: Ativo | Em produção | Encerrado
// url: página do projeto (pasta neste site, ex. 'sts26/', ou link externo)
// capa: imagem 16:9   itens: o que o pacote tem (aparece como etiquetas)
window.MARCAS = [
  { id: 'URBNEWS', nome: 'urb.NEWS', cor: '#426fd6', desc: 'Jornalismo e coberturas especiais do Grupo Urbmídia.' },
  { id: 'FUTEBORA', nome: 'FUTEBORA', cor: '#01fd5f', desc: 'Futebol cearense: programas, jogos e conteúdo de arquibancada.' },
];

window.PROJETOS = [
  {
    marca: 'URBNEWS', tipo: 'Evento', nome: 'Siará Tech Summit ‘26', status: 'Ativo', ano: 2026,
    url: 'sts26/', capa: 'sts26/img/tela-comecaremos-dia1.png',
    resumo: 'Cobertura ao vivo em 3 dias: telas, mosquito, Inscreva-se e tarjas controladas pelo celular.',
    itens: ['vMix', 'Controle remoto', 'Tarjas', 'Telas', '3 dias'],
  },
  {
    marca: 'URBNEWS', tipo: 'Evento', nome: 'Eleições 2026', status: 'Ativo', ano: 2026,
    url: 'https://luisvictorms.github.io/urbnews-apuracao/estudio.html', capa: 'capas/eleicoes-2026.jpg',
    resumo: 'Apuração ao vivo do TSE, vencedores, pesquisas, tarjas vMix e OOH em vários formatos.',
    itens: ['vMix', 'Apuração TSE', 'Pesquisas', 'OOH', 'Redes'],
  },
];
