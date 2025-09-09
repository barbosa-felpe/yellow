
// Função que exibe os resultados filtrados no HTML
function displayResults(filteredLines) {
    const searchResultsContainer = document.getElementById('searchResults');
    // Limpa os resultados antigos
    searchResultsContainer.innerHTML = '';

    // Se não houver resultados, exibe uma mensagem
    if (filteredLines.length === 0) {
        searchResultsContainer.style.display = 'none';
        return;
    }
    
    searchResultsContainer.style.display = 'block';

    // Para cada linha encontrada, cria um elemento 'div' e o adiciona na página
    filteredLines.forEach(linhas => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.textContent = `${linhas.codigo} - ${linhas.nome}`;
        
        item.onclick = () => {
            alert(`Você selecionou a linha: ${linhas.nome}`);
            document.getElementById('searchInput').value = linhas.codigo;
            searchResultsContainer.innerHTML = '';
            searchResultsContainer.style.display = 'none';
        };
        
        searchResultsContainer.appendChild(item);
    });
}

// Função que busca os dados na nossa API do backend
async function setupDatabase(searchTerm) {
    // Se o campo de busca estiver vazio, limpa os resultados
    if (searchTerm.trim() === '') {
        displayResults([]);
        return;
    }
    
    try {
        // Chama a rota da nossa API, passando o termo de busca como query param
        const response = await fetch(`/api/search?term=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        
        // Mostra os resultados retornados pela API na tela
        displayResults(data);

    } catch (error) {
        console.error('Falha ao buscar as linhas de ônibus:', error);
    }
}

// "Escuta" o evento de digitação no campo de busca
const searchInput = document.getElementById('searchInput');

// Debounce: Evita fazer requisições à API a cada tecla pressionada
let debounceTimer;
searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const searchTerm = this.value.toLowerCase().trim();

    // Espera 300ms após o usuário parar de digitar para fazer a busca
    debounceTimer = setTimeout(() => {
        setupDatabase(searchTerm);
    }, 300);
});