from rest_framework import routers
from .views import JornaleroViewSet, PropietarioViewSet, PeriodoViewSet, CalendarioViewSet

router = routers.DefaultRouter()
router.register(r'jornaleros', JornaleroViewSet, basename='jornalero')
router.register(r'propietarios', PropietarioViewSet, basename='propietario')
router.register(r'periodos', PeriodoViewSet, basename='periodo')
router.register(r'calendarios', CalendarioViewSet, basename='calendario')
urlpatterns = router.urls