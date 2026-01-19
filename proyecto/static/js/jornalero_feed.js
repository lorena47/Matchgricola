const API = "/api";
const usuario = localStorage.getItem("usuario");

let calendarioId = null;
let periodoEliminarInicio = null;
let periodoEliminarFin = null;
let suscripcionCancelarId = null;

if (!usuario) window.location.href = "/login/";

/* ===== UTIL ===== */

function formatFecha(f) {
  const [y, m, d] = f.split("-");
  return `${d}/${m}/${y}`;
}

function mostrarMensaje(tipo, texto) {
  document.getElementById("mensaje-calendario").innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show">
      ${texto}
      <button class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
}

/* ===== FEED ===== */

async function cargarFeed() {
  const res = await fetch(`${API}/jornaleros/${usuario}/feed/`);
  const data = await res.json();

  calendarioId = data.calendario_id;
  renderPeriodos(data.periodos_disponibles);
  renderOfertas(data.ofertas_disponibles);
  cargarSuscripciones();
}

/* ===== PERIODOS ===== */

function renderPeriodos(periodos) {
  const ul = document.getElementById("lista-periodos");
  ul.innerHTML = "";

  if (!periodos.length) {
    ul.innerHTML = `<li class="list-group-item text-muted">Sin periodos</li>`;
    return;
  }

  periodos.forEach(p => {
    ul.innerHTML += `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${formatFecha(p.fecha_inicio)} → ${formatFecha(p.fecha_fin)}
        <button class="btn btn-danger btn-sm"
          onclick="mostrarModalEliminar('${p.fecha_inicio}','${p.fecha_fin}')">
          <i class="bi bi-trash-fill text-white"></i>
        </button>
      </li>`;
  });
}

async function incluirPeriodo() {
  const inicio = inicioInput();
  const fin = finInput();

  if (!inicio || !fin) {
    mostrarMensaje("warning", "Debes introducir ambas fechas");
    return;
  }

  await fetch(`${API}/calendarios/${calendarioId}/incluir_periodo/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fecha_inicio: inicio, fecha_fin: fin })
  });

  cargarFeed();
}

async function quitarPeriodo() {
  const inicio = inicioInput();
  const fin = finInput();

  if (!inicio || !fin) {
    mostrarMensaje("warning", "Debes introducir ambas fechas");
    return;
  }

  await fetch(`${API}/calendarios/${calendarioId}/quitar_periodo/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fecha_inicio: inicio, fecha_fin: fin })
  });

  cargarFeed();
}

function mostrarModalEliminar(i, f) {
  periodoEliminarInicio = i;
  periodoEliminarFin = f;

  document.getElementById("periodo-a-eliminar").innerText =
    `${formatFecha(i)} → ${formatFecha(f)}`;

  new bootstrap.Modal(
    document.getElementById("modalEliminarPeriodo")
  ).show();
}

async function confirmarEliminarPeriodo() {
  await fetch(`${API}/calendarios/${calendarioId}/quitar_periodo/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fecha_inicio: periodoEliminarInicio,
      fecha_fin: periodoEliminarFin
    })
  });

  bootstrap.Modal.getInstance(
    document.getElementById("modalEliminarPeriodo")
  ).hide();

  cargarFeed();
}

/* ===== OFERTAS ===== */

function renderOfertas(ofertas) {
  const div = document.getElementById("lista-ofertas");
  div.innerHTML = "";

  if (!ofertas.length) {
    div.innerHTML = `<p class="text-muted">No hay ofertas disponibles</p>`;
    return;
  }

  ofertas.forEach(o => {
    div.innerHTML += `
      <div class="border rounded p-3 mb-3">
        <h5>${o.titulo}</h5>
        <p>${o.descripcion}</p>
        <p><b>Periodo:</b> ${o.periodo}</p>
        <p><b>€/hora:</b> ${o.euros_hora}</p>
        <p><b>Plazas:</b> ${o.plazas}</p>
        <p><b>Propietario:</b> ${o.propietario}</p>

        <div class="d-grid mt-3">
          <button class="btn btn-primary" onclick="suscribirse(${o.id})">
            Suscribirse
          </button>
        </div>
      </div>`;
  });
}


async function suscribirse(ofertaId) {
  await fetch(`${API}/suscripciones/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jornalero: usuario,
      oferta: ofertaId,
      interesado: "jornalero"
    })
  });

  cargarFeed();
}

/* ===== SUSCRIPCIONES ===== */

async function cargarSuscripciones() {
  const res = await fetch(`${API}/suscripciones/?jornalero=${usuario}`);
  const data = await res.json();

  renderLista(
    "suscripciones-pendientes",
    data.filter(s =>
      s.activa &&
      !s.trabajo &&
      s.interesado === "jornalero"
    )
  );

  renderLista(
    "suscripciones-propuestas",
    data.filter(s =>
      s.activa &&
      !s.trabajo &&
      s.interesado === "propietario"
    )
  );

  renderLista(
    "suscripciones-aceptadas",
    data.filter(s => s.trabajo)
  );

  renderLista(
    "suscripciones-rechazadas",
    data.filter(s => !s.activa && !s.trabajo)
  );
}


async function renderLista(id, lista) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";

  if (!lista.length) {
    ul.innerHTML = `<li class="list-group-item text-muted">Vacío</li>`;
    return;
  }

  for (const s of lista) {
    const o = await (await fetch(`${API}/ofertas/${s.oferta}/`)).json();
    const p = await (await fetch(`${API}/periodos/${o.periodo}/`)).json();

    ul.innerHTML += `
      <li class="list-group-item position-relative">
        
        <!-- BOTONES SEGÚN LISTA -->
        ${id === "suscripciones-pendientes" ? `
          <button class="btn btn-secondary btn-sm position-absolute top-0 end-0 m-2"
            onclick="mostrarModalCancelarSuscripcion(${s.id}, '${o.titulo}', '${p.fecha_inicio}', '${p.fecha_fin}')">
            <i class="bi bi-trash-fill text-white"></i>
          </button>` : ``}

        ${id === "suscripciones-propuestas" ? `
          <div class="position-absolute top-0 end-0 m-2 d-flex gap-1">
            <button class="btn btn-success btn-sm"
              onclick="aceptarPropuesta(${s.id})">
              ✓
            </button>
            <button class="btn btn-danger btn-sm"
              onclick="rechazarPropuesta(${s.id})">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>` : ``}

        <strong>${o.titulo}</strong><br>
        <small>
          Periodo: ${formatFecha(p.fecha_inicio)} → ${formatFecha(p.fecha_fin)}<br>
          €/hora: ${o.euros_hora}<br>
          Propietario: ${o.propietario}
        </small>
      </li>`;
  }
}

async function aceptarPropuesta(id) {
  await fetch(`${API}/suscripciones/${id}/aceptar/`, {
    method: "POST"
  });
  cargarFeed();
}

async function rechazarPropuesta(id) {
  await fetch(`${API}/suscripciones/${id}/rechazar/`, {
    method: "POST"
  });
  cargarFeed();
}

function mostrarModalCancelarSuscripcion(id, titulo, i, f) {
  suscripcionCancelarId = id;
  document.getElementById("suscripcion-a-cancelar").innerText =
    `${titulo} (${formatFecha(i)} → ${formatFecha(f)})`;

  new bootstrap.Modal(
    document.getElementById("modalCancelarSuscripcion")
  ).show();
}

async function confirmarCancelarSuscripcion() {
  await fetch(`${API}/suscripciones/${suscripcionCancelarId}/`, {
    method: "DELETE"
  });

  bootstrap.Modal.getInstance(
    document.getElementById("modalCancelarSuscripcion")
  ).hide();

  cargarFeed();
}

/* ===== HELPERS ===== */

function inicioInput() {
  return document.getElementById("inicio").value;
}

function finInput() {
  return document.getElementById("fin").value;
}

cargarFeed();
