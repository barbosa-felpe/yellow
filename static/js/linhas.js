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
                    alert(`Você selecionou a linha: ${linha.nome}`);
                    document.getElementById('searchInput').value = linha.codigo; // Preenche o input
                    searchResultsContainer.innerHTML = ''; // Limpa os resultados
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