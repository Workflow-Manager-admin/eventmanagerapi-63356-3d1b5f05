from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, EventViewSet, UserViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('health/', health, name='Health'),
    path('', include(router.urls)),
]
