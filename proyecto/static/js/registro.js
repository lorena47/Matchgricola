const API = "/api";

async function registrar() {
  const resultado = document.getElementById("resultado");
  resultado.innerHTML = "";

  const tipo = document.getElementById("tipo").value;

  const payload = {
    usuario: document.getElementById("usuario").value,
    nombre: document.getElementById("nombre").value,
    correo: document.getElementById("correo").value,
    contrasenia: document.getElementById("contrasenia").value,
    telefono: document.getElementById("telefono").value || null,
  };

  try {
    const response = await fetch(`${API}/${tipo}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      resultado.innerHTML = `
        <div class="alert alert-danger">
          <strong>Error:</strong>
          <pre class="mb-0">${JSON.stringify(data, null, 2)}</pre>
        </div>
      `;
      return;
    }

    resultado.innerHTML = `
      <div class="alert alert-success">
        Cuenta creada correctamente ✔️<br>
        <a href="/login/" class="alert-link">Ir al login</a>
      </div>
    `;

  } catch (error) {
    resultado.innerHTML = `
      <div class="alert alert-danger">
        Error de conexión con la API
      </div>
    `;
  }
}
