import subprocess
import time
import requests
import pytest
import os


BASE = os.getenv("BASE_URL", "http://localhost:8000/api")


@pytest.fixture(scope="session", autouse=True)
def cluster():
    print("\n==> Levantando clúster Docker...")
    with open(os.devnull, "w") as DEVNULL:
        subprocess.run(["docker", "compose", "down", "-v"], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.run(
            ["docker", "compose", "up", "--build", "-d"],
            stdout=DEVNULL,
            stderr=DEVNULL,
            check=True
        )

    # Esperar a la API
    for i in range(30):
        try:
            r = requests.get(f"{BASE}/jornaleros/")
            if r.status_code < 500:
                print("API lista.")
                break
        except Exception:
            pass

        print(f"Esperando a la API... {i}")
        time.sleep(2)
    else:
        subprocess.run(["docker", "compose", "down", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        raise RuntimeError("El servicio web no arrancó.")

    yield

    print("\n==> Apagando clúster Docker...")
    with open(os.devnull, "w") as DEVNULL:
        subprocess.run(["docker", "compose", "down", "-v"], stdout=DEVNULL, stderr=DEVNULL)


def test_crear_jornalero():
    payload = {
        "usuario": "lorenaJOR",
        "nombre": "Lorena",
        "correo": "lorenaPRO@gmail.com",
        "contrasenia": "pro"
    }
    r = requests.post(f"{BASE}/jornaleros/", json=payload)
    assert r.status_code == 201


def test_listar_jornaleros():
    r = requests.get(f"{BASE}/jornaleros/")
    assert r.status_code == 200
    assert any(j["usuario"] == "lorenaJOR" for j in r.json())


def test_crear_propietario():
    payload = {
        "usuario": "lorenaPRO",
        "nombre": "Lorena",
        "correo": "lorenaPRO@gmail.com",
        "contrasenia": "pro"
    }
    r = requests.post(f"{BASE}/propietarios/", json=payload)
    assert r.status_code == 201


def test_listar_propietarios():
    r = requests.get(f"{BASE}/propietarios/")
    assert r.status_code == 200
    assert any(p["usuario"] == "lorenaPRO" for p in r.json())


def test_crear_periodo():
    payload = {
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-10"
    }
    r = requests.post(f"{BASE}/periodos/", json=payload)
    assert r.status_code == 201


def test_listar_periodos():
    r = requests.get(f"{BASE}/periodos/")
    assert r.status_code == 200
    periodos = r.json()
    assert len(periodos) == 1


def test_crear_calendario():
    jornaleros = requests.get(f"{BASE}/jornaleros/").json()
    usuario = jornaleros[0]["usuario"]

    payload = {"jornalero": usuario}
    r = requests.post(f"{BASE}/calendarios/", json=payload)
    assert r.status_code == 201


def test_incluir_periodo_en_calendario():
    calendarios = requests.get(f"{BASE}/calendarios/").json()
    id = calendarios[0]["id"]

    payload = {"fecha_inicio": "2025-02-01", "fecha_fin": "2025-02-05"}
    r = requests.post(f"{BASE}/calendarios/{id}/incluir_periodo/", json=payload)
    assert r.status_code == 200


def test_quitar_periodo_en_calendario():
    calendarios = requests.get(f"{BASE}/calendarios/").json()
    id = calendarios[0]["id"]

    payload = {"fecha_inicio": "2025-02-02", "fecha_fin": "2025-02-03"}
    r = requests.post(f"{BASE}/calendarios/{id}/quitar_periodo/", json=payload)
    assert r.status_code == 200
