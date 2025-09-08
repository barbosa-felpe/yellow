document.getElementById("formLogin").addEventListener("submit", function(e) {
    e.preventDefault(); // impede reload

    const cpf = document.getElementById("cpf").value.trim();
    const senha = document.getElementById("senha").value.trim();

    // Envia mesmo que esteja vazio; backend vai validar
    fetch("/logar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf, senha })
    })
    .then(res => res.json())
    .then(data => {
        console.log("📥 Resposta do backend:", data); // debug no console

        if (data.mensagem) {
            alert(data.mensagem);
            window.location.href = "/dashboard"; // redireciona em caso de sucesso
        } else if (data.erro) {
            alert("Erro: " + data.erro); // exibe erro em popup
        }
    })
    .catch(err => {
        console.error("🔥 Erro na requisição:", err);
        alert("Falha na conexão com o servidor.");
    });
});
