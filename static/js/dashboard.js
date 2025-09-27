// Pega o elemento que mostra o saldo
const saldoDisplay = document.getElementById("saldoDisplay");
const botaoVerSaldo = document.querySelectorAll(".olharSaldo");

let verSaldo = true; // inicialmente o saldo está visível
const saldoOriginal = saldoDisplay.innerText; // pega o saldo renderizado pelo Flask

botaoVerSaldo.forEach(botao => {
    botao.addEventListener("click", function () {
        verSaldo = !verSaldo;

        if (verSaldo) {
            // Mostra o saldo real
            saldoDisplay.innerText = saldoOriginal;
        } else {
            // Oculta o saldo com asteriscos
            saldoDisplay.innerText = "*".repeat(saldoOriginal.length);
        }
    });
});


const slider = document.getElementById("scrollWrapper");
let isDown = false;
let startX;
let scrollLeft;

// Para o "arrastar" com o mouse (opcional, mas melhora a experiência)
slider.addEventListener('mousedown', (e) => {
  isDown = true;
  slider.classList.add('active');
  startX = e.pageX - slider.offsetLeft;
  scrollLeft = slider.scrollLeft;
});
slider.addEventListener('mouseleave', () => {
  isDown = false;
  slider.classList.remove('active');
});
slider.addEventListener('mouseup', () => {
  isDown = false;
  slider.classList.remove('active');
});
slider.addEventListener('mousemove', (e) => {
  if(!isDown) return;
  e.preventDefault();
  const x = e.pageX - slider.offsetLeft;
  const walk = (x - startX) * 1; // O multiplicador ajusta a velocidade do arrastar
  slider.scrollLeft = scrollLeft - walk;
});

// A solução para o "agarrar" do scroll do mouse
slider.addEventListener("wheel", (e) => {
  e.preventDefault();
  slider.scrollLeft += e.deltaY;
});


