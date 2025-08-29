window.addEventListener("scroll", function () {
    const scrollY = window.scrollY;
    
    if (scrollY > 700) { // valor em pixels para quando a troca ocorre
      document.body.style.backgroundColor = "#000000"; // nova cor
    } else {
      document.body.style.backgroundColor = "#ffcf00"; // cor original
    }
  });