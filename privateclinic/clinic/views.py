from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponse
from django.shortcuts import render
from .models import Patient
from rest_framework import viewsets, permissions
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]


def index(request):
    return HttpResponse("This is Private Clinic")


# def login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request,
#                         username=username,
#                         password=password)
#     if user is not None:
#         login(request, user)
#
#     else:
#         pass
#
#
# def logout_view(request):
#     logout(request)

# def details(request, patient_id):
#     try:
#         patient = Patient.objects.get(pk=patient_id)
#     except Patient.DoesNotExists:
#         return HttpResponseNotFound("<h1>Page Not Found</h1>")
#
#     return render(request, 'patient/detail.html', {'patient': patient})
