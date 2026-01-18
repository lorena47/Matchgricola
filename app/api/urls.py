from rest_framework import routers
from django.urls import path
from .views import JornaleroViewSet, PropietarioViewSet, PeriodoViewSet, CalendarioViewSet, OfertaViewSet, SuscripcionViewSet, LoginView

router = routers.DefaultRouter()
router.register(r'jornaleros', JornaleroViewSet, basename='jornalero')
router.register(r'propietarios', PropietarioViewSet, basename='propietario')
router.register(r'periodos', PeriodoViewSet, basename='periodo')
router.register(r'calendarios', CalendarioViewSet, basename='calendario')
router.register(r'ofertas', OfertaViewSet, basename='oferta')
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')

urlpatterns = [
    path("login/", LoginView.as_view()),
] + router.urls