from django.urls import path, include
from . import views
from rest_framework import routers

routers = routers.DefaultRouter()
routers.register('patient', views.PatientViewSet, basename='patient')
routers.register('medicine', views.MedicineViewSet, basename='medicine')
routers.register('user', views.UserViewSet, basename='user')
routers.register('appointment', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(routers.urls)),
]
