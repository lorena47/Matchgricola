import pytest
from app.base.models import usuario, oferta, calendario, suscripcion
from datetime import date #date(yyyy, mm, dd)

@pytest.fixture
def fechasOfertas(): 
    return {
        "inicioOferta1": date(2026, 3, 3),
        "finOferta1": date(2026, 6, 3),
        "inicioOferta2": date(2026, 10, 15),
        "finOferta2": date(2026, 11, 15),
        "inicioOferta3": date(2026, 1, 15),
        "finOferta3": date(2026, 5, 31),
    }

@pytest.fixture
def propietario(fechasOfertas):
    propietario = usuario.Propietario.crear(
        nombre="Lorena",
        correo="lorenaPRO@gmail.com",
        usuario="lorenaPRO",
        contrasenia="pro"
    )

    oferta.Oferta.crear(
        titulo="Cortar espárragos", 
        descripcion="Se requiere a un jornalero para abarcar tres alanzadas diarias",
        fechaInicio=fechasOfertas["inicioOferta1"],
        fechaFin=fechasOfertas["finOferta1"],
        plazas=1, eurosHora=8,
        propietario=propietario
    )
    
    oferta.Oferta.crear(
        titulo="Coger aceitunas", 
        descripcion="Se requiere a un jornalero para 6h diarias",
        fechaInicio=fechasOfertas["inicioOferta2"],
        fechaFin=fechasOfertas["finOferta2"],
        plazas=1, eurosHora=10,
        propietario=propietario
    )

    oferta.Oferta.crear(
        titulo="Quemar rastrojos", 
        descripcion="Se requiere a un jornalero para 6h diarias",
        fechaInicio=fechasOfertas["inicioOferta3"],
        fechaFin=fechasOfertas["finOferta3"],
        plazas=1, eurosHora=10,
        propietario=propietario
    )

    return propietario

@pytest.fixture
def jornalero(fechasOfertas):
    jornalero = usuario.Jornalero.crear(
        nombre="Lorena",
        correo="lorenaJOR@gmail.com",
        usuario="lorenaJOR",
        contrasenia="jor"
    )
    jornalero.tenerCalendario()
    calendarioJornalero = jornalero.getCalendario()
    calendarioJornalero.incluirPeriodo(fechasOfertas["inicioOferta1"], fechasOfertas["finOferta1"])
    calendarioJornalero.incluirPeriodo(fechasOfertas["inicioOferta2"], fechasOfertas["finOferta2"])
    return jornalero

@pytest.fixture
def suscripcionJornalero(jornalero, propietario):
    oferta = propietario.getOferta(0)
    suscripcionJornalero = jornalero.suscribir(oferta)
    return suscripcionJornalero

@pytest.fixture
def suscripcionPropietario(propietario, jornalero):
    oferta = propietario.getOferta(1)
    suscripcionPropietario = propietario.proponer(oferta, jornalero)
    return suscripcionPropietario


##################################################################################################
# HU4. Como jornalero, debo ver en mi inicio ofertas que se adecúen a mi disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_ver_ofertas(jornalero, propietario):
    ofertas = propietario.getOfertas()
    oferta1, oferta2, oferta3 = ofertas
    disponibles = jornalero.getOfertasDisponibles()
    assert len(disponibles) == 2
    assert oferta1 in disponibles
    assert oferta2 in disponibles
    assert not oferta3 in disponibles


##################################################################################################
# HU5. Como jornalero, debo poder suscribirme a la oferta que me interese.
##################################################################################################

@pytest.mark.django_db
def test_suscribir_ofertas(suscripcionJornalero, jornalero):
    assert suscripcion.Suscripcion.existe(suscripcionJornalero.id)
    ##############################################################################################
    # Como jornalero, debo poder cancelar mi suscripción.
    ##############################################################################################
    jornalero.cancelarSuscripcion(suscripcionJornalero)
    assert not suscripcion.Suscripcion.existe(suscripcionJornalero.id)


##################################################################################################
# HU6. Como propietario, debo poder ver las suscripciones a mi oferta.
##################################################################################################

@pytest.mark.django_db
def test_ver_suscripciones(propietario, suscripcionJornalero, jornalero):
    oferta = propietario.getOferta(0)
    suscripciones = oferta.getSuscripciones()
    assert len(suscripciones) == 1
    assert suscripciones[0] == suscripcionJornalero
    assert suscripciones[0].getJornalero() == jornalero


##################################################################################################
# HU7. Como propietario, debo poder aceptar la suscripción a una oferta.
##################################################################################################

@pytest.mark.django_db
def test_aceptar_suscripcion(propietario, suscripcionJornalero, jornalero):
    propietario.aceptarSuscripcion(suscripcionJornalero)
    suscripcionJornalero.actualizar()
    assert suscripcionJornalero.match() == True
    assert suscripcionJornalero.suscripcionActiva() == True
    assert suscripcionJornalero.getOferta().getPlazas() == 0
    trabajadores = suscripcionJornalero.getOferta().getTrabajadores()
    assert len(trabajadores) == 1
    assert trabajadores[0] == jornalero
    oferta = propietario.getOferta(0)
    assert oferta == suscripcionJornalero.getOferta()
    assert not jornalero.getCalendario().disponible(oferta.getPeriodo().getInicio(), oferta.getPeriodo().getFin())
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 1
    assert trabajos[0] == oferta


##################################################################################################
# HU8. Como propietario, debo poder rechazar la suscripción a una oferta.
##################################################################################################

@pytest.mark.django_db
def test_rechazar_suscripcion(propietario, suscripcionJornalero, jornalero):
    suscripcionJornalero.rechazar('propietario')
    suscripcionJornalero.actualizar()
    assert suscripcionJornalero.match() == False
    assert suscripcionJornalero.suscripcionActiva() == False
    assert suscripcionJornalero.getOferta().getPlazas() == 1
    trabajadores = suscripcionJornalero.getOferta().getTrabajadores()
    assert len(trabajadores) == 0
    oferta = propietario.getOferta(0)
    assert oferta == suscripcionJornalero.getOferta()
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 0


##################################################################################################
# HU9. Como propietario, debo ver en mi inicio jornaleros disponibles para mis ofertas.
##################################################################################################

@pytest.mark.django_db
def test_ver_jornaleros(jornalero, propietario):
    ofertas = propietario.getOfertas()
    oferta1, oferta2, oferta3 = ofertas
    disponibles = propietario.getJornalerosDisponibles()

    assert oferta1 in disponibles
    assert len(disponibles[oferta1]) == 1
    assert jornalero in disponibles[oferta1]

    assert oferta2 in disponibles
    assert len(disponibles[oferta2]) == 1
    assert jornalero in disponibles[oferta2]

    assert oferta3 in disponibles
    assert len(disponibles[oferta3]) == 0


##################################################################################################
# HU10. Como propietario, debo poder proponer mi oferta al jornalero que me interese.
##################################################################################################

@pytest.mark.django_db
def test_proponer_ofertas(suscripcionPropietario, propietario):
    assert suscripcion.Suscripcion.existe(suscripcionPropietario.id)
    ##############################################################################################
    # Como propietario, debo poder cancelar mi propuesta.
    ##############################################################################################
    propietario.cancelarSuscripcion(suscripcionPropietario)
    assert not suscripcion.Suscripcion.existe(suscripcionPropietario.id)


##################################################################################################
# HU11. Como jornalero, debo poder ver las propuestas de ofertas.
##################################################################################################

@pytest.mark.django_db
def test_ver_propuestas(jornalero, suscripcionPropietario, propietario):
    propuestas = jornalero.getPropuestas()
    assert len(propuestas) == 1
    assert propuestas[0].getOferta() == suscripcionPropietario.getOferta()
    assert propuestas[0].getOferta() == propietario.getOferta(1)


##################################################################################################
# HU12. Como jornalero, debo poder aceptar la propuesta de una oferta.
##################################################################################################

@pytest.mark.django_db
def test_aceptar_propuesta(jornalero, suscripcionPropietario, propietario):
    jornalero.aceptarPropuesta(suscripcionPropietario)
    suscripcionPropietario.actualizar()
    assert suscripcionPropietario.match() == True
    assert suscripcionPropietario.suscripcionActiva() == True
    assert suscripcionPropietario.getOferta().getPlazas() == 0
    trabajadores = suscripcionPropietario.getOferta().getTrabajadores()
    assert len(trabajadores) == 1
    assert trabajadores[0] == jornalero
    oferta = propietario.getOferta(1)
    assert oferta == suscripcionPropietario.getOferta()
    assert not jornalero.getCalendario().disponible(oferta.getPeriodo().getInicio(), oferta.getPeriodo().getFin())
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 1
    assert trabajos[0] == oferta
    propuestas = jornalero.getPropuestas()
    assert len(propuestas) == 0


##################################################################################################
# HU13. Como jornalero, debo poder rechazar la propuesta de una oferta.
##################################################################################################

@pytest.mark.django_db
def test_rechazar_propuesta(jornalero, suscripcionPropietario, propietario):
    suscripcionPropietario.rechazar('jornalero')
    suscripcionPropietario.actualizar()
    assert suscripcionPropietario.match() == False
    assert suscripcionPropietario.suscripcionActiva() == False
    assert suscripcionPropietario.getOferta().getPlazas() == 1
    trabajadores = suscripcionPropietario.getOferta().getTrabajadores()
    assert len(trabajadores) == 0
    oferta = propietario.getOferta(1)
    assert oferta == suscripcionPropietario.getOferta()
    trabajos = jornalero.getTrabajos()
    assert len(trabajos) == 0
    propuestas = jornalero.getPropuestas()
    assert len(propuestas) == 0