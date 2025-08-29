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
