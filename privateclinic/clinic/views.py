from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponse
from django.shortcuts import render
from .models import Patient, Doctor, Nurse, User, Medicine, Prescription, Appointment
from rest_framework import viewsets, permissions, generics, parsers, status
from .serializers import PatientSerializer
from . import serializers, paginator, perms
from rest_framework.decorators import action, permission_classes
from django.contrib.auth.decorators import permission_required
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
import cloudinary.uploader


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]


def index(request):
    return HttpResponse("This is Private Clinic")


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, PermissionRequiredMixin):
    queryset = User.objects.filter(is_active=True).all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    # permission_required = ("blog.view_post", "blog.add_post")

    def get_permissions(self):
        # if self.request.method == "GET":
        #     return [permissions.IsAdminUser(), ]
        if self.action.__eq__('update_user'):
            return [perms.AccountOwnerAuthenticated()]
        elif self.action.__eq__('profile'):
            return [perms.AccountOwnerAuthenticated()]
        return [permissions.IsAuthenticated()]

    @action(methods=['post'], url_path='register', detail=False)
    def register_user(self, request):
        try:
            data = request.data
            avatar = request.data.get("avatar")
            # upload file
            new_avatar = cloudinary.uploader.upload(avatar)
            new_user = User.objects.create_user(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password"),
                avatar=new_avatar['secure_url'],
            )
            Group.objects.get(name='PATIENT').user_set.add(new_user)
            return Response(data=serializers.UserSerializer(new_user, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")

    @action(methods=['patch'], url_path='update', url_name='update', detail=True)
    def update_user(self, request, pk):
        try:
            user_before = self.get_object()
            avatar_file = request.data.get("avatar")
            for fields, value in request.data.items():
                setattr(user_before, fields, value)
            if avatar_file:
                new_avatar = cloudinary.uploader.upload(avatar_file)
                user_before.avatar = new_avatar['secure_url']
            user_before.save()
            return Response(data=serializers.UserSerializer(user_before, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_403_FORBIDDEN)

    @action(methods=['get'], url_path='profile', detail=True)
    def profile(self, request, pk):
        try:
            user = self.get_object()
            detail_user = serializers.UserSerializer(user, context={'request': request}).data
            return Response(data=detail_user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_403_FORBIDDEN)

