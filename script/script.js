function backgroundPage(){

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

}

function enviar(){
    const nmCompleto = document.getElementById("nmCompleto").value
    const senha = document.getElementById("senha").value
    const tel = document.getElementById("tel").value
    const email = document.getElementById("email").value
    const cpf = document.getElementById("cpf").value

    const usuario = {
        "nome": nmCompleto,
        "senha": senha,
        "tel": tel,
        "email": email,
        "cpf": cpf
    }

    fetch("/cadastrar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(usuario)  
    })

    .then(res => res.json())
    .then(data => alert(data.mensagem))
    .catch(err => console.error(err))
}