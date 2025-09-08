document.getElementById("formCadastro").addEventListener("submit", async function(e) {
  e.preventDefault(); // evita reload da página

  // Criar objeto com os dados do formulário
  const usuario = {
    nome: document.getElementById("nmCompleto").value.trim(),
    senha: document.getElementById("senha").value.trim(),
    tel: document.getElementById("tel").value.trim(),
    email: document.getElementById("email").value.trim(),
    cpf: document.getElementById("cpf").value.trim()
  };

  try {
    const response = await fetch("/cadastrar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(usuario)
    });

    const data = await response.json();
    console.log("Resposta do backend:", data);

    if (response.ok && data.mensagem) {
      alert(data.mensagem);
      window.location.href = "/login"; // redireciona
    } else if (data.erro) {
      alert("Erro: " + data.erro);
    } else {
      alert("Erro inesperado. Tente novamente.");
    }
  } catch (err) {
    console.error("Erro na requisição:", err);
    alert("Não foi possível conectar ao servidor.");
  }
});
