// Mapeamento de imagens de personagens (pois você não as tem no banco de dados)
const characterImages = {
    "Scorpion": "https://www.fightersgeneration.com/nf7/char/scorpion-mk11-render.png",
    "Sub-Zero": "https://www.fightersgeneration.com/nf7/char/subzero-mk11-render.png",
    "Liu Kang": "https://www.fightersgeneration.com/nf7/char/liu-kang-mk11-render.png",
    "Raiden": "https://www.fightersgeneration.com/nf7/char/raiden-mk11-render.png",
    "Johnny Cage": "https://www.fightersgeneration.com/nf7/char/johnny-cage-mk11-render.png",
    "Sonya Blade": "https://www.fightersgeneration.com/nf7/char/sonya-blade-mk11-render.png",
    "Kitana": "https://www.fightersgeneration.com/nf7/char/kitana-mk11-render.png",
    "Jax Briggs": "https://www.fightersgeneration.com/nf7/char/jax-mk11-render.png",
    "Mileena": "https://www.fightersgeneration.com/nf7/char/mileena-mk11-render.png",
    // Adicione mais mapeamentos para os 48 personagens conforme necessário
    // Ex: "Kano": "URL_DA_IMAGEM_KANO.png",
    // ...
};

// Mapeamento de imagens dos jogos (baseado nos títulos, ou você pode adicionar URLs no banco)
const gameImages = {
    "Mortal Kombat": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2b/Mortal_Kombat_Logo.png/220px-Mortal_Kombat_Logo.png",
    "Mortal Kombat II": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5d/Mortal_Kombat_II_cover.jpg/220px-Mortal_Kombat_II_cover.jpg",
    "Mortal Kombat 3": "https://upload.wikimedia.org/wikipedia/en/a/a2/Mortal_Kombat_3_Cover.png",
    "Ultimate Mortal Kombat 3": "https://upload.wikimedia.org/wikipedia/en/4/4b/Ultimate_Mortal_Kombat_3_cover.jpg",
    "Mortal Kombat Trilogy": "https://upload.wikimedia.org/wikipedia/en/e/e0/Mortal_Kombat_Trilogy_cover.jpg",
    "Mortal Kombat 4": "https://upload.wikimedia.org/wikipedia/en/a/a4/Mortal_Kombat_4_cover.jpg",
    "Mortal Kombat: Deadly Alliance": "https://upload.wikimedia.org/wikipedia/en/9/91/Mortal_Kombat_Deadly_Alliance_cover_art.jpg",
    "Mortal Kombat: Deception": "https://upload.wikimedia.org/wikipedia/en/1/18/Mortal_Kombat_Deception_cover_art.jpg",
    "Mortal Kombat: Armageddon": "https://upload.wikimedia.org/wikipedia/en/e/e7/Mortal_Kombat_Armageddon_cover_art.jpg",
    "Mortal Kombat vs DC Universe": "https://upload.wikimedia.org/wikipedia/en/6/6b/Mortal_Kombat_vs_DC_Universe_cover_art.jpg",
    "Mortal Kombat (MK9)": "https://upload.wikimedia.org/wikipedia/en/9/9e/Mortal_Kombat_%282011%29_cover_art.jpg",
    "Mortal Kombat X": "https://upload.wikimedia.org/wikipedia/en/a/ad/Mortal_Kombat_X_cover_art.png",
    "Mortal Kombat 11": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a0/Mortal_Kombat_11_cover_art.png/220px-Mortal_Kombat_11_cover_art.png",
    "Mortal Kombat 1 (MK1)": "https://assets-prd.ignimgs.com/2023/05/18/mortalkombat1-button-1684436067654.jpg",
};


document.addEventListener('DOMContentLoaded', function() {
    // Carregar personagens na grid
    carregarKombatants();
    // Carregar jogos na timeline
    carregarJogosTimeline();
    // Adicionar funcionalidade ao modal (já está no seu HTML)
    setupModal();
});

// --- Funções de Carregamento de Dados ---

async function carregarKombatants() {
    const charactersGrid = document.querySelector('#characters .grid');
    charactersGrid.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Kombatants...</p>';

    try {
        const response = await fetch('http://127.0.0.1:5000/api/personagens'); // Nova rota da API
        if (!response.ok) {
            throw new Error(`Erro ao buscar personagens: ${response.statusText}`);
        }
        const personagens = await response.json();

        charactersGrid.innerHTML = ''; // Limpa o carregamento

        if (personagens.length === 0) {
            charactersGrid.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhum personagem encontrado.</p>';
            return;
        }

        personagens.forEach(personagem => {
            const card = document.createElement('div');
            card.className = 'character-card bg-gray-800 rounded-lg overflow-hidden border border-red-900 cursor-pointer transition duration-300';
            
            // Usar o mapeamento de imagens ou um placeholder
            const imageUrl = characterImages[personagem.nome] || 'https://via.placeholder.com/200x250/333/666?text=Image+Missing'; 

            card.innerHTML = `
                <div class="h-48 md:h-56 overflow-hidden">
                    <img src="${imageUrl}" 
                         alt="${personagem.nome}" 
                         class="w-full h-full object-cover">
                </div>
                <div class="p-4">
                    <h3 class="text-xl font-bold blood-text">${personagem.nome}</h3>
                    <p class="text-gray-400 text-sm mt-2">Raça: ${personagem.raca}</p>
                    <p class="text-gray-400 text-sm">Status: ${personagem.status_vida}</p>
                </div>
            `;
            // Passar o ID do personagem para openCharacterModal
            card.addEventListener('click', () => openCharacterModal(personagem.id));
            charactersGrid.appendChild(card);
        });

    } catch (error) {
        console.error('Erro ao carregar Kombatants:', error);
        charactersGrid.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar personagens: ${error.message}</p>`;
    }
}

async function carregarJogosTimeline() {
    const timelineContainer = document.querySelector('#games .space-y-12'); // Seleciona o contêiner dos itens da timeline
    timelineContainer.innerHTML = '<p class="col-span-full text-center text-gray-400">Carregando Linha do Tempo...</p>';

    try {
        const response = await fetch('http://127.0.0.1:5000/api/jogos'); // Nova rota da API
        if (!response.ok) {
            throw new Error(`Erro ao buscar jogos: ${response.statusText}`);
        }
        const jogos = await response.json();

        timelineContainer.innerHTML = ''; // Limpa o carregamento

        if (jogos.length === 0) {
            timelineContainer.innerHTML = '<p class="col-span-full text-center text-gray-400">Nenhum jogo encontrado.</p>';
            return;
        }

        jogos.forEach((jogo, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('relative', 'md:flex', 'justify-between', 'items-center', 'mb-16', 'timeline-item');

            // Determinar a ordem para alternar esquerda/direita
            const isEven = index % 2 === 0; // Se o índice for par, o texto fica à direita
            
            // Usar o mapeamento de imagens ou um placeholder
            const imageUrl = gameImages[jogo.titulo] || 'https://via.placeholder.com/220x220/333/666?text=Jogo';

            itemDiv.innerHTML = `
                <div class="md:w-5/12 md:pr-8 ${isEven ? 'text-right' : 'order-last text-left'} mb-4 md:mb-0">
                    <h3 class="text-2xl font-bold blood-text">${jogo.titulo} (${jogo.ano})</h3>
                    <p class="text-gray-300">Plataformas: ${jogo.plataforma}</p>
                    </div>
                <div class="hidden md:block w-2 h-2 rounded-full bg-red-600 mx-auto"></div>
                <div class="md:w-5/12 md:pl-8 ${isEven ? '' : 'order-first'}">
                    <img src="${imageUrl}" 
                         alt="${jogo.titulo}" 
                         class="w-full max-w-xs mx-auto rounded border border-red-900">
                </div>
            `;
            timelineContainer.appendChild(itemDiv);

            // Adiciona o círculo da timeline (que já está na sua CSS customizada)
            const circle = document.createElement('div');
            circle.className = 'hidden md:block w-3 h-3 rounded-full bg-red-600 absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2';
            itemDiv.appendChild(circle);
        });

    } catch (error) {
        console.error('Erro ao carregar Linha do Tempo:', error);
        timelineContainer.innerHTML = `<p class="col-span-full text-center text-red-500">Erro ao carregar jogos: ${error.message}</p>`;
    }
}

// --- Lógica do Modal de Personagem ---

function setupModal() {
    const modal = document.getElementById('characterModal');
    const closeModalBtn = document.getElementById('closeModal');

    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
}

// openCharacterModal agora recebe o ID e busca os detalhes do back-end
async function openCharacterModal(id_personagem) {
    const modal = document.getElementById('characterModal');
    const modalImage = document.getElementById('modalCharacterImage');
    const modalName = document.getElementById('modalCharacterName');
    const modalBio = document.getElementById('modalCharacterBio');
    const modalMoves = document.getElementById('modalCharacterMoves');
    const modalFatality = document.getElementById('modalCharacterFatality');

    // Limpa conteúdo antigo e mostra mensagem de carregamento
    modalImage.src = '';
    modalName.textContent = 'Carregando...';
    modalBio.textContent = '';
    modalMoves.innerHTML = '<li>Carregando habilidades...</li>';
    modalFatality.textContent = 'Carregando fatality...';
    modal.classList.remove('hidden');

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/personagens/${id_personagem}`);
        if (!response.ok) {
            throw new Error(`Erro ao buscar detalhes do personagem: ${response.statusText}`);
        }
        const characterData = await response.json();

        // Popula o modal com os dados do back-end
        modalImage.src = characterImages[characterData.nome] || 'https://via.placeholder.com/250x300/333/666?text=Image+Missing';
        modalImage.alt = characterData.nome;
        modalName.textContent = characterData.nome;
        modalBio.textContent = `Raça: ${characterData.raca} | Idade: ${characterData.idade} | Status: ${characterData.status_vida}`; // Exemplo, adapte a bio real se tiver no BD

        // Habilidades
        modalMoves.innerHTML = '';
        if (characterData.habilidades && characterData.habilidades.length > 0) {
            characterData.habilidades.forEach(habilidade => {
                const li = document.createElement('li');
                li.className = 'flex items-start';
                li.innerHTML = `
                    <span class="text-red-500 mr-2">•</span>
                    <span>${habilidade.nome} (Tipo: ${habilidade.tipo}, Categoria: ${habilidade.categoria}, Elemento: ${habilidade.elemento})</span>
                `;
                modalMoves.appendChild(li);
            });
        } else {
            modalMoves.innerHTML = '<li>Nenhuma habilidade encontrada.</li>';
        }

        // Fatality
        if (characterData.fatality_detalhes && characterData.fatality_detalhes.nome) {
            modalFatality.textContent = `Nome: ${characterData.fatality_detalhes.nome} | Brutalidade: ${characterData.fatality_detalhes.brutalidade} | Tipo: ${characterData.fatality_detalhes.tipo} | Origem: ${characterData.fatality_detalhes.origem}`;
        } else {
            modalFatality.textContent = 'Nenhuma Fatality associada ou encontrada.';
        }

    } catch (error) {
        console.error('Erro ao carregar detalhes do personagem:', error);
        modalName.textContent = 'Erro';
        modalBio.textContent = `Não foi possível carregar os detalhes: ${error.message}`;
        modalMoves.innerHTML = '';
        modalFatality.textContent = '';
    }
}


// --- Lógica para o efeito de sangue ao clicar (já estava no seu HTML, movido para cá) ---
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON' || e.target.parentElement.tagName === 'BUTTON') {
        const blood = document.createElement('div');
        blood.className = 'absolute w-4 h-4 bg-red-600 rounded-full pointer-events-none opacity-70';
        blood.style.left = `${e.pageX - 8}px`;
        blood.style.top = `${e.pageY - 8}px`;
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