import datetime
from datetime import date

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.hashers import make_password
from django.contrib.sites import requests
from django.core.mail import send_mail
from django.db.models import Sum, ExpressionWrapper, F, DecimalField, Max, Q
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.generics import UpdateAPIView

from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, \
    DepartmentSchedule, PrescriptionMedicine
from rest_framework import viewsets, permissions, generics, parsers, status

from .paginator import DoctorPaginator
from .serializers import PatientSerializer, AppointmentSerializer
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
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action in ['profile', 'update_user']:
            return [perms.AccountOwnerAuthenticated()]
        elif self.action in ['register_user']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['update_user']:
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer

    @action(methods=['get'], url_path='current-user', url_name='current-user', detail=False)
    def current_user(self, request):
        return Response(serializers.UserSerializer(request.user).data)

    @action(methods=['post'], url_path='register', detail=False)
    def register_user(self, request):
        try:
            data = request.data
            avatar = request.data.get("avatar")
            new_avatar = cloudinary.uploader.upload(data.get('avatar'), folder='clinic_user/')

            new_user = User.objects.create_user(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password"),
                avatar=new_avatar['secure_url'],
            )
            new_user.patient = Patient.objects.create(weight='0', allergies='No information', user_info=new_user)
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
            passw = request.data.get("password")
            if passw is not None:
                return Response({'error': 'Can not change password'}, status=status.HTTP_400_BAD_REQUEST)
            for fields, value in request.data.items():
                setattr(user_before, fields, value)
            if avatar_file:
                new_avatar = cloudinary.uploader.upload(avatar_file)
                user_before.avatar = new_avatar['secure_url']
            user_before.save()
            return Response(data=serializers.UserSerializer(user_before, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='profile', detail=True)
    def profile(self, request, pk):
        try:
            user = self.get_object()
            detail_user = serializers.UserSerializer(user, context={'request': request}).data
            return Response(data=detail_user, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_403_FORBIDDEN)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            now = datetime.datetime.now()
            subject = f'YOUR PASSWORD HAS BEEN CHANGED !!'
            message = f"Dear ,\n\nYour password has been changed at {now}" \
                      f".\n\nRegards,\nThe Private Clinic Team"
            sender_email = 'peteralwaysloveu@gmail.com'
            recipient_email = self.get_object().email
            print(recipient_email)
            send_mail(subject, message, sender_email, [recipient_email], fail_silently=True)

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in ['create_appointment', 'get_user_appointment', 'user_cancel_appointment']:
            return [perms.IsInGroup(allowed_groups=['PATIENT'])]
        return [perms.IsInGroup(allowed_groups=['NURSE'])]

    @action(methods=['post'], url_name='create-appointment', url_path='create-appointment', detail=False)
    def create_appointment(self, request):
        if request.user.is_authenticated:
            today = date.today()
            # phan nay la dung yeu cau den bai 1 ngay chi tiep nhan 100 don
            appointment_count = Appointment.objects.filter(created_date=today).count()
            max_appointments_per_day = 100
            # phaafn check single ton ch lam gio lam
            # cai nay if else moi chuan check thg approved voi pending gan nhat xem co ton tai kh
            # neu ton tai xem shecu voi today đã qua chưa, nếu qua rồi thì mới cho tạo
            # my_appointment_count = request.user.patient.appointments.filter(Q(scheduled_date=request.data.get("scheduled_date")) & Q(status__in=['pending', 'approved'])).count()
            # print(my_appointment_count)
            if appointment_count >= max_appointments_per_day:
                return Response({'error': 'You are no longer able to create appointment today. Retry on tomorrow.'},
                                status=status.HTTP_400_BAD_REQUEST)
            count_pending_approved_appointments = Appointment.objects.filter(status__in=['approved', 'pending'],
                                                                             patient=request.user.patient,
                                                                             scheduled_date__range=[today,
                                                                                                    request.data.get(
                                                                                                        "scheduled_date")]).count()

            if count_pending_approved_appointments >= 1:
                print(count_pending_approved_appointments)
                return Response({'error': 'Has been appointment.'},
                                status=status.HTTP_400_BAD_REQUEST)

            new_appointment = Appointment(
                patient=request.user.patient,
                scheduled_date=request.data.get("scheduled_date"),
                status='pending'
            )
            new_appointment.save()
            return Response(data=serializers.AppointmentSerializer(new_appointment, context={"request": request}).data,
                            status=status.HTTP_201_CREATED)

        else:
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['get'], url_path='get-list-pending', detail=False)
    def get_list_pending(self, request):
        today = date.today()
        queryset = Appointment.objects.order_by('-created_date').filter(status='pending', scheduled_date__gt=today)
        serializer = AppointmentSerializer(queryset, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='get-user-appointment', detail=False)
    def get_user_appointment(self, request):
        today = date.today()
        user_id = request.user.id
        print(user_id)
        user_appointment_now = Appointment.objects.filter(status__in=['approved', 'pending'],
                                                          scheduled_date__gt=today,
                                                          patient=Patient.objects.get(pk=user_id))
        appointment = user_appointment_now.first()  # Lấy ra cuộc hẹn đầu tiên trong queryset
        if appointment:
            serializer = AppointmentSerializer(appointment)  # Sử dụng serializer cho cuộc hẹn duy nhất
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Không có cuộc hẹn nào."}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], url_path='status-change', detail=True)
    def status_change(self, request, pk=None):
        this_apm = Appointment.objects.get(pk=pk)
        try:
            Appointment.objects.filter(scheduled_date=this_apm.scheduled_date)
            appointment = Appointment.objects.get(pk=pk)
            new_status = request.data.get('status')
            user = request.user

            if new_status in ['approved', 'cancelled'] and user.email is not None:
                appointment.status = new_status
                appointment.nurse = user.nurse
                if new_status == 'approved':
                    latest_order_number = \
                        Appointment.objects.filter(scheduled_date=appointment.scheduled_date).aggregate(
                            Max('order_number'))['order_number__max']
                    if latest_order_number is not None:
                        appointment.order_number = latest_order_number + 1
                    else:
                        appointment.order_number = 1

                subject = f'Appointment Status Changed: #{appointment.id}'
                message = f"Dear ,\n\nYour appointment status has been changed " \
                          f"from to " \
                          f"'{new_status}'.\n\nRegards,\nThe Private Clinic Team"
                sender_email = 'peteralwaysloveu@gmail.com'
                recipient_email = appointment.patient.user_info.email
                send_mail(subject, message, sender_email, [recipient_email])
                appointment.save()
                return Response({'message': 'Appointment status updated successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['patch'], url_path='user-cancel-appointment', detail=True)
    def user_cancel_appointment(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            if appointment.status in ['pending', 'approved']:
                appointment.status = 'cancelled'
                appointment.save()
                return Response({'message': 'Appointment cancelled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cannot cancel appointment with current status'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['patch'], url_path='cancel-appointment', detail=True)
    def cancel_appointment(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
            if appointment.status in ['pending', 'approved']:
                appointment.status = 'cancelled'
                appointment.nurse = request.user.nurse
                appointment.save()
                return Response({'message': 'Appointment cancelled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cannot cancel appointment with current status'},
                                status=status.HTTP_400_BAD_REQUEST)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


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
        if self.action in ['retrieve', 'user_pres']:
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

    @action(methods=['get'], detail=False, url_path='user-pres')
    def user_pres(self, request):
        try:
            pres = Prescription.objects.filter(patient=request.user.patient).order_by('-created_date')
            if pres is not None:
                return Response(serializers.PrescriptionListSerializer(pres, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=e.__str__()), status=status.HTTP_400_BAD_REQUEST)


class ReceiptViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer

    def get_permissions(self):
        if self.action in ['update_paid']:
            return [perms.IsInGroup(allowed_groups=['NURSE', 'PATIENT'])]
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
    pagination_class = DoctorPaginator
    queryset = Doctor.objects.all()


class ServiceViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = serializers.ServiceSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Service.objects.all()


class PatientViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]


import hmac, hashlib, urllib.parse, urllib.request, json, uuid
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
import json
import requests


@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        # Nhận thông tin thanh toán từ yêu cầu POST
        payment_data = json.loads(request.body)
        amount = payment_data.get('amount')

        # Tạo orderId và requestId
        order_id = str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        # Cấu hình thông tin MoMo
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        access_key = "F8BBA842ECF85"
        secret_key = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
        order_info = "Thanh chi phi kham benh"
        redirect_url = "http://127.0.0.1:8000/"  # Thay đổi URL redirect tại đây
        ipn_url = "http://127.0.0.1:8000"  # Thay đổi URL IPN tại đây

        # Tạo chuỗi chữ ký
        raw_signature = "accessKey=" + access_key + "&amount=" + str(amount) + "&extraData=" + "" \
                        + "&ipnUrl=" + ipn_url + "&orderId=" + order_id + "&orderInfo=" + order_info \
                        + "&partnerCode=MOMO" + "&redirectUrl=" + redirect_url + "&requestId=" + request_id \
                        + "&requestType=captureWallet"
        h = hmac.new(bytes(secret_key, 'ascii'), bytes(raw_signature, 'ascii'), hashlib.sha256)
        signature = h.hexdigest()

        # Tạo dữ liệu gửi đến MoMo
        data = {
            'partnerCode': 'MOMO',
            'partnerName': 'Test',
            'storeId': 'MomoTestStore',
            'requestId': request_id,
            'amount': str(amount),
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': redirect_url,
            'ipnUrl': ipn_url,
            'lang': 'vi',
            'extraData': '',
            'requestType': 'captureWallet',
            'signature': signature
        }

        # Gửi yêu cầu thanh toán đến MoMo
        response = requests.post(endpoint, json=data)
        print(response.json())
        # Xử lý kết quả trả về từ MoMo
        if response.status_code == 200:
            response_data = response.json()
            if 'payUrl' in response_data:
                # Nếu thành công, trả về URL thanh toán cho frontend
                return JsonResponse({'payUrl': response_data['payUrl']})
            else:
                return JsonResponse({'error': 'Failed to process payment'})
        else:
            return JsonResponse({'error': 'Failed to communicate with MoMo'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'})
