from .models import Patient, Doctor, Nurse, Prescription, Medicine, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

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


class PatientSerializer(BaseSerialize):

    class Meta:
        model = Patient
        fields = '__all__'


class DoctorSerializer(BaseSerialize):
    class Meta:
        model = Doctor
        fields = '__all__'


class NurseSerializer(BaseSerialize):
    class Meta:
        model = Nurse
        fields = '__all__'


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
