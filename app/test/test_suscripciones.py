import pytest
from app import models

@pytest.fixture
def propietario():
    propietario = models.Propietario.crear(
        nombre="Lorena",
        correo="lorenaPRO@gmail.com",
        usuario="lorenaPRO",
        contrasena="pro"
    )

    models.Oferta.crear(
        titulo="Cortar espárragos", 
        descripcion="Se requiere de un jornalero para abarcar tres alanzadas diarias",
        diaInicio=3, mesInicio=3, anoInicio=2026,
        diaFin=3, mesFin=6, anoFin=2026,
        plazas=1, eurosHora=8,
        propietario=propietario
    )
    
    models.Oferta.crear(
        titulo="Coger aceitunas", 
        descripcion="Se requiere de un jornalero para 6h diarias",
        diaInicio=15, mesInicio=10, anoInicio=2026,
        diaFin=15, mesFin=11, anoFin=2026,
        plazas=1, eurosHora=10,
        propietario=propietario
    )

    return propietario

@pytest.fixture
def jornalero():
    jornalero = models.Jornalero.crear(
        nombre="Lorena",
        correo="lorenaJOR@gmail.com",
        usuario="lorenaJOR",
        contrasena="jor"
    )
    models.Calendario.crear(jornalero)
    jornalero.calendario.incluirPeriodo(3, 3, 2026, 3, 6, 2026)
    return jornalero

@pytest.fixture
def suscripcion(jornalero, propietario):
    oferta = propietario.getOferta(0)
    suscripcion = jornalero.suscribir(oferta)
    return suscripcion


##################################################################################################
# HU4. Como jornalero, debo ver en mi inicio ofertas que se adecúen a mi disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_ver_ofertas(jornalero, propietario):
    ofertas = propietario.getOfertas()
    oferta1, oferta2 = ofertas
    disponibles = models.obtenerOfertasDisponibles(jornalero)
    assert len(disponibles) == 1
    assert oferta1 in disponibles
    assert not oferta2 in disponibles


##################################################################################################
# HU5. Como jornalero, debo poder suscribirme a la oferta que me interese.
##################################################################################################

@pytest.mark.django_db
def test_suscribir_ofertas(suscripcion):
    assert suscripcion.id is not None
    assert models.Suscribir.existe(suscripcion.id)
    suscripcion.jornalero.calendario.quitarPeriodo(3, 4, 2026, 3, 5, 2026)
    suscripcion.actualizar()
    assert suscripcion.activa == False


##################################################################################################
# HU6. Como propietario, debo poder ver las suscripciones a mi oferta.
##################################################################################################

@pytest.mark.django_db
def test_ver_suscripciones(propietario, suscripcion, jornalero):
    oferta = propietario.getOferta(0)
    suscripciones = oferta.getSuscripciones()
    assert len(suscripciones) == 1
    assert suscripciones[0] == suscripcion
    assert suscripciones[0].jornalero == jornalero


##################################################################################################
# HU7. Como propietario, debo poder aceptar la suscripción a una oferta.
##################################################################################################

@pytest.mark.django_db
def test_aceptar_suscripcion(propietario, suscripcion, jornalero):
    trabajo = propietario.aceptarSuscripcion(suscripcion)
    suscripcion.actualizar()
    assert trabajo.id is not None
    assert models.Trabajar.existe(trabajo.id)
    assert suscripcion.oferta.plazas == 0
    trabajadores = suscripcion.oferta.getTrabajadores()
    assert len(trabajadores) == 1
    assert trabajadores[0].jornalero == jornalero
    oferta = propietario.getOferta(0)
    assert oferta.plazas == 0
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 1
    assert trabajos[0].oferta == oferta
    assert suscripcion.activa == False


##################################################################################################
# HU8. Como propietario, debo poder rechazar la suscripción a una oferta.
##################################################################################################

@pytest.mark.django_db
def test_rechazar_suscripcion(propietario, suscripcion, jornalero):
    suscripcion.cancelar()
    suscripcion.actualizar()
    assert suscripcion.oferta.plazas == 1
    trabajadores = suscripcion.oferta.getTrabajadores()
    assert len(trabajadores) == 0
    oferta = propietario.getOferta(0)
    assert oferta.plazas == 1
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 0
    assert suscripcion.activa == False