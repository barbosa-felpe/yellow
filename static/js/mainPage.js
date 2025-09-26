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

  const littleBus = document.getElementById("littleBus");
  let posY = 200;
  let posX = 42;
  let angle = 0;
  
  // Etapas: sobe -> direita -> desce -> sobe -> esquerda -> desce
  let stage = "up";
  
  function animate() {
    if (stage === "up") {
      if (posY > 52) {
        posY -= 3;
      } else {
        stage = "right";
      }
    } 
    
    else if (stage === "right") {
      if (posX < 1579) {
        posX += 3;
        if (angle < 90) angle += 10;
      } else {
        stage = "down1";
      }
    } 
    
    else if (stage === "down1") {
      if (posY < 200) {
        posY += 3;
        if (angle < 180) angle += 10;
      } else {
        stage = "turn";
      }
    }

    else if (stage === "turn"){
      if(angle < 360){
        angle += 3;
      } else{
        stage = "up2"

        angle = 0
      }
      
    }
  
    else if(stage === "up2"){
      if(posY > 52){
        posY -= 3
        
      } else {
        stage = "left"
      }
    }
    
    else if(stage === "left"){
      if (posX > 42){
        posX -= 3;
        if (angle > -90) angle -= 10;
        if (angle < -90) angle = -90;
      } else{
        stage = "down2"
      }
    }

    else if(stage === "down2"){
      if (posY < 200){
        posY += 3;
        if (angle > -180) angle -= 10;
      } else {
        stage = "turn2"

        
      }
    }

    else if (stage === "turn2"){
      if(angle < 0){
        angle += 3;
      } else{
        stage = "up"
         angle = 0

        
      }
      
    }
    
  
    // aplica no elemento
    littleBus.style.top = posY + "px";
    littleBus.style.left = posX + "px";
    littleBus.style.transform = `rotate(${angle}deg)`;
  
    requestAnimationFrame(animate);
  }
  
  animate();
   