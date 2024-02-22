from django.urls import path, include
from . import views
from rest_framework import routers

from .admin import admin_site

routers = routers.DefaultRouter()
routers.register('patient', views.PatientViewSet, basename='patient')
routers.register('doctor', views.DoctorViewSet, basename='doctor')
routers.register('medicine', views.MedicineViewSet, basename='medicine')
routers.register('user', views.UserViewSet, basename='user')
routers.register('appointment', views.AppointmentViewSet, basename='appointment')
routers.register('prescription', views.PrescriptionViewSet, basename='prescription')
routers.register('receipt', views.ReceiptViewSet, basename='receipt')

urlpatterns = [
    path('', include(routers.urls)),
    path('admin/', admin_site.urls)
]
