from django.urls import path, include
from . import views
from rest_framework import routers

routers = routers.DefaultRouter()
routers.register('patient', views.PatientViewSet)

urlpatterns = [
    # path('', views.index, name="index"),
    path('', include(routers.urls)),

    # path('patient/<int:patient_id>', views.details)
]
