// Archivo: login.js
// Este archivo contiene interacciones para mejorar la experiencia del usuario en la página de login.

document.addEventListener("DOMContentLoaded", function() {
    // Selecciona el botón de envío
    const loginButton = document.querySelector('.login .inputBx input[type="submit"]');
  
    if (loginButton) {
      loginButton.addEventListener('click', function(event) {
        // Prevenir el envío del formulario para mostrar animación
        event.preventDefault();
  
        // Desactivar el botón para evitar múltiples clics
        loginButton.disabled = true;
        loginButton.value = "Cargando...";
  
        // Simular una llamada a servidor (puedes reemplazar esto con tu lógica real)
        setTimeout(() => {
          loginButton.disabled = false;
          loginButton.value = "Ingresar";
          // Aquí puedes añadir lógica para mostrar mensajes de error o redirigir al usuario
        }, 2000);
      });
    }
  
    // Añadir efecto de "ripple" al botón de envío
    loginButton.addEventListener('click', function(event) {
      const ripple = document.createElement("span");
      const rect = loginButton.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = event.clientX - rect.left - size / 2;
      const y = event.clientY - rect.top - size / 2;
  
      ripple.style.position = "absolute";
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      ripple.style.background = "rgba(255, 255, 255, 0.3)";
      ripple.style.borderRadius = "50%";
      ripple.style.transform = "scale(0)";
      ripple.style.opacity = "1";
      ripple.style.transition = "transform 0.5s, opacity 0.5s";
      ripple.classList.add("ripple-effect");
  
      loginButton.appendChild(ripple);
  
      // Forzar el reflow para activar la animación
      window.getComputedStyle(ripple).transform;
      ripple.style.transform = "scale(3)";
      ripple.style.opacity = "0";
  
      // Eliminar el efecto después de la animación
      ripple.addEventListener("transitionend", () => {
        ripple.remove();
      });
    });
  
    // Mover la bandera a la esquina inferior derecha
    const flag = document.querySelector('.flag');
    if (flag) {
      flag.style.position = "fixed";
      flag.style.bottom = "10px";
      flag.style.right = "10px";
      flag.style.width = "150px";
      flag.style.height = "auto";
      flag.style.animation = "wave 2s infinite";
    }
  });
  