// Variável para guardar todas as linhas de ônibus depois de buscá-las na API
        let allBusLines = [];

        // Função para buscar os dados da API e preparar nossa lista de linhas
        async function fetchAllBusLines() {
            try {
                // Chama a rota da API que retorna todas as linhas
                const response = await fetch('/api/linhas');
                const data = await response.json();
                
                // O JSON é aninhado ('terminais' -> 'linhas'). Vamos criar uma lista única.
                const flatLines = [];
                const seenCodes = new Set(); // Para evitar linhas duplicadas na lista

                data.terminais.forEach(terminal => {
                    terminal.linhas.forEach(linha => {
                        // Se ainda não vimos esse código, adiciona na nossa lista
                        if (!seenCodes.has(linha.codigo)) {
                            flatLines.push(linha);
                            seenCodes.add(linha.codigo);
                        }
                    });
                });

                allBusLines = flatLines; // Armazena a lista única na variável global
                console.log('Linhas de ônibus carregadas:', allBusLines.length);

            } catch (error) {
                console.error('Falha ao buscar as linhas de ônibus:', error);
            }
        }

        // Função que exibe os resultados filtrados no HTML
        function displayResults(filteredLines) {
            const searchResultsContainer = document.getElementById('searchResults');
            // Limpa os resultados antigos
            searchResultsContainer.innerHTML = '';

            // Para cada linha encontrada, cria um elemento 'div' e o adiciona na página
            filteredLines.forEach(linha => {
                const item = document.createElement('div');
                item.className = 'search-result-item'; // Adiciona a classe para o CSS
                item.textContent = `${linha.codigo} - ${linha.nome}`; // Define o texto
                
                // Opcional: Adiciona uma ação ao clicar no resultado
                item.onclick = () => {
                    document.getElementById('searchInput').value = `${linha.codigo} - ${linha.nome}`;
                    searchResultsContainer.innerHTML = ''; // Limpa os resultados
                    desenharRota(linha.codigo); // Chama a função para desenhar a rota no mapa
                };
                
                searchResultsContainer.appendChild(item);
            });
        }

        // "Escuta" o evento de carregar a página para buscar os dados
        document.addEventListener('DOMContentLoaded', fetchAllBusLines);

        // "Escuta" o evento de digitação no campo de busca
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            // Se o campo de busca estiver vazio, limpa os resultados
            if (searchTerm === '') {
                displayResults([]); // Chama a função com uma lista vazia
                return;
            }

            // Filtra a lista 'allBusLines' com base no que foi digitado
            const filteredLines = allBusLines.filter(linha => {
                const nomeLowerCase = linha.nome.toLowerCase();
                const codigo = linha.codigo;
                // Retorna verdadeiro se o código ou o nome incluírem o termo da busca
                return codigo.includes(searchTerm) || nomeLowerCase.includes(searchTerm);
            });
            
            // Mostra os resultados filtrados na tela
            displayResults(filteredLines);
        });

const joinvilleCoords = [-26.3045, -48.8477];

// Inicializa o mapa no div com o ID 'mapa'
const mapa = L.map('mapa').setView(joinvilleCoords, 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mapa);

let rotaAtual = null;

async function desenharRota(codigoLinha) {
    // 1. Limpa a rota anterior do mapa, se existir
    if (rotaAtual) {
        mapa.removeLayer(rotaAtual);
    }

    try {
        console.log(`Buscando rota para a linha ${codigoLinha}...`);

        // 2. Busca os dados da rota na API que criamos no Flask
        const response = await fetch(`/api/rota/${codigoLinha}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.erro || 'Rota não encontrada.');
        }
        const dataRota = await response.json();
        
        // A API já retorna os pontos no formato [latitude, longitude]
        const coordenadas = dataRota.pontos;

        if (!coordenadas || coordenadas.length === 0) {
            console.warn(`A rota para a linha ${codigoLinha} não possui pontos.`);
            return;
        }

        // 3. Cria a polilinha (a rota) com as coordenadas
        const rotaLinha = L.polyline(coordenadas, { 
            color: '#0055b3', // Um tom de azul escuro
            weight: 5,
            opacity: 0.8
        });

        // 4. Adiciona a nova rota ao mapa e a armazena na variável 'rotaAtual'
        rotaAtual = rotaLinha.addTo(mapa);
        
        // 5. Ajusta o zoom e a centralização do mapa para mostrar a rota inteira
        mapa.fitBounds(rotaAtual.getBounds(), { padding: [30, 30] });

    } catch (error) {
        console.error(`Falha ao desenhar a rota para ${codigoLinha}:`, error);
        alert(`Não foi possível carregar a rota: ${error.message}`);
    }
}