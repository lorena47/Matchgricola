const API = "http://127.0.0.1:8080/api";
const usuario = localStorage.getItem("usuario");

if (!usuario) location.href = "/login/";

let feedData = null;
let ofertaSeleccionada = null;
let propuestaCancelarId = null;
let ofertaEliminarId = null;



/* ================= UTIL ================= */

function formatFecha(f) {
  const [y, m, d] = f.split("-");
  return `${d}/${m}/${y}`;
}

/* ================= FEED ================= */

async function cargarFeed() {
  const res = await fetch(`${API}/propietarios/${usuario}/feed/`);
  feedData = await res.json();

  renderOfertas(feedData.ofertas);
  cargarSuscripciones();
}

/* ================= OFERTAS ================= */

async function renderOfertas(ofertas) {
  const div = document.getElementById("lista-ofertas");
  div.innerHTML = "";

  if (!ofertas.length) {
    div.innerHTML = `<p class="text-muted">Sin ofertas</p>`;
    return;
  }

  for (const o of ofertas) {
    const p = await (await fetch(`${API}/periodos/${o.periodo}/`)).json();

    div.innerHTML += `
      <div class="border rounded p-3 mb-3">
        <strong>${o.titulo}</strong><br>
        <small>${o.descripcion}</small><br>
        <small>Periodo: ${formatFecha(p.fecha_inicio)} → ${formatFecha(p.fecha_fin)}</small><br>
        <small>Plazas: ${o.plazas}</small><br>
        <small>€/hora: ${o.euros_hora}</small>

        <div class="row mt-3 g-2">
          <div class="col">
            <button class="btn btn-outline-primary w-100"
              onclick="verJornaleros(${o.id})">
              Ver jornaleros
            </button>
          </div>
          <div class="col-auto">
            <button class="btn btn-danger"
              onclick="eliminarOferta(${o.id}, '${o.titulo}')">
              <i class="bi bi-trash-fill text-white"></i>
            </button>
          </div>
        </div>
      </div>`;
  }
}

async function crearOferta() {
  const titulo = document.getElementById("titulo").value;
  const descripcion = document.getElementById("descripcion").value;
  const plazas = document.getElementById("plazas").value;
  const euros = document.getElementById("euros").value;
  const inicio = document.getElementById("inicio").value;
  const fin = document.getElementById("fin").value;

  if (!titulo || !descripcion || !plazas || !euros || !inicio || !fin) {
    alert("Rellena todos los campos");
    return;
  }

  const resPeriodo = await fetch(`${API}/periodos/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fecha_inicio: inicio,
      fecha_fin: fin
    })
  });

  if (!resPeriodo.ok) {
    const err = await resPeriodo.json();
    alert("Error creando periodo:\n" + JSON.stringify(err, null, 2));
    return;
  }

  const periodo = await resPeriodo.json();

  const resOferta = await fetch(`${API}/ofertas/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      titulo,
      descripcion,
      plazas,
      euros_hora: euros,
      periodo: periodo.id,
      propietario: usuario
    })
  });

  if (!resOferta.ok) {
    const err = await resOferta.json();
    alert("Error creando oferta:\n" + JSON.stringify(err, null, 2));
    return;
  }

  document.getElementById("titulo").value = "";
  document.getElementById("descripcion").value = "";
  document.getElementById("plazas").value = "";
  document.getElementById("euros").value = "";
  document.getElementById("inicio").value = "";
  document.getElementById("fin").value = "";

  cargarFeed();
}


/* ================= JORNALEROS ================= */

function verJornaleros(ofertaId) {
  ofertaSeleccionada = ofertaId;

  const oferta = feedData.ofertas.find(o => o.id === ofertaId);

  document.getElementById("texto-jornaleros").innerText =
    `Jornaleros disponibles para la oferta "${oferta.titulo}"`;

  const div = document.getElementById("lista-jornaleros");
  div.innerHTML = "";

  const jornaleros = feedData.jornaleros_disponibles[ofertaId] || [];

  if (!jornaleros.length) {
    div.innerHTML = `<p class="text-muted">No hay jornaleros disponibles</p>`;
    return;
  }

  jornaleros.forEach(j => {
    div.innerHTML += `
      <div class="border rounded p-3 mb-2 d-flex justify-content-between align-items-center">
        <strong>${j.usuario}</strong>
        <button class="btn btn-outline-success btn-sm"
          onclick="proponerOferta('${j.usuario}')">
          Proponer
        </button>
      </div>`;
  });
}

/* ================= PROPONER ================= */

async function proponerOferta(jornalero) {
  const res = await fetch(`${API}/suscripciones/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jornalero,
      oferta: ofertaSeleccionada,
      interesado: "propietario"
    })
  });

  if (!res.ok) {
    const err = await res.json();
    alert(JSON.stringify(err, null, 2));
    return;
  }

  cargarSuscripciones();
}


/* ================= CANCELAR PROPUESTA ================= */

function cancelarPropuesta(id, titulo, jornalero) {
  propuestaCancelarId = id;

  document.getElementById("propuesta-a-cancelar").innerText =
    `${titulo} · Jornalero: ${jornalero}`;

  new bootstrap.Modal(
    document.getElementById("modalCancelarPropuesta")
  ).show();
}

async function confirmarCancelarPropuesta() {
  await fetch(`${API}/suscripciones/${propuestaCancelarId}/`, {
    method: "DELETE"
  });

  bootstrap.Modal.getInstance(
    document.getElementById("modalCancelarPropuesta")
  ).hide();

  cargarSuscripciones();
}


/* ================= SUSCRIPCIONES ================= */

async function cargarSuscripciones() {
  const res = await fetch(`${API}/suscripciones/?propietario=${usuario}`);
  const data = await res.json();

  renderPendientes(
    data.filter(s => s.activa && !s.trabajo && s.interesado === "propietario")
  );

  renderSuscripciones(
    data.filter(s => s.activa && !s.trabajo && s.interesado === "jornalero")
  );

  renderLista("aceptadas", data.filter(s => s.trabajo));
  renderLista("rechazadas", data.filter(s => !s.activa && !s.trabajo));
}

/* ================= PENDIENTES ================= */

async function renderPendientes(lista) {
  const ul = document.getElementById("pendientes");
  ul.innerHTML = "";

  if (!lista.length) {
    ul.innerHTML = `<li class="list-group-item text-muted">Vacío</li>`;
    return;
  }

  for (const s of lista) {
    const oferta = await (await fetch(`${API}/ofertas/${s.oferta}/`)).json();

    ul.innerHTML += `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>${oferta.titulo}</strong><br>
          <small>Jornalero: ${s.jornalero}</small>
        </div>
        <button class="btn btn-secondary btn-sm"
          onclick="cancelarPropuesta(${s.id}, '${oferta.titulo}', '${s.jornalero}')">
          <i class="bi bi-trash-fill"></i>
        </button>
      </li>`;
  }
}

/* ================= ACEPTAR / RECHAZAR ================= */

async function renderSuscripciones(lista) {
  const ul = document.getElementById("suscripciones");
  ul.innerHTML = "";

  if (!lista.length) {
    ul.innerHTML = `<li class="list-group-item text-muted">Vacío</li>`;
    return;
  }

  for (const s of lista) {
    const oferta = await (await fetch(`${API}/ofertas/${s.oferta}/`)).json();

    ul.innerHTML += `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <strong>${oferta.titulo}</strong><br>
          <small>Jornalero: ${s.jornalero}</small>
        </div>
        <div class="d-flex gap-1">
          <button class="btn btn-success btn-sm"
            onclick="aceptarSuscripcion(${s.id})">
            ✓
          </button>
          <button class="btn btn-danger btn-sm"
            onclick="rechazarSuscripcion(${s.id})">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

      </li>`;
  }
}

async function aceptarSuscripcion(id) {
  const res = await fetch(`${API}/suscripciones/${id}/aceptar/`, {
    method: "POST"
  });

  if (!res.ok) {
    const err = await res.json();
    alert(JSON.stringify(err, null, 2));
    return;
  }

  cargarFeed();
  cargarSuscripciones();
}


async function rechazarSuscripcion(id) {
  await fetch(`${API}/suscripciones/${id}/rechazar/`, {
    method: "POST"
  });
  cargarSuscripciones();
}


/* ================= LISTAS ================= */

async function renderLista(id, lista) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";

  if (!lista.length) {
    ul.innerHTML = `<li class="list-group-item text-muted">Vacío</li>`;
    return;
  }

  for (const s of lista) {
    const oferta = await (await fetch(`${API}/ofertas/${s.oferta}/`)).json();
    ul.innerHTML += `
      <li class="list-group-item">
        <strong>${oferta.titulo}</strong><br>
        <small>Jornalero: ${s.jornalero}</small>
      </li>`;
  }
}

/* ================= ELIMINAR OFERTA ================= */

function eliminarOferta(id, titulo) {
  ofertaEliminarId = id;

  document.getElementById("oferta-a-eliminar").innerText = titulo;

  new bootstrap.Modal(
    document.getElementById("modalEliminarOferta")
  ).show();
}

async function confirmarEliminarOferta() {
  await fetch(`${API}/ofertas/${ofertaEliminarId}/`, {
    method: "DELETE"
  });

  bootstrap.Modal.getInstance(
    document.getElementById("modalEliminarOferta")
  ).hide();

  cargarFeed();
}

cargarFeed();
