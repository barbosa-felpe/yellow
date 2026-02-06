document
  .getElementById("formRecarga")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const idCartao = document.getElementById("selectCartao").value;
    const valor = document.getElementById("valorRecarga").value;

    if (!idCartao || !valor) {
      alert("Por favor, preencha todos os campos.");
      return;
    }

    const dados = {
      id_cartao: idCartao,
      valor: valor,
    };

    try {
      const response = await fetch("/api/realizar_recarga", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
      });

      const data = await response.json();

      if (response.ok) {
        alert(data.mensagem);
        if (data.redirect) {
          window.location.href = data.redirect;
        }
      } else {
        alert("Erro: " + data.erro);
      }
    } catch (err) {
      console.error("Erro:", err);
      alert("Erro de conexão com o servidor.");
    }
  });
