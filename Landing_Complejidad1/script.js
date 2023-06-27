function obtenerValores() {
  // Obtener los valores del formulario
  var tiempo = document.getElementById("tiempo").value;
  var tipo = document.getElementById("tipo").value;
  var alimento = document.getElementById("alimento").value;

  // Crear un objeto con los valores a enviar
  var datos = {
    tiempo: tiempo,
    tipo: tipo,
    alimento: alimento
  };

  // Imprimir los valores en la consola
  console.log("Valores a enviar:", datos);

  // Enviar los valores al servidor
  enviar(datos);
}

function enviar(datos) {
  fetch("http://localhost:5000/api/procesar_valores", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(datos)
  })
    .then(function(response) {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Error en la solicitud: " + response.status);
      }
    })
    .then(function(data) {
      console.log(data);
      mostrarResultados(data); // Assuming the response is an array of recipe objects
    })
    .catch(function(error) {
      console.error("Error al enviar los valores al servidor:", error);
    });
}

function mostrarResultados(recetas) {
  var recetasDiv = document.querySelector('.recetas'); // Obtener el elemento <div> por su clase
  // Limpiar el contenido actual del elemento <div>
  recetasDiv.innerHTML = '';

  // Recorrer las recetas y crear elementos HTML para mostrarlas
  recetas.forEach(function(receta) {
    var recetaElemento = document.createElement('p'); // Crear un elemento <p> para cada receta
    recetaElemento.textContent = receta.nombre; // Assuming each recipe object has a "nombre" property
    recetasDiv.appendChild(recetaElemento); // Agregar el elemento <p> al elemento <div>
  });
}

