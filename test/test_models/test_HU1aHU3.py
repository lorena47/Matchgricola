import pytest
from app.base.models import usuario, oferta, calendario
from datetime import date #date(yyyy, mm, dd)

@pytest.fixture
def propietario():
    propietario = usuario.Propietario.crear(
        nombre="Lorena",
        correo="lorenaPRO@gmail.com",
        usuario="lorenaPRO",
        contrasenia="pro"
    )
    return propietario

@pytest.fixture
def fechasOfertas(): 
    return {
        "inicioOferta1": date(2026, 3, 3),
        "finOferta1": date(2026, 6, 3),
        "inicioOferta2": date(2026, 10, 15),
        "finOferta2": date(2026, 11, 15),
    }

@pytest.fixture
def ofertas(propietario, fechasOfertas):
    oferta1 = oferta.Oferta.crear(
        titulo="Cortar espárragos", 
        descripcion="Se requiere a un jornalero para abarcar tres alanzadas diarias",
        fechaInicio=fechasOfertas["inicioOferta1"],
        fechaFin=fechasOfertas["finOferta1"],
        plazas=1, eurosHora=8,
        propietario=propietario
    )
    
    oferta2 = oferta.Oferta.crear(
        titulo="Coger aceitunas", 
        descripcion="Se requiere a un jornalero para 6h diarias",
        fechaInicio=fechasOfertas["inicioOferta2"],
        fechaFin=fechasOfertas["finOferta2"],
        plazas=1, eurosHora=10,
        propietario=propietario
    )
    
    return oferta1, oferta2

@pytest.fixture
def jornalero():
    jornalero = usuario.Jornalero.crear(
        nombre="Lorena",
        correo="lorenaJOR@gmail.com",
        usuario="lorenaJOR",
        contrasenia="jor"
    )
    jornalero.tenerCalendario()
    return jornalero

@pytest.fixture
def calendarioJornalero(jornalero):
    calendarioJornalero = jornalero.getCalendario()
    return calendarioJornalero


##################################################################################################
# HU1. Como propietario, debo poder hacer una propuesta de trabajo para un período determinado.
##################################################################################################

@pytest.mark.django_db
def test_crear_propietario(propietario):
    assert usuario.Propietario.existe(propietario.usuario)

@pytest.mark.django_db
def test_crear_oferta(ofertas):
    oferta1, oferta2 = ofertas
    assert oferta.Oferta.existe(oferta1.id)
    assert oferta.Oferta.existe(oferta2.id)

@pytest.mark.django_db
def test_propietario_propone_ofertas(propietario, ofertas):    
    oferta1, oferta2 = ofertas
    propietario_ofertas = propietario.getOfertas()
    assert len(propietario_ofertas) == 2
    assert oferta1 in propietario_ofertas
    assert oferta2 in propietario_ofertas


##################################################################################################
# HU2. Como jornalero, debo poder tener un calendarioJornalero de disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_crear_jornalero(jornalero):
    assert usuario.Jornalero.existe(jornalero.usuario)

@pytest.mark.django_db
def test_jornalero_tiene_calendario(calendarioJornalero):
    assert calendario.Calendario.existe(calendarioJornalero.id)


##################################################################################################
# HU3. Como jornalero, debo poder editar mi calendarioJornalero de disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_incluir_periodo(calendarioJornalero):
    calendarioJornalero.incluirPeriodo(date(2026, 3, 3), date(2026, 6, 3))

    assert calendarioJornalero.numeroPeriodos() == 1
    periodo = calendarioJornalero.getPeriodo(0)
    fechaInicio = periodo.getInicio()
    fechaFin = periodo.getFin()
    assert fechaInicio.day == 3
    assert fechaInicio.month == 3
    assert fechaInicio.year == 2026
    assert fechaFin.day == 3
    assert fechaFin.month == 6
    assert fechaFin.year == 2026

@pytest.mark.django_db
def test_fusion(calendarioJornalero):
    calendarioJornalero.incluirPeriodo(date(2026, 3, 3), date(2026, 6, 3))

    # Período incluido en el anterior
    calendarioJornalero.incluirPeriodo(date(2026, 4, 3), date(2026, 5, 3))
    assert calendarioJornalero.numeroPeriodos() == 1
    periodo = calendarioJornalero.getPeriodo(0)
    fechaInicio = periodo.getInicio()
    fechaFin = periodo.getFin()
    assert fechaInicio.day == 3
    assert fechaInicio.month == 3
    assert fechaInicio.year == 2026
    assert fechaFin.day == 3
    assert fechaFin.month == 6
    assert fechaFin.year == 2026

    # Período comienza un día después que el anterior
    calendarioJornalero.incluirPeriodo(date(2026, 6, 4), date(2026, 6, 4))
    assert calendarioJornalero.numeroPeriodos() == 1
    periodo = calendarioJornalero.getPeriodo(0)
    fechaInicio = periodo.getInicio()
    fechaFin = periodo.getFin()
    assert fechaInicio.day == 3
    assert fechaInicio.month == 3
    assert fechaInicio.year == 2026
    assert fechaFin.day == 4
    assert fechaFin.month == 6
    assert fechaFin.year == 2026

    # Período comparte sus días iniciales con el anterior
    calendarioJornalero.incluirPeriodo(date(2026, 5, 3), date(2026, 7, 3))
    assert calendarioJornalero.numeroPeriodos() == 1
    periodo = calendarioJornalero.getPeriodo(0)
    fechaInicio = periodo.getInicio()
    fechaFin = periodo.getFin()
    assert fechaInicio.day == 3
    assert fechaInicio.month == 3
    assert fechaInicio.year == 2026
    assert fechaFin.day == 3
    assert fechaFin.month == 7
    assert fechaFin.year == 2026

    # Período comparte sus días finales con el anterior
    calendarioJornalero.incluirPeriodo(date(2026, 2, 3), date(2026, 4, 3))
    assert calendarioJornalero.numeroPeriodos() == 1
    periodo = calendarioJornalero.getPeriodo(0)
    fechaInicio = periodo.getInicio()
    fechaFin = periodo.getFin()
    assert fechaInicio.day == 3
    assert fechaInicio.month == 2
    assert fechaInicio.year == 2026
    assert fechaFin.day == 3
    assert fechaFin.month == 7
    assert fechaFin.year == 2026

@pytest.mark.django_db
def test_disponibilidad(calendarioJornalero):
    calendarioJornalero.incluirPeriodo(date(2026, 3, 3), date(2026, 6, 3))
    calendarioJornalero.incluirPeriodo(date(2026, 6, 5), date(2026, 7, 5))
    calendarioJornalero.incluirPeriodo(date(2026, 7, 6), date(2026, 8, 6))

    assert calendarioJornalero.disponible(date(2026, 3, 3), date(2026, 6, 3)) == True
    assert calendarioJornalero.disponible(date(2026, 6, 4), date(2026, 7, 4)) == False
    assert calendarioJornalero.disponible(date(2026, 6, 5), date(2026, 7, 5)) == True
    assert calendarioJornalero.disponible(date(2026, 7, 6), date(2026, 6, 8)) == True
    assert calendarioJornalero.disponible(date(2026, 3, 3), date(2026, 8, 6)) == False
    assert calendarioJornalero.disponible(date(2026, 6, 5), date(2026, 8, 6)) == True

@pytest.mark.django_db
def test_quitar_periodo(calendarioJornalero):
    calendarioJornalero.incluirPeriodo(date(2026, 1, 1),  date(2026, 1, 31))
    calendarioJornalero.incluirPeriodo(date(2026, 3, 1),  date(2026, 3, 31))
    calendarioJornalero.incluirPeriodo(date(2026, 5, 1),  date(2026, 5, 31))
    calendarioJornalero.incluirPeriodo(date(2026, 7, 1),  date(2026, 7, 31))
    calendarioJornalero.incluirPeriodo(date(2026, 8, 1),  date(2026, 8, 31))
    
    # Periodo que se quita está incluido en uno disponible
    calendarioJornalero.quitarPeriodo(date(2026, 1, 5), date(2026, 1, 15))

    assert calendarioJornalero.disponible(date(2026, 1, 1),  date(2026, 1, 4))  == True
    assert calendarioJornalero.disponible(date(2026, 1, 2),  date(2026, 1, 5))  == False
    assert calendarioJornalero.disponible(date(2026, 1, 5),  date(2026, 1, 10)) == False
    assert calendarioJornalero.disponible(date(2026, 1, 12), date(2026, 1, 17)) == False
    assert calendarioJornalero.disponible(date(2026, 1, 15), date(2026, 1, 19)) == False
    assert calendarioJornalero.disponible(date(2026, 1, 20), date(2026, 1, 27)) == True

    # Periodo que se quita incluye a uno disponible
    calendarioJornalero.quitarPeriodo(date(2026, 2, 28), date(2026, 4, 2))

    assert calendarioJornalero.disponible(date(2026, 2, 28), date(2026, 3, 1))  == False
    assert calendarioJornalero.disponible(date(2026, 3, 5),  date(2026, 3, 15)) == False
    assert calendarioJornalero.disponible(date(2026, 3, 25), date(2026, 4, 2))  == False

    # Periodo que se quita es uno disponible
    calendarioJornalero.quitarPeriodo(date(2026, 5, 1), date(2026, 5, 31))

    assert calendarioJornalero.disponible(date(2026, 5, 1),  date(2026, 5, 1))  == False
    assert calendarioJornalero.disponible(date(2026, 5, 31), date(2026, 5, 31)) == False
    assert calendarioJornalero.disponible(date(2026, 5, 2),  date(2026, 5, 30)) == False

    # Periodo que se quita comparte sus días finales con uno disponible
    calendarioJornalero.quitarPeriodo(date(2026, 6, 22), date(2026, 7, 7))

    assert calendarioJornalero.disponible(date(2026, 7, 1),  date(2026, 7, 5))  == False
    assert calendarioJornalero.disponible(date(2026, 7, 7),  date(2026, 7, 11)) == False
    assert calendarioJornalero.disponible(date(2026, 7, 13), date(2026, 7, 20)) == True

    # Periodo que se quita comparte sus días iniciales con uno disponible
    calendarioJornalero.quitarPeriodo(date(2026, 8, 15), date(2026, 9, 6))

    assert calendarioJornalero.disponible(date(2026, 7, 28), date(2026, 8, 3))  == True
    assert calendarioJornalero.disponible(date(2026, 8, 15), date(2026, 8, 17)) == False
    assert calendarioJornalero.disponible(date(2026, 8, 20), date(2026, 8, 25)) == False


##################################################################################################
# HU19. Como administrador, debo poder eliminar un perfil.
##################################################################################################

@pytest.mark.django_db
def test_eliminar_propietario(propietario, ofertas):
    oferta1, oferta2 = ofertas
    assert oferta.Oferta.existe(oferta1.id)
    assert oferta.Oferta.existe(oferta2.id)
    assert usuario.Propietario.existe(propietario.usuario)
    propietario.borrar()
    assert not usuario.Propietario.existe(propietario.usuario)
    assert not oferta.Oferta.existe(oferta1.id)
    assert not oferta.Oferta.existe(oferta2.id)

@pytest.mark.django_db
def test_eliminar_jornalero(jornalero, calendarioJornalero):
   assert usuario.Jornalero.existe(jornalero.usuario)
   assert calendario.Calendario.existe(calendarioJornalero.id)
   jornalero.borrar()
   assert not usuario.Jornalero.existe(jornalero.usuario)
   assert not calendario.Calendario.existe(calendarioJornalero.id)

##################################################################################################
# HU20. Como administrador, debo poder eliminar una oferta.
##################################################################################################

@pytest.mark.django_db
def test_eliminar_oferta(propietario, ofertas):
    oferta1, oferta2 = ofertas
    assert usuario.Propietario.existe(propietario.usuario)
    assert oferta.Oferta.existe(oferta1.id)
    assert oferta.Oferta.existe(oferta2.id)
    oferta2.borrar()
    assert usuario.Propietario.existe(propietario.usuario)
    assert oferta.Oferta.existe(oferta1.id)
    assert not oferta.Oferta.existe(oferta2.id)

@pytest.mark.django_db
def test_eliminar_calendario(jornalero, calendarioJornalero):
   assert usuario.Jornalero.existe(jornalero.usuario)
   assert calendario.Calendario.existe(calendarioJornalero.id)
   calendarioJornalero.borrar()
   assert usuario.Jornalero.existe(jornalero.usuario)
   assert not calendario.Calendario.existe(calendarioJornalero.id)