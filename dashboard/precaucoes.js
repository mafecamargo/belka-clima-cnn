// Base de eventos e precauções da Belka.
// Texto escrito no tom de voz do manual da marca: frases curtas, um verbo no começo,
// números concretos. Conteúdo baseado nas orientações públicas da Defesa Civil,
// do Corpo de Bombeiros, do INMET e do Ministério da Saúde.

window.BELKA_NIVEIS = {
  fique_de_olho: { nome: "Fique de olho", inmet: "Perigo potencial", resumo: "Acompanhe as atualizações e evite riscos desnecessários." },
  prepare_se:    { nome: "Prepare-se",    inmet: "Perigo",           resumo: "Separe documentos, remédios e água. Combine com a família onde se encontrar." },
  aja_agora:     { nome: "Aja agora",     inmet: "Grande perigo",    resumo: "Saia da área de risco e vá para o ponto de apoio mais próximo." },
  depois:        { nome: "Depois que passar", inmet: null,           resumo: "Volte com cuidado e só quando for seguro." }
};

window.BELKA_EVENTOS = {
  enchente: {
    nome: "Enchente e alagamento",
    oque: "Chuva forte faz ruas alagarem e rios ou córregos subirem acima do normal.",
    sinais: ["Chuva forte por mais de 1 hora", "Água subindo rápido na rua ou no córrego", "Bueiros devolvendo água"],
    fique_de_olho: [
      "Acompanhe os avisos do INMET e da Defesa Civil da sua cidade.",
      "Limpe calhas e ralos e não deixe lixo perto de bueiros.",
      "Combine com a família um ponto de encontro em lugar alto."
    ],
    prepare_se: [
      "Coloque documentos, remédios e eletrônicos no alto, dentro de sacos plásticos.",
      "Separe água potável, lanterna e carregador para 1 dia.",
      "Tire o carro de ruas que costumam alagar.",
      "Saiba onde fica o abrigo ou a escola mais próxima em área alta."
    ],
    aja_agora: [
      "Saia de casa se a água começar a entrar. Vá para um lugar alto.",
      "Desligue a energia no quadro geral e feche o gás antes de sair.",
      "Não atravesse água em movimento, nem a pé nem de carro: 30 cm de água já arrastam um veículo.",
      "Fique longe de postes e fios caídos. Ligue 199 (Defesa Civil) ou 193 (Bombeiros)."
    ],
    depois: [
      "Só volte para casa quando a Defesa Civil liberar.",
      "Não use água da enchente nem alimentos que ela tocou.",
      "Lave e desinfete a casa de botas e luvas: a lama pode transmitir leptospirose.",
      "Procure um posto de saúde se tiver febre e dor no corpo nos 30 dias seguintes."
    ]
  },
  deslizamento: {
    nome: "Deslizamento de terra",
    oque: "Encostas encharcadas pela chuva perdem a firmeza e a terra desce.",
    sinais: ["Rachaduras novas em paredes ou no chão", "Árvores, postes ou muros inclinando", "Água barrenta brotando do barranco", "Estalos e portas ou janelas emperrando"],
    fique_de_olho: [
      "Observe o terreno todos os dias em época de chuva.",
      "Não jogue lixo nem entulho na encosta e não corte o barranco.",
      "Descubra com a Defesa Civil qual é a rota de fuga e o ponto de apoio do seu bairro."
    ],
    prepare_se: [
      "Deixe uma mochila pronta com documentos, remédios, água e lanterna.",
      "Combine com vizinhos um jeito de avisar uns aos outros, inclusive à noite.",
      "Durma no cômodo mais distante do barranco enquanto a chuva durar.",
      "Leve antes para a casa de parentes quem tem dificuldade de andar."
    ],
    aja_agora: [
      "Saia de casa agora se notar rachaduras, estalos ou terra descendo.",
      "Avise os vizinhos no caminho e vá para o ponto de apoio.",
      "Não volte para buscar objetos.",
      "Ligue 199 (Defesa Civil) ou 193 (Bombeiros)."
    ],
    depois: [
      "Não volte para casa até a Defesa Civil vistoriar o local.",
      "Fique longe da área atingida: outro deslizamento pode acontecer.",
      "Ajude a informar quem está desaparecido às equipes de resgate."
    ]
  },
  incendio: {
    nome: "Incêndio e queimada",
    oque: "Tempo seco, calor e vento fazem o fogo se espalhar rápido pela vegetação.",
    sinais: ["Fumaça ou cheiro de queimado", "Vários dias sem chuva e umidade do ar baixa", "Vento forte perto de mato seco"],
    fique_de_olho: [
      "Não queime lixo, folhas nem pasto. Além de perigoso, é crime ambiental.",
      "Não jogue bituca de cigarro na estrada ou no mato.",
      "Mantenha o terreno em volta da casa limpo, sem mato seco."
    ],
    prepare_se: [
      "Faça um aceiro: uma faixa de 3 metros sem vegetação em volta da casa.",
      "Deixe mangueira e baldes com água à mão.",
      "Separe documentos e remédios e combine a rota de saída com a família.",
      "Feche portas e janelas se a fumaça chegar."
    ],
    aja_agora: [
      "Saia da área no sentido contrário ao do vento e da fumaça.",
      "Ligue 193 (Bombeiros). Não tente apagar um fogo grande sozinho.",
      "Cubra nariz e boca com um pano úmido.",
      "Na estrada com fumaça, reduza a velocidade, acenda o farol baixo e não pare na pista."
    ],
    depois: [
      "Só volte quando os Bombeiros liberarem a área.",
      "Cuidado com brasas escondidas: elas reacendem o fogo.",
      "Procure atendimento se tiver falta de ar, tosse forte ou ardência nos olhos."
    ]
  },
  tempestade: {
    nome: "Tempestade com raios",
    oque: "Chuva forte com raios, trovões e rajadas de vento, às vezes com granizo.",
    sinais: ["Céu escurecendo rápido", "Trovões cada vez mais próximos", "Vento que muda de repente"],
    fique_de_olho: [
      "Confira a previsão antes de sair ou de marcar atividades ao ar livre.",
      "Carregue o celular e deixe uma lanterna à mão.",
      "Recolha objetos soltos do quintal e da varanda."
    ],
    prepare_se: [
      "Vá para um lugar fechado assim que ouvir o primeiro trovão.",
      "Tire aparelhos eletrônicos da tomada.",
      "Saia da piscina, do mar, do rio e de campos abertos."
    ],
    aja_agora: [
      "Fique dentro de casa ou do carro, com portas e janelas fechadas.",
      "Não se abrigue debaixo de árvores nem perto de postes, cercas e torres.",
      "Não use chuveiro elétrico nem telefone com fio durante os raios.",
      "Em campo aberto sem abrigo, agache com os pés juntos. Não deite no chão."
    ],
    depois: [
      "Espere 30 minutos depois do último trovão para sair.",
      "Não toque em fios caídos. Avise a companhia de energia.",
      "Se alguém for atingido por raio, ligue 192 (SAMU): a pessoa pode ser tocada e socorrida."
    ]
  },
  vendaval: {
    nome: "Vendaval e tornado",
    oque: "Rajadas de vento fortes derrubam árvores, destelham casas e lançam objetos.",
    sinais: ["Rajadas que balançam árvores inteiras", "Objetos sendo arrastados", "Nuvem escura em forma de funil"],
    fique_de_olho: [
      "Recolha vasos, lonas e objetos soltos de quintais e varandas.",
      "Verifique se telhas e antenas estão bem presas.",
      "Não estacione debaixo de árvores, placas ou andaimes."
    ],
    prepare_se: [
      "Feche bem portas e janelas e fique longe dos vidros.",
      "Escolha o cômodo mais protegido da casa, de preferência um banheiro ou corredor sem janelas.",
      "Carregue o celular: pode faltar energia."
    ],
    aja_agora: [
      "Fique dentro de casa, no cômodo mais interno e longe de janelas.",
      "Na rua, entre em uma construção firme. Não se abrigue debaixo de árvores, marquises frágeis ou placas.",
      "No carro, pare em local aberto, longe de árvores e postes.",
      "Se o telhado ceder, proteja a cabeça debaixo de uma mesa resistente."
    ],
    depois: [
      "Não toque em fios caídos e avise a companhia de energia.",
      "Cuidado com galhos e telhas soltas que ainda podem cair.",
      "Ligue 199 (Defesa Civil) se a casa tiver danos na estrutura."
    ]
  },
  granizo: {
    nome: "Granizo",
    oque: "Pedras de gelo caem junto com a tempestade e podem ferir pessoas e quebrar telhas.",
    sinais: ["Tempestade forte com queda rápida de temperatura", "Barulho de pedras batendo no telhado"],
    fique_de_olho: [
      "Guarde o carro em local coberto quando houver aviso de tempestade.",
      "Recolha animais e plantas sensíveis."
    ],
    prepare_se: [
      "Fique em local coberto por telhado firme ou laje.",
      "Afaste-se de janelas, claraboias e telhas de vidro ou fibra."
    ],
    aja_agora: [
      "Não saia enquanto o granizo estiver caindo.",
      "Na rua, proteja a cabeça e entre na construção mais próxima.",
      "No carro, pare em local seguro e fique de costas para os vidros."
    ],
    depois: [
      "Veja se há telhas quebradas antes da próxima chuva.",
      "Cuidado ao andar: o chão fica escorregadio.",
      "Ligue 199 (Defesa Civil) se o telhado foi muito danificado."
    ]
  },
  calor: {
    nome: "Onda de calor",
    oque: "Vários dias seguidos com temperatura bem acima do normal para a época.",
    sinais: ["Temperatura 5 °C ou mais acima da média por vários dias", "Noites que não refrescam"],
    fique_de_olho: [
      "Beba água ao longo do dia, mesmo sem sede.",
      "Use roupas leves e claras, chapéu e protetor solar.",
      "Evite o sol entre 10h e 16h."
    ],
    prepare_se: [
      "Deixe a casa ventilada e feche cortinas do lado em que bate sol.",
      "Ligue ou visite idosos, pessoas doentes e quem mora sozinho.",
      "Deixe atividade física pesada para o começo da manhã ou a noite.",
      "Ofereça água a crianças e idosos a cada hora."
    ],
    aja_agora: [
      "Fique em local fresco e na sombra nas horas mais quentes.",
      "Nunca deixe crianças, idosos ou animais dentro de carro fechado.",
      "Refresque o corpo com banho ou panos úmidos.",
      "Ligue 192 (SAMU) se alguém tiver confusão mental, pele muito quente, desmaio ou convulsão."
    ],
    depois: [
      "Continue bebendo bastante água por alguns dias.",
      "Procure um posto de saúde se o cansaço, a tontura ou a dor de cabeça não passarem."
    ]
  },
  seca: {
    nome: "Seca e baixa umidade",
    oque: "Muitos dias sem chuva deixam o ar seco, o que afeta a respiração e aumenta o risco de fogo.",
    sinais: ["Umidade do ar abaixo de 30%", "Lábios, olhos e nariz ressecados", "Vegetação seca e poeira no ar"],
    fique_de_olho: [
      "Beba bastante água ao longo do dia.",
      "Evite exercício ao ar livre entre 10h e 16h.",
      "Use água com consciência: conserte vazamentos e reduza o tempo de banho."
    ],
    prepare_se: [
      "Umedeça o ambiente com toalha molhada ou bacia de água no quarto.",
      "Use soro fisiológico no nariz e nos olhos se estiverem ressecados.",
      "Guarde água potável para alguns dias se houver risco de racionamento.",
      "Não queime lixo nem mato: o fogo se espalha muito rápido no tempo seco."
    ],
    aja_agora: [
      "Suspenda atividades físicas ao ar livre quando a umidade ficar abaixo de 12%.",
      "Fique em locais protegidos do sol e mantenha crianças e idosos hidratados.",
      "Procure atendimento se tiver falta de ar ou sangramento no nariz que não para.",
      "Ligue 193 (Bombeiros) ao ver foco de incêndio."
    ],
    depois: [
      "Mantenha os hábitos de economia de água até os reservatórios se recuperarem."
    ]
  },
  frio: {
    nome: "Frio, geada e neve",
    oque: "Queda forte de temperatura, com risco para a saúde, para quem vive na rua e para as plantações.",
    sinais: ["Aviso de frente fria ou massa de ar polar", "Temperatura perto de 0 °C ao amanhecer"],
    fique_de_olho: [
      "Vista-se em camadas e proteja mãos, pés e cabeça.",
      "Tome bebidas quentes e mantenha a alimentação em dia.",
      "Proteja plantas sensíveis e leve os animais para local abrigado."
    ],
    prepare_se: [
      "Separe cobertores e agasalhos extras para a noite.",
      "Veja como estão idosos, bebês e vizinhos que moram sozinhos.",
      "Avise a assistência social da sua cidade se vir alguém dormindo na rua."
    ],
    aja_agora: [
      "Fique em local aquecido e evite sair de madrugada.",
      "Nunca use fogareiro, carvão ou aquecedor a gás em ambiente fechado: o gás que eles soltam pode matar.",
      "Na estrada com geada ou neve, reduza a velocidade e aumente a distância do carro da frente.",
      "Ligue 192 (SAMU) se alguém estiver com tremores fortes, fala enrolada ou muita sonolência."
    ],
    depois: [
      "Continue se agasalhando: as manhãs seguintes ainda costumam ser frias.",
      "Procure um posto de saúde se tiver febre ou falta de ar."
    ]
  }
};

// Classe que a CNN devolve -> evento da base de precauções
window.BELKA_CLASSE_PARA_EVENTO = {
  enchente: "enchente", deslizamento: "deslizamento", incendio: "incendio", tempestade: "tempestade",
  tornado: "vendaval", seca: "seca", neve: "frio", granizo: "granizo", calor: "calor"
};
