const API = "http://127.0.0.1:8080/api";

async function login() {
  const resultado = document.getElementById("resultado");
  resultado.innerHTML = "";

  const payload = {
    usuario: document.getElementById("usuario").value,
    contrasenia: document.getElementById("contrasenia").value,
  };

  try {
    const response = await fetch(`${API}/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      resultado.innerHTML = `
        <div class="alert alert-danger">
          ${data.error || "Credenciales incorrectas"}
        </div>
      `;
      return;
    }

    localStorage.setItem("usuario", data.usuario);
    localStorage.setItem("tipo", data.tipo);

    if (data.tipo === "jornalero") {
      window.location.href = "jornalero_feed.html";
    } else {
      window.location.href = "propietario_feed.html";
    }

  } catch (error) {
    resultado.innerHTML = `
      <div class="alert alert-danger">
        Error de conexión con la API
      </div>
    `;
  }
}
