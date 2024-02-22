from django.contrib.auth import authenticate, logout, login
from django.core.mail import send_mail
from django.db.models import Sum, ExpressionWrapper, F, DecimalField
from django.http import HttpResponse
from django.shortcuts import render
from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, \
    DepartmentSchedule, PrescriptionMedicine
from rest_framework import viewsets, permissions, generics, parsers, status
from .serializers import PatientSerializer
from . import serializers, paginator, perms
from rest_framework.decorators import action, permission_classes
from django.contrib.auth.decorators import permission_required
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
import cloudinary.uploader
from functools import partial

MAX_PATIENT_PER_DAY = 100


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, PermissionRequiredMixin):
    queryset = User.objects.filter(is_active=True).all()
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action in ['profile', 'update_user']:
            return [perms.AccountOwnerAuthenticated()]
        elif self.action in ['register_user']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(methods=['get'], url_path='current-user', url_name='current-user', detail=False)
    def current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)

    @action(methods=['post'], url_path='register', detail=False)
    def register_user(self, request):
        try:
            data = request.data
            avatar = request.data.get("avatar")
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
            return Response(dict(error=e.__str__()), status=status.HTTP_403_FORBIDDEN)

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


# HUY's missing part
class AppointmentViewSet(viewsets.ViewSet):
    @action(methods=['GET'], detail=False, name="Confirm this appointment", url_name='confirm', url_path='confirm')
    def confirm(self, request):
        t = send_mail(
            subject="Appointment Comfirmation",
            message=f'''
           OKOK Em huy 
        ''',
            from_email='peteralwaysloveu@gmail.com',
            recipient_list=['2151013029huy@ou.edu.vn']
        )
        return Response({'success': 'OK'}, status=status.HTTP_200_OK)


class MedicineViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Medicine.objects.filter(active=True).all()
    serializer_class = serializers.MedicineListSerializer
    permission_classes = [partial(perms.IsInGroup, allowed_groups=['DOCTOR'])]

    def get_queryset(self):
        q = self.queryset
        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(name__icontains=kw)
        return q

    @action(methods=['get'], detail=False, url_path="hello")
    def hello(self, request):
        return Response({'ms': 'Hello'}, status=status.HTTP_200_OK)


class PrescriptionViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Prescription.objects.all()
    # permission_classes = [partial(perms.IsInGroup, allowed_groups=['DOCTOR'])]
    # serializer_class = serializers.PrescriptionSerializer

    def get_permissions(self):
        if self.action.__eq__('retrieve'):
            return [permissions.IsAuthenticated()]
        return [perms.IsInGroup(allowed_groups=['DOCTOR'])]

    def get_serializer_class(self):
        if self.action.__eq__('retrieve'):
            return serializers.PrescriptionDetailSerializer
        return serializers.PrescriptionSerializer

    @action(methods=['patch'], detail=True, url_path="add-medicine")
    def add_medicine(self, request, pk=None):
        try:
            prescription = self.get_object()
            medicine_id = request.data["medicine_id"]
            found_medicine = Medicine.objects.get(pk=medicine_id)
            dosage = request.data['dosage']
            quantity = request.data['quantity']
            pres, created = PrescriptionMedicine.objects.get_or_create(prescription=prescription,
                                                                       medicine=found_medicine, dosage=dosage,
                                                                       quantity=quantity)
            if created:
                res = {'message': "Add medicine successfully",
                       'prescription': serializers.PrescriptionMedicineSerializer(pres).data}
                return Response(data=res, status=status.HTTP_200_OK)
            else:
                return Response({"error": "This medicine has been added"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='make-receipt')
    def make_receipt(self, request, pk=None):
        prescription = self.get_object()

        total_medicine_cost = prescription.dosages.aggregate(
            total_cost=ExpressionWrapper(
                Sum(F('medicine__price') * F('quantity')),
                output_field=DecimalField()
            )
        )['total_cost']

        total_service_cost = prescription.services.aggregate(
            total_cost=Sum('price')
        )['total_cost']

        total = total_medicine_cost + total_service_cost

        receipt = Receipt.objects.create(
            prescription=prescription,
            total=total
        )
        data = serializers.ReceiptSerializer(receipt).data
        return Response(data=data, status=status.HTTP_201_CREATED)


class ReceiptViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer

    def get_permissions(self):
        if self.action in ['update_paid']:
            return [perms.IsInGroup(allowed_groups=['NURSE'])]
        return [perms.IsInGroup(allowed_groups=['NURSE', 'DOCTOR'])]

    @action(methods=['patch'], detail=True, url_path='update-paid')
    def update_paid(self, request, pk=None):
        try:
            receipt = self.get_object()
            receipt.nurse = request.user.nurse
            receipt.paid = True
            receipt.save()
            return Response({'message': 'Receipt paid successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    serializer_class = serializers.DoctorSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Doctor.objects.all()


class PatientViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]
