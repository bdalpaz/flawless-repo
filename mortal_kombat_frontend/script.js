document.addEventListener('DOMContentLoaded', () => {
    carregarPersonagens(); // Carrega os personagens ao carregar a página
});

async function carregarPersonagens() {
    const listaPersonagensDiv = document.getElementById('personagens-lista');
    listaPersonagensDiv.innerHTML = '<p>Carregando personagens...</p>'; // Mensagem de carregamento

    try {
        const response = await fetch('http://127.0.0.1:5000/personagens'); // URL do seu back-end Flask
        if (!response.ok) {
            throw new Error(`Erro HTTP! Status: ${response.status}`);
        }
        const personagens = await response.json();

        listaPersonagensDiv.innerHTML = ''; // Limpa a mensagem de carregamento

        if (personagens.length === 0) {
            listaPersonagensDiv.innerHTML = '<p>Nenhum personagem encontrado.</p>';
            return;
        }

        personagens.forEach(personagem => {
            const cardCol = document.createElement('div');
            cardCol.classList.add('col');

            cardCol.innerHTML = `
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${personagem.nome}</h5>
                        <p class="card-text">Raça: ${personagem.raca}</p>
                        <p class="card-text">Status: ${personagem.status_vida}</p>
                        <a href="#" class="btn btn-primary btn-sm" onclick="mostrarDetalhesPersonagem(${personagem.id_personagem})">Ver Detalhes</a>
                    </div>
                </div>
            `;
            listaPersonagensDiv.appendChild(cardCol);
        });

    } catch (error) {
        console.error('Erro ao buscar personagens:', error);
        listaPersonagensDiv.innerHTML = `<p class="text-danger">Erro ao carregar personagens: ${error.message}</p>`;
    }
}

async function mostrarDetalhesPersonagem(id) {
    alert(`Funcionalidade de detalhes para o personagem ID: ${id} (ainda não implementada)`);
    // Aqui você faria uma nova requisição para 'http://127.0.0.1:5000/personagens/${id}'
    // e exibiria os detalhes em um modal ou nova página.
}