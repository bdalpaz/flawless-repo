const characterImages = {
    "Scorpion": "assets/images/personagens/scorpion.png",
    "Sub-Zero": "assets/images/personagens/subzeroatualizado.png",
    "Liu Kang": "assets/images/personagens/liukang.png",
    "Raiden": "assets/images/personagens/raiden.png",
    "Johnny Cage": "assets/images/personagens/johnnycage.png",
    "Sonya Blade": "assets/images/personagens/sonya.png",
    "Kitana": "assets/images/personagens/kitana.png",
    "Jax Briggs": "assets/images/personagens/jax.png",
    "Mileena": "assets/images/personagens/mileena.png",
    "Kano": "assets/images/personagens/kano.png",
    "Baraka": "assets/images/personagens/barakac.png",
    "Shang Tsung": "assets/images/personagens/shang.png",
    "Shao Kahn": "assets/images/personagens/shao.png",
    "Ermac": "assets/images/personagens/emerc.png",
    "Reptile": "assets/images/personagens/reptile.png",
    "Smoke": "assets/images/personagens/smoke.png",
    "Noob Saibot": "assets/images/personagens/noob.png",
    "Goro": "assets/images/personagens/goro.png",
    "Kintaro": "assets/images/personagens/kintaro.png",
    "Motaro": "assets/images/personagens/motaro.png",
    "Bo' Rai Cho": "assets/images/personagens/boraicho.png",
    "Cassie Cage": "assets/images/personagens/cassiecage.png",
    "Cetrion": "assets/images/personagens/cetrion.png",
    "Cyrax": "assets/images/personagens/cyrax.png",
    "D'Vorah": "assets/images/personagens/dvorah.png",
    "Erron Black": "assets/images/personagens/erron.png",
    "Fujin": "assets/images/personagens/fujin.png",
    "Geras": "assets/images/personagens/geras.png",
    "Jacqui Briggs": "assets/images/personagens/jacqui.png",
    "Jade": "assets/images/personagens/jade.png",
    "Kabal": "assets/images/personagens/kabal.png",
    "Kenshi": "assets/images/personagens/kenshi.png",
    "Kollector": "assets/images/personagens/kollector.png",
    "Kotal Kahn": "assets/images/personagens/kotal.png",
    "Kung Lao": "assets/images/personagens/kunglao.png",
    "Nightwolf": "assets/images/personagens/nightwolf.png",
    "Onaga": "assets/images/personagens/onaga.png",
    "Quan Chi": "assets/images/personagens/quanchi.png",
    "Rain": "assets/images/personagens/rain.png",
    "Sektor": "assets/images/personagens/sektor.png",
    "Sheeva": "assets/images/personagens/sheeva.png",
    "Shinnok": "assets/images/personagens/shinnok.jpg",
    "Shujinko": "assets/images/personagens/shujinco.webp", 
    "Sindel": "assets/images/personagens/sindel.png",
    "Skarlet": "assets/images/personagens/skarlet.png",
    "Stryker": "assets/images/personagens/stryker.png",
    "Takeda Takahashi": "assets/images/personagens/takeda.png",
    "Tanya": "assets/images/personagens/tanya.png",
    "Triborg": "assets/images/personagens/triborg.png",
};

// Mapeamento de imagens dos jogos (local)
const gameImages = {
    "Mortal Kombat": "assets/images/jogos/jogo1992.png",
    "Mortal Kombat II": "assets/images/jogos/jogo1993.png",
    "Mortal Kombat 3": "assets/images/jogos/jogo1995.png",
    "Ultimate Mortal Kombat 3": "assets/images/jogos/jogo1995U.png",
    "Mortal Kombat Trilogy": "assets/images/jogos/jogo1996.png",
    "Mortal Kombat 4": "assets/images/jogos/jogo1997.png",
    "Mortal Kombat: Deadly Alliance": "assets/images/jogos/jogo2002.png",
    "Mortal Kombat: Deception": "assets/images/jogos/jogo2004.png",
    "Mortal Kombat: Armageddon": "assets/images/jogos/jogo2006.png",
    "Mortal Kombat vs DC Universe": "assets/images/jogos/jogo2008.png",
    "Mortal Kombat (MK9)": "assets/images/jogos/jogo2011.png",
    "Mortal Kombat X": "assets/images/jogos/jogo2015.png",
    "Mortal Kombat 11": "assets/images/jogos/jogo2019.png",
    "Mortal Kombat 1 (MK1)": "assets/images/jogos/jogo2023.png",
};

// Variáveis de estado para a paginação de personagens
let currentOffset = 0;
const limitPerPage = 8; 

// Elementos DOM para os personagens
const charactersGrid = document.querySelector('#personagens .grid'); 
const showMoreCharsButton = document.getElementById('showMoreChars');

// Variáveis de estado para a paginação de fatalities
let currentOffsetFatalities = 0;
const limitPerPageFatalities = 3; 

// Elementos DOM para os fatalities
const fatalitiesLista = document.getElementById('fatalities-lista');
const showMoreFatalitiesButton = document.getElementById('showMoreFatalities');

// Variáveis de estado para a paginação de armas
let currentOffsetArmas = 0;
const limitPerPageArmas = 6; 

// Elementos DOM para as armas
const armasLista = document.getElementById('armas-lista');
const showMoreArmasButton = document.getElementById('showMoreArmas');


console.log('Script.js carregado!'); 

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded disparado!'); 

    // Carregar os primeiros elementos ao carregar a página
    carregarKombatants(true); 
    carregarJogosTimeline();
    carregarFatalities(true);
    carregarArmas(true); 

    setupModal();

    // Efeito de digitação no título
    const titleElement = document.querySelector('h1');
    if (titleElement) {
        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        let i = 0;
        const typingEffect = setInterval(() => {
            if (i < originalText.length) {
                titleElement.textContent += originalText.charAt(i);
                i++;
            } else {
                clearInterval(typingEffect);
            }
        }, 100);
    }

    // Suavizar scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Event Listener para o botão "Mostrar Mais Personagens"
    if (showMoreCharsButton) { 
        showMoreCharsButton.addEventListener('click', function() {
            carregarKombatants(false); 
        });
    } else {
        console.warn('showMoreCharsButton NÃO foi encontrado. Verifique o ID no HTML.');
    }

    // Event Listener para o botão "Mostrar Mais Fatalities"
    if (showMoreFatalitiesButton) {
        showMoreFatalitiesButton.addEventListener('click', function() {
            carregarFatalities(false);
        });
    } else {
        console.warn('showMoreFatalitiesButton NÃO foi encontrado. Verifique o ID no HTML.');
    }

    // Event Listener para o botão "Mostrar Mais Armas"
    if (showMoreArmasButton) {
        showMoreArmasButton.addEventListener('click', function() {
            carregarArmas(false);
        });
    } else {
        console.warn('showMoreArmasButton NÃO foi encontrado. Verifique o ID no HTML.');
    }
});


// --- Funções de Carregamento de Dados ---

async function carregarKombatants(isInitialLoad) {
    if (isInitialLoad) {
        currentOffset = 0; 
        charactersGrid.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Kombatants...</p>';
        if (showMoreCharsButton) {
            showMoreCharsButton.style.display = 'none'; 
        }
    } else {
        if (showMoreCharsButton) {
            showMoreCharsButton.disabled = true;
            showMoreCharsButton.innerHTML = 'CARREGANDO... <i class="fas fa-spinner fa-spin ml-2"></i>';
        }
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/personagens?limit=${limitPerPage}&offset=${currentOffset}`);
        if (!response.ok) {
            throw new Error(`Erro ao buscar personagens: ${response.statusText}`);
        }
        const data = await response.json(); 
        const personagens = data.personagens;
        const totalPersonagens = data.total;

        if (isInitialLoad) {
            charactersGrid.innerHTML = ''; 
        }

        if (personagens.length === 0 && isInitialLoad) {
            charactersGrid.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhum personagem encontrado.</p>';
            if (showMoreCharsButton) {
                showMoreCharsButton.style.display = 'none'; 
            }
            return;
        } else if (personagens.length === 0 && !isInitialLoad) {
            if (showMoreCharsButton) {
                showMoreCharsButton.style.display = 'none'; 
            }
            return;
        }

        personagens.forEach(personagem => {
            const card = document.createElement('div');
            card.className = 'character-card bg-gray-800 rounded-lg overflow-hidden border border-red-900 cursor-pointer transition duration-300';
            
            const imageUrl = characterImages[personagem.nome] || 'assets/images/placeholder-personagem.png'; 

            card.innerHTML = `
                <div class="h-48 md:h-56 overflow-hidden">
                    <img src="${imageUrl}" 
                        alt="${personagem.nome}" 
                        class="w-full h-full object-cover">
                </div>
                <div class="p-4">
                    <h3 class="text-xl font-bold blood-text">${personagem.nome}</h3>
                    ${personagem.habilidade_principal ? `<p class="text-red-400 text-sm mt-1 mb-2">Habilidade: ${personagem.habilidade_principal}</p>` : ''} 
                    <p class="text-gray-400 text-sm mt-2">Raça: ${personagem.raca || 'N/A'}</p>
                    <p class="text-gray-400 text-sm">Status: ${personagem.status_vida || 'N/A'}</p> 
                    ${personagem.origem ? `<p class="text-gray-400 text-sm">Origem: ${personagem.origem}</p>` : ''}
                    ${personagem.alinhamento ? `<p class="text-gray-400 text-sm">Alinhamento: ${personagem.alinhamento}</p>` : ''}
                    ${personagem.nome_mundo ? `<p class="text-gray-400 text-sm">Mundo: ${personagem.nome_mundo}${personagem.tipo_mundo ? ` (${personagem.tipo_mundo})` : ''}</p>` : ''}
                
                </div>
            `;
            card.addEventListener('click', () => openCharacterModal(personagem.id));
            charactersGrid.appendChild(card);
        });

        currentOffset += personagens.length;

        if (showMoreCharsButton) { 
            if (currentOffset < totalPersonagens) {
                showMoreCharsButton.style.display = 'block'; 
                showMoreCharsButton.disabled = false;
                showMoreCharsButton.innerHTML = 'MOSTRAR MAIS PERSONAGENS <i class="fas fa-chevron-down ml-2"></i>';
            } else {
                showMoreCharsButton.style.display = 'none'; 
            }
        }

    } catch (error) {
        console.error('Erro ao carregar Kombatants:', error);
        charactersGrid.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar personagens: ${error.message}</p>`;
        if (showMoreCharsButton) {
            showMoreCharsButton.style.display = 'none'; 
        }
    }
}

async function carregarJogosTimeline() {
    const timelineContainer = document.querySelector('#jogos .space-y-12'); 
    timelineContainer.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Linha do Tempo...</p>';

    try {
        const response = await fetch('http://127.0.0.1:5000/api/jogos'); 
        if (!response.ok) {
            throw new Error(`Erro ao buscar jogos: ${response.statusText}`);
        }
        const jogos = await response.json(); 
        
        timelineContainer.innerHTML = ''; 

        if (jogos.length === 0) {
            timelineContainer.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhum jogo encontrado.</p>';
            return;
        }

        jogos.forEach((jogo, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('relative', 'md:flex', 'justify-between', 'items-center', 'mb-16', 'timeline-item');

            const isEven = index % 2 === 0; 
            
            const imageUrl = gameImages[jogo.titulo] || 'assets/images/placeholder-jogo.png'; // Fallback local

            itemDiv.innerHTML = `
                <div class="md:w-5/12 md:pr-8 ${isEven ? 'text-right' : 'order-last text-left'} mb-4 md:mb-0">
                    <h3 class="text-2xl font-bold blood-text">${jogo.titulo} (${jogo.ano || 'N/A'})</h3>
                    <p class="text-gray-300">Plataformas: ${jogo.plataforma || 'N/A'}</p>
                </div>
                <div class="hidden md:block w-2 h-2 rounded-full bg-red-600 mx-auto"></div>
                <div class="md:w-5/12 md:pl-8 ${isEven ? '' : 'order-first'}">
                    <img src="${imageUrl}" 
                        alt="${jogo.titulo}" 
                        class="w-full max-w-xs mx-auto rounded border border-red-900">
                </div>
            `;
            timelineContainer.appendChild(itemDiv);

            const circle = document.createElement('div');
            circle.className = 'hidden md:block w-3 h-3 rounded-full bg-red-600 absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2';
            itemDiv.appendChild(circle);
        });

    } catch (error) {
        console.error('Erro ao carregar Linha do Tempo:', error);
        timelineContainer.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar jogos: ${error.message}</p>`;
    }
}
async function carregarFatalities(isInitialLoad) {
    if (isInitialLoad) {
        currentOffsetFatalities = 0;
        fatalitiesLista.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Fatalities...</p>';
        if (showMoreFatalitiesButton) {
            showMoreFatalitiesButton.style.display = 'none';
        }
    } else {
        if (showMoreFatalitiesButton) {
            showMoreFatalitiesButton.disabled = true;
            showMoreFatalitiesButton.innerHTML = 'CARREGANDO... <i class="fas fa-spinner fa-spin ml-2"></i>';
        }
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/fatalities?limit=${limitPerPageFatalities}&offset=${currentOffsetFatalities}`);
        if (!response.ok) {
            throw new Error(`Erro ao buscar fatalities: ${response.statusText}`);
        }
        const data = await response.json();
        const fatalities = data.fatalities;
        const totalFatalities = data.total;

        if (isInitialLoad) {
            fatalitiesLista.innerHTML = ''; 
        }

        if (fatalities.length === 0 && isInitialLoad) {
            fatalitiesLista.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhum Fatality encontrado.</p>';
            if (showMoreFatalitiesButton) {
                showMoreFatalitiesButton.style.display = 'none';
            }
            return;
        } else if (fatalities.length === 0 && !isInitialLoad) {
            if (showMoreFatalitiesButton) {
                showMoreFatalitiesButton.style.display = 'none';
            }
            return;
        }

        fatalities.forEach(fatality => {
            const card = document.createElement('div');
            card.className = 'bg-gray-800 rounded-lg p-3 shadow-lg border border-red-700 w-5/5'; 
            card.innerHTML = `
                <h3 class="text-xl font-bold blood-text mb-2">${fatality.nome || 'N/A'}</h3> 
                <p class="text-gray-300 text-sm mb-2">Tipo: ${fatality.tipo || 'N/A'}</p> <p class="text-gray-300 text-sm mb-2">Brutalidade: ${fatality.brutalidade || 'N/A'}</p> <p class="text-gray-300 text-sm">Origem: ${fatality.origem || 'N/A'}</p> 
            `;
            fatalitiesLista.appendChild(card);
        });

        currentOffsetFatalities += fatalities.length;

        if (showMoreFatalitiesButton) {
            if (currentOffsetFatalities < totalFatalities) {
                showMoreFatalitiesButton.style.display = 'block';
                showMoreFatalitiesButton.disabled = false;
                showMoreFatalitiesButton.innerHTML = 'MOSTRAR MAIS FATALITIES <i class="fas fa-chevron-down ml-2"></i>';
            } else {
                showMoreFatalitiesButton.style.display = 'none';
            }
        }

    } catch (error) {
        console.error('Erro ao carregar Fatalities:', error);
        fatalitiesLista.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar fatalities: ${error.message}</p>`;
        if (showMoreFatalitiesButton) {
            showMoreFatalitiesButton.style.display = 'none';
        }
    }
}

async function carregarArmas(isInitialLoad) {
    console.log('Função carregarArmas chamada. isInitialLoad:', isInitialLoad); // DEBUG
    if (isInitialLoad) {
        currentOffsetArmas = 0;
        if (armasLista) { // Verificação para evitar erro de null
            armasLista.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Armas...</p>';
        } else {
            console.error('Elemento "armas-lista" não encontrado. Verifique o ID no HTML.'); // DEBUG
            return; // Sai da função se o elemento não for encontrado
        }
        if (showMoreArmasButton) {
            showMoreArmasButton.style.display = 'none';
        }
    } else {
        if (showMoreArmasButton) {
            showMoreArmasButton.disabled = true;
            showMoreArmasButton.innerHTML = 'CARREGANDO... <i class="fas fa-spinner fa-spin ml-2"></i>';
        }
    }

    try {
        const url = `http://127.0.0.1:5000/api/armas?limit=${limitPerPageArmas}&offset=${currentOffsetArmas}`;
        console.log('Requisição Armas URL:', url); // DEBUG
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erro ao buscar armas: ${response.statusText}`);
        }
        const data = await response.json();
        const armas = data.armas;
        const totalArmas = data.total;

        console.log('Dados de Armas recebidos:', data); // DEBUG
        console.log('Armas recebidas na carga:', armas.length); // DEBUG
        console.log('Total de armas no DB:', totalArmas); // DEBUG

        if (isInitialLoad) {
            armasLista.innerHTML = ''; 
        }

        if (armas.length === 0 && isInitialLoad) {
            armasLista.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhuma Arma encontrada.</p>';
            if (showMoreArmasButton) {
                showMoreArmasButton.style.display = 'none';
            }
            return;
        } else if (armas.length === 0 && !isInitialLoad) {
            if (showMoreArmasButton) {
                showMoreArmasButton.style.display = 'none';
            }
            return;
        }

        armas.forEach(arma => {
            const card = document.createElement('div');
            card.className = 'bg-gray-800 rounded-lg p-4 shadow-lg border border-yellow-500 w-5/7'; 
            card.innerHTML = `
                <h3 class="text-xl font-bold text-yellow-400 mb-2">${arma.nome || 'N/A'}</h3>
                <p class="text-gray-300 text-sm mb-1">Tipo: ${arma.tipo || 'N/A'}</p>
                <p class="text-gray-300 text-sm mb-1">Raridade: ${arma.raridade || 'N/A'}</p>
                <p class="text-gray-300 text-sm mb-1">Alcance: ${arma.alcance || 'N/A'}</p>
                <p class="text-gray-300 text-sm">Dano: ${arma.dano || 'N/A'}</p>
            `;
            armasLista.appendChild(card);
        });

        currentOffsetArmas += armas.length;

        if (showMoreArmasButton) {
            if (currentOffsetArmas < totalArmas) {
                showMoreArmasButton.style.display = 'block';
                showMoreArmasButton.disabled = false;
                showMoreArmasButton.innerHTML = 'MOSTRAR MAIS ARMAS <i class="fas fa-chevron-down ml-2"></i>';
            } else {
                showMoreArmasButton.style.display = 'none';
            }
        }

    } catch (error) {
        console.error('Erro ao carregar Armas:', error);
        if (armasLista) { 
            armasLista.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar armas: ${error.message}</p>`;
        }
        if (showMoreArmasButton) {
            showMoreArmasButton.style.display = 'none';
        }
    }
}

// --- Lógica do Modal de Personagem ---

function setupModal() {
    const modal = document.getElementById('characterModal');
    const closeModalBtn = document.getElementById('closeModal');
    const modalContent = modal.querySelector('.modal-content');

    closeModalBtn.addEventListener('click', () => {
        modalContent.classList.remove('scale-100', 'opacity-100');
        modalContent.classList.add('scale-95', 'opacity-0');
        setTimeout(() => modal.classList.add('hidden'), 300);
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modalContent.classList.remove('scale-100', 'opacity-100');
            modalContent.classList.add('scale-95', 'opacity-0');
            setTimeout(() => modal.classList.add('hidden'), 300);
        }
    });
}

async function openCharacterModal(id_personagem) {
    const modal = document.getElementById('characterModal');
    const modalContent = modal.querySelector('.modal-content');
    const modalImage = document.getElementById('modalCharacterImage');
    const modalName = document.getElementById('modalCharacterName');
    const modalBio = document.getElementById('modalCharacterBio');
    const modalRaceOriginAlign = document.getElementById('modalRaceOriginAlign');
    const modalAgeStatus = document.getElementById('modalAgeStatus');
    const modalCla = document.getElementById('modalCla');
    const modalMundo = document.getElementById('modalMundo');
    const modalArma = document.getElementById('modalArma');
    const modalTransformacao = document.getElementById('modalTransformacao');
    const modalMoves = document.getElementById('modalCharacterMoves');
    const modalFatality = document.getElementById('modalCharacterFatality');


// Limpa conteúdo antigo
    modalImage.src = '';
    modalName.textContent = 'Carregando...';
    modalBio.textContent = '';
    modalRaceOriginAlign.textContent = '';
    modalAgeStatus.textContent = '';
    modalCla.textContent = '';
    modalMundo.textContent = '';
    modalArma.textContent = '';
    modalTransformacao.textContent = '';
    modalMoves.innerHTML = '<li>Carregando habilidade principal...</li>';
    modalFatality.textContent = 'Carregando fatality...';
    modal.classList.remove('hidden');

    setTimeout(() => {
        modalContent.classList.remove('scale-95', 'opacity-0');
        modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);

try {
        const response = await fetch(`http://127.0.0.1:5000/api/personagens/${id_personagem}`);
        if (!response.ok) {
            throw new Error(`Erro ao buscar detalhes do personagem: ${response.statusText}`);
        }
        const characterData = await response.json();


        const imageUrl = characterImages[characterData.nome] || 'https://via.placeholder.com/250x300/333/666?text=Image+Missing';
        modalImage.src = imageUrl;
        modalImage.alt = characterData.nome;
        modalName.textContent = characterData.nome;

        modalRaceOriginAlign.innerHTML = `<span class="font-bold">Raça:</span> ${characterData.raca || 'N/A'} | <span class="font-bold">Origem:</span> ${characterData.origem || 'N/A'} | <span class="font-bold">Alinhamento:</span> ${characterData.alinhamento || 'N/A'}`;
        modalAgeStatus.innerHTML = `<span class="font-bold">Idade:</span> ${characterData.idade || 'N/A'} | <span class="font-bold">Status:</span> ${characterData.status_vida || 'N/A'}`;

        if (characterData.nome_cla) {
            modalCla.innerHTML = `<span class="font-bold">Clã:</span> ${characterData.nome_cla || 'N/A'} ${characterData.simbolo_cla ? `<img src="https://example.com/assets/${characterData.simbolo_cla}" alt="Símbolo" class="inline-block h-6 ml-2">` : ''}`;
        } else {
            modalCla.textContent = 'Clã: N/A';
        }

        if (characterData.nome_mundo) {
            modalMundo.innerHTML = `<span class="font-bold">Mundo:</span> ${characterData.nome_mundo || 'N/A'} (${characterData.tipo_mundo || 'N/A'})`;
        } else {
            modalMundo.textContent = 'Mundo: N/A';
        }


        if (characterData.nome_arma) {
            modalArma.innerHTML = `<span class="font-bold">Arma:</span> ${characterData.nome_arma || 'N/A'} (Tipo: ${characterData.tipo_arma || 'N/A'}, Dano: ${characterData.dano_arma || 'N/A'})`;
        } else {
            modalArma.textContent = 'Arma: N/A';
        }

        if (characterData.tipo_transformacao || characterData.forma_transformacao) {
            modalTransformacao.innerHTML = `<span class="font-bold">Transformação:</span> ${characterData.tipo_transformacao || 'N/A'} - ${characterData.forma_transformacao || 'N/A'}`;
        } else {
            modalTransformacao.textContent = 'Transformação: N/A';
        }

        modalMoves.innerHTML = ''; // Limpa o conteúdo anterior
        if (characterData.habilidade_principal) {
            modalMoves.innerHTML = `
                <li class="flex items-start text-gray-400">
                    <span class="text-red-500 mr-2">•</span>
                    <span>${characterData.habilidade_principal}</span>
                </li>
            `;
        } else {
            modalMoves.innerHTML = '<li>Nenhuma habilidade principal encontrada.</li>';
        }

        if (characterData.fatality_detalhes && characterData.fatality_detalhes.nome) {
            modalFatality.innerHTML = `
                <span class="font-bold">Nome:</span> ${characterData.fatality_detalhes.nome || 'N/A'} |
                <span class="font-bold">Brutalidade:</span> ${characterData.fatality_detalhes.brutalidade || 'N/A'} |
                <span class="font-bold">Tipo:</span> ${characterData.fatality_detalhes.tipo || 'N/A'} |
                <span class="font-bold">Origem:</span> ${characterData.fatality_detalhes.origem || 'N/A'}
            `;
        } else {
            modalFatality.textContent = 'Nenhuma Fatality associada ou encontrada.';
        }

 
    } catch (error) {
        console.error('Erro ao carregar detalhes do personagem:', error);
        modalName.textContent = 'Erro ao Carregar';
        modalRaceOriginAlign.textContent = `Não foi possível carregar os detalhes: ${error.message}`;
        modalAgeStatus.textContent = '';
        modalCla.textContent = '';
        modalMundo.textContent = '';
        modalArma.textContent = '';
        modalTransformacao.textContent = '';
        modalMoves.innerHTML = '<li>Erro ao carregar habilidade.</li>';
        modalFatality.textContent = 'Erro ao carregar fatality.';
    }
}

document.addEventListener('click', function(e) {
    const targetButton = e.target.closest('button');
    const targetLink = e.target.closest('a');

    if (targetButton || targetLink) {
        const blood = document.createElement('div');
        blood.className = 'absolute w-4 h-4 bg-red-600 rounded-full pointer-events-none opacity-70';
        blood.style.left = `${e.clientX - 8}px`;
        blood.style.top = `${e.clientY - 8}px`;
        document.body.appendChild(blood);

        setTimeout(() => {
            blood.style.transform = 'scale(2)';
            blood.style.opacity = '0';
        }, 10);
        setTimeout(() => {
            blood.remove();
        }, 500);
    }
});