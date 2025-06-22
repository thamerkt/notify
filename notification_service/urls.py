from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

# Création d'un router pour gérer automatiquement les endpoints
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename="notifications")

urlpatterns = [
    path('', include(router.urls)),  # Inclure toutes les routes du ViewSet
]
