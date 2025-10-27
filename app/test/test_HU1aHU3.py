import pytest
from app import models

##################################################################################################
# SEGUNDA ITERACIÓN
##################################################################################################

##################################################################################################
# HU1. Como propietario, debo poder hacer una propuesta de trabajo para un período determinado.
##################################################################################################

@pytest.fixture
def propietario():
    propietario = models.Propietario.crear(
        nombre="Lorena",
        correo="lorenaPRO@gmail.com"
    )
    return propietario

@pytest.mark.django_db
def test_crear_propietario(propietario):
    assert propietario.id is not None
    assert models.Propietario.objects.filter(id=propietario.id).exists()

@pytest.fixture
def ofertas(propietario):
    oferta1 = models.Oferta.crear(
        titulo="Cortar espárragos", 
        descripcion="Se requiere de un jornalero para abarcar tres alanzadas diarias",
        diaInicio=3, mesInicio=3, anoInicio=2026,
        diaFin=3, mesFin=6, anoFin=2026,
        plazas=1, eurosHora=8,
        propietario=propietario
    )
    
    oferta2 = models.Oferta.crear(
        titulo="Coger aceitunas", 
        descripcion="Se requiere de un jornalero para 6h diarias",
        diaInicio=15, mesInicio=10, anoInicio=2026,
        diaFin=15, mesFin=11, anoFin=2026,
        plazas=1, eurosHora=10,
        propietario=propietario
    )
    
    return oferta1, oferta2

@pytest.mark.django_db
def test_propietario_propone_ofertas(propietario, ofertas):    
    oferta1, oferta2 = ofertas
    propietario_ofertas = list(propietario.ofertas.all())
    assert len(propietario_ofertas) == 2
    assert oferta1 in propietario_ofertas
    assert oferta2 in propietario_ofertas

@pytest.mark.django_db
def test_eliminar_propietario(propietario, ofertas):
    oferta1, oferta2 = ofertas
    assert models.Oferta.objects.filter(id=oferta1.id).exists()
    assert models.Oferta.objects.filter(id=oferta2.id).exists()
    propietario.delete()
    assert not models.Oferta.objects.filter(id=oferta1.id).exists()
    assert not models.Oferta.objects.filter(id=oferta2.id).exists()

##################################################################################################
# HU2. Como jornalero, debo poder tener un calendario de disponibilidad.
##################################################################################################

@pytest.fixture
def jornalero():
    jornalero = models.Jornalero.crear(
        nombre="Lorena",
        correo="lorenaJOR@gmail.com"
    )
    return jornalero

@pytest.mark.django_db
def test_crear_jornalero(jornalero):
    assert jornalero.id is not None
    assert models.Jornalero.objects.filter(id=jornalero.id).exists()

@pytest.mark.django_db
def test_jornalero_tiene_calendario(jornalero):
    assert jornalero.calendario is not None
    assert models.Calendario.objects.filter(id=jornalero.calendario.id).exists()

#@pytest.mark.django_db
#def test_eliminar_jornalero(jornalero):
#    calendario_id = jornalero.calendario.id
#    assert models.Calendario.objects.filter(id=calendario_id).exists()
#    jornalero.delete()
#    assert not models.Calendario.objects.filter(id=calendario_id).exists()

##################################################################################################
# PRIMERA ITERACIÓN
##################################################################################################

##################################################################################################
# HU1. Como propietario, debo poder hacer una propuesta de trabajo para un período determinado.
##################################################################################################

@pytest.mark.django_db
def test_crear_oferta():
    #Segunda iteración
    propietario = models.Propietario.crear(
        nombre="Lorena",
        correo="lorenaPRO@gmail.com"
    )

    oferta = models.Oferta.crear(
        titulo="Cortar espárragos", 
        descripcion="Se requiere de un jornalero para abarcar tres alanzadas diarias", diaInicio=3, mesInicio=3, anoInicio=2026,
        diaFin=3, mesFin=6, anoFin=2026,
        plazas=1, eurosHora=8,
        propietario=propietario # Segunda iteración
    )

    assert oferta.id is not None
    assert models.Oferta.objects.filter(id=oferta.id).exists()

##################################################################################################
# HU2. Como jornalero, debo poder tener un calendario de disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_crear_calendario():
    calendario = models.Calendario.crear()
    
    assert calendario.id is not None
    assert models.Calendario.objects.filter(id=calendario.id).exists()

##################################################################################################
# HU3. Como jornalero, debo poder editar mi calendario de disponibilidad.
##################################################################################################

@pytest.mark.django_db
def test_incluir_periodo():
    calendario = models.Calendario.crear()
    calendario.incluirPeriodo(3, 3, 2026, 3, 6, 2026)
    
    assert calendario.periodos.count() == 1
    periodo = calendario.periodos.first()
    assert periodo.fecha_inicio.day == 3
    assert periodo.fecha_inicio.month == 3
    assert periodo.fecha_inicio.year == 2026
    assert periodo.fecha_fin.day == 3
    assert periodo.fecha_fin.month == 6
    assert periodo.fecha_fin.year == 2026

@pytest.mark.django_db
def test_fusion():
    calendario = models.Calendario.crear()
    calendario.incluirPeriodo(3, 3, 2026, 3, 6, 2026)
    calendario.incluirPeriodo(4, 6, 2026, 4, 7, 2026)
    
    assert calendario.periodos.count() == 1
    periodo = calendario.periodos.first()
    assert periodo.fecha_inicio.day == 3
    assert periodo.fecha_inicio.month == 3
    assert periodo.fecha_inicio.year == 2026
    assert periodo.fecha_fin.day == 4
    assert periodo.fecha_fin.month == 7
    assert periodo.fecha_fin.year == 2026

@pytest.mark.django_db
def test_disponibilidad():
    calendario = models.Calendario.crear()
    calendario.incluirPeriodo(3, 3, 2026, 3, 6, 2026)
    calendario.incluirPeriodo(4, 6, 2026, 4, 7, 2026)

    assert calendario.disponible(3, 3, 2026, 10, 6, 2026) == True
    assert calendario.disponible(10, 6, 2026, 4, 7, 2026) == True
    assert calendario.disponible(3, 3, 2026, 10, 7, 2026) == False
    assert calendario.disponible(2, 3, 2026, 4, 7, 2026) == False
    assert calendario.disponible(3, 3, 2026, 4, 7, 2026) == True

@pytest.mark.django_db
def test_quitar_periodo():
    calendario = models.Calendario.crear()
    calendario.incluirPeriodo(1, 1, 2026,31, 1, 2026)
    calendario.incluirPeriodo(1, 3, 2026, 31, 3, 2026)
    calendario.incluirPeriodo(1, 5, 2026, 31, 5, 2026)
    calendario.incluirPeriodo(1, 7, 2026, 31, 7, 2026)
    calendario.incluirPeriodo(1, 8, 2026, 31, 8, 2026)
    
    # Periodo que se quita está incluido en uno disponible
    calendario.quitarPeriodo(5,1,2026,15,1,2026)
    assert calendario.disponible(1,1,2026,4,1,2026) == True
    assert calendario.disponible(2,1,2026,5,1,2026) == False
    assert calendario.disponible(5,1,2026,10,1,2026) == False
    assert calendario.disponible(12,1,2026,17,1,2026) == False
    assert calendario.disponible(15,1,2026,19,1,2026) == False
    assert calendario.disponible(20,1,2026,27,1,2026) == True

    # Periodo que se quita incluye a uno disponible
    calendario.quitarPeriodo(28,2,2026,2,4,2026)
    assert calendario.disponible(28,2,2026,1,3,2026) == False
    assert calendario.disponible(5,3,2026,15,3,2026) == False
    assert calendario.disponible(25,3,2026,2,4,2026) == False

    # Periodo que se quita es uno disponible
    calendario.quitarPeriodo(1,5,2026,31,5,2026)
    assert calendario.disponible(1,5,2026,1,5,2026) == False
    assert calendario.disponible(31,5,2026,31,5,2026) == False
    assert calendario.disponible(2,5,2026,30,5,2026) == False

    # Periodo que se quita comparte sus días finales con uno disponible
    calendario.quitarPeriodo(22,6,2026,7,7,2026)
    assert calendario.disponible(1,7,2026,5,7,2026) == False
    assert calendario.disponible(7,7,2026,11,7,2026) == False
    assert calendario.disponible(13,7,2026,20,7,2026) == True

    # Periodo que se quita comparte sus días iniciales con uno disponible
    calendario.quitarPeriodo(15,8,2026,6,9,2026)
    assert calendario.disponible(28,7,2026,3,8,2026) == True
    assert calendario.disponible(15,8,2026,17,8,2026) == False
    assert calendario.disponible(20,8,2026,25,8,2026) == False
