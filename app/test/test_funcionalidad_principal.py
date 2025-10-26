import pytest

@pytest.mark.django_db
# Como propietario, debo poder hacer una propuesta de trabajo para un período determinado.
def test_HU1():
    oferta = Oferta.crear(titulo="Cortar espárragos", 
        descripcion="Se requiere de un jornalero para abarcar tres alanzadas diarias", diaInicio=3, mesInicio=3, añoInicio=2026,
        diaFin=3, mesFin=6, añoFin=2026,
        plazas=1, eurosHora=8)

    assert oferta.id is not None
    assert Oferta.objects.filter(id=oferta.id).exists()
    

@pytest.mark.django_db
# Como jornalero, debo poder tener un calendario de disponibilidad.
def test_HU2():
    calendario = Calendario.crear()
    
    assert calendario.id is not None
    assert Calendario.objects.filter(id=calendario.id).exists()

@pytest.mark.django_db
# Como jornalero, debo poder editar mi calendario de disponibilidad.
def test_HU3():
    calendario = Calendario.crear()
    calendario.incluirPeriodo(diaInicio=3, mesInicio=3, añoInicio=2026,
        diaFin=3, mesFin=6, añoFin=2026)
    
    assert calendario.disponible(3,3,2026,10,3,2026) == True
    assert calendario.disponible(2,3,2026,10,3,2026) == False
    assert calendario.disponible(3,3,2026,10,6,2026) == False
