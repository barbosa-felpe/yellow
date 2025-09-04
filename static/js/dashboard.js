const saldoDisplay = document.getElementById("saldoDisplay")
const botaoVerSaldo = document.querySelectorAll(".olharSaldo")

let verSaldo = false
let saldo = "1600,00"

saldoDisplay.innerText = saldo

botaoVerSaldo.forEach(botao => {
    botao.addEventListener("click", function () {
        verSaldo = !verSaldo
    
        if (verSaldo) {
            document.getElementById("blind").style.display = "none"
            document.getElementById("view").style.display = "block"

            saldoDisplay.innerText = "*".repeat(saldo.length)
        } else {
            document.getElementById("blind").style.display = "block"
            document.getElementById("view").style.display = "none"

            saldoDisplay.innerText = saldo
        }
    })
})

