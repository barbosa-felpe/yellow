function backgroundPage(){
    window.addEventListener("scroll", function(){
        const scrollY = window.scrollY;
        if(scrollY < 600){
            document.body.style.backgroundColor = "#ffcf00";
        } else if(scrollY >= 600 && scrollY < 1800){
            document.body.style.backgroundColor = "#000000";
        } else {
            document.body.style.backgroundColor = "#ffcf00";
        }
    });
}
backgroundPage();

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
    .then(data => alert(data.mensagem))
    .catch(err => console.error(err));
  });
