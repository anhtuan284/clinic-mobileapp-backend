from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", 'Patient'
        ADMIN = "ADMIN", 'Admin'
        DOCTOR = "DOCTOR", 'Doctor'
        NURSE = "NURSE", 'Nurse'

    avatar = CloudinaryField('avatar', null=True)
    role = models.CharField(max_length=50, choices=Role, default=Role.PATIENT)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class UserInfo(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    birth_date = models.DateField(null=True)
    sex = models.CharField(max_length=10, choices=SEX, null=True)
    phone_nb = models.CharField(max_length=30, null=True)

    class Meta:
        abstract = True


class Patient(UserInfo):
    weight = models.IntegerField(null=True)
    allergies = models.CharField(max_length=200, null=True)


class Doctor(UserInfo):
    SPECIALTY = (
        ('G', 'General practice'),
        ('C', 'Clinical radiology'),  # X quang lam san
        ('A', 'Anaesthesia'),  # Gay te
        ('O', 'Ophthalmology')  # Eye
    )
    salary = models.FloatField()
    specialty = models.CharField(max_length=200, choices=SPECIALTY)


class Nurse(UserInfo):
    salary = models.FloatField(null=True)


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    price = models.FloatField(null=True)
    # Shell: m.prescription_set.all()

    def __str__(self):
        return self.name


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name="appointments", on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.doctor)


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    symptoms = models.TextField(max_length=500)
    diagnosis = models.TextField(max_length=500)
    pay_status = models.BooleanField(default=False)
    medicines = models.ManyToManyField(Medicine)  # Shell: p.medicines.all()

    def calculate_total_cost(self):
        total_cost = 0.0
        for medicine in self.medicines.all():
            if medicine.price is not None:
                total_cost += medicine.price
        return total_cost

    def __str__(self):
        return "Toa thuốc " + str(self.appointment)
