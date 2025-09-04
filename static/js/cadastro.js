document.getElementById("formCadastro").addEventListener("submit", function(e) {
    e.preventDefault(); // evita reload da página
  
    const usuario = {
      nome: document.getElementById("nmCompleto").value,
      senha: document.getElementById("senha").value,
      tel: document.getElementById("tel").value,
      email: document.getElementById("email").value,
      cpf: document.getElementById("cpf").value
    };
  
    fetch("/cadastrar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(usuario)
    })
    .then(res => res.json())
    .then(data => alert(data.mensagem || data.erro))
    .catch(err => console.error(err));
  });