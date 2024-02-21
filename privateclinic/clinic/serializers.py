from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, \
    DepartmentSchedule, PrescriptionMedicine
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(source="avatar")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def get_avatar(self, user):
        if user.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(user.avatar)
            return user.avatar.url
        return None

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        return u


class BaseSerialize(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='avatar')

    def get_image(self, patient):
        if patient.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('https://res.cloudinary.com/drbd9x4ha/%s' % patient.avatar)

            return 'https://res.cloudinary.com/drbd9x4ha/%s' % patient.avatar


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = '__all__'
        select_related = ['user_info']


class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        fields = '__all__'
        select_related = ['user_info']


class NurseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nurse
        fields = '__all__'
        select_related = ['user_info']



class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = '__all__'


class MedicineListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'weight']


class MedicineDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prescription
        fields = ['id', 'symptoms', 'diagnosis', 'patient', 'doctor', 'medicines', 'services']
        select_related = ['patient', 'doctor']
        prefetch_related = ['medicines', 'services']


class PrescriptionMedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrescriptionMedicine
        fields = ['id', 'prescription', 'medicine', 'quantity', 'dosage']


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    dosages = PrescriptionMedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['id', 'symptoms', 'diagnosis', 'patient', 'doctor', 'services', 'dosages']
        select_related = ['patient', 'doctor']
        prefetch_related = ['medicines', 'services']


class ReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = '__all__'
        select_related = ['nurse', 'prescription']
