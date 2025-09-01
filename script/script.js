window.addEventListener("scroll", function () {
  const scrollY = window.scrollY;

  // Se o scroll estiver na PRIMEIRA página
  if (scrollY < 650) {
      document.body.style.backgroundColor = "#ffcf00"; 
  }
  // Se o scroll estiver na SEGUNDA página
  else if (scrollY >= 600 && scrollY < 1800) {
      document.body.style.backgroundColor = "#000000"; 
  }
  // Se o scroll estiver na TERCEIRA página
  else {
      document.body.style.backgroundColor = "#ffcf00"; 
  }
});

//Informações do cliente

document.getElementById("cadastro").addEventListener("submit", async (e) => {
    e.preventDefault();

    // Pegando os valores
    const dados = {
      nome: document.getElementById("nome").value,
      senha: document.getElementById("senha").value,
      telefone: document.getElementById("telefone").value,
      email: document.getElementById("email").value,
      cpf: document.getElementById("cpf").value,
    };

    // Enviando pro servidor
    const resposta = await fetch("http://localhost:3000/cadastrar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });

    const resultado = await resposta.json();
    alert(resultado.mensagem);
  });