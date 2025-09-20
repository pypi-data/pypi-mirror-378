from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('networks', views.ZwaveNetworkViewSet)
router.register('devices', views.ZwaveDeviceViewSet)
router.register('command-classes', views.ZwaveCommandClassViewSet)
router.register('associations', views.ZwaveAssociationViewSet)

app_name = 'netbox_zwave-api'
urlpatterns = [
    path('', include(router.urls)),
]
