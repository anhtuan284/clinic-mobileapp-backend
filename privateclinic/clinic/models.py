from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class CommonInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    first_name = models.CharField(max_length=80, null=True)
    last_name = models.CharField(max_length=80, null=True)
    birth_date = models.DateField(null=True)
    sex = models.CharField(max_length=10, choices=SEX, null=True)
    cin = models.CharField(max_length=15, null=True)
    phone_nb = models.CharField(max_length=30, null=True)

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)

    class Meta:
        abstract = True


class Patient(CommonInfo):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    avatar = CloudinaryField('avatar', null=True)
    email = models.EmailField(null=True)
    weight = models.IntegerField(null=True)
    allergies = models.CharField(max_length=200, null=True)


class Doctor(CommonInfo):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    SPECIALTY = (
        ('G', 'General practice'),
        ('C', 'Clinical radiology'),  # X quang lam san
        ('A', 'Anaesthesia'),  # Gay te
        ('O', 'Ophthalmology')  # Eye
    )
    email = models.EmailField()
    pwd = models.CharField(max_length=200)
    salary = models.FloatField()
    specialty = models.CharField(max_length=200, choices=SPECIALTY)
    is_active = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)


class Nurse(CommonInfo):
    salary = models.FloatField()
    is_active = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    # Shell: m.prescription_set.all()

    def __str__(self):
        return self.name


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.doctor) + " | " + str(self.nurse)


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    medicines = models.ManyToManyField(Medicine)  # Shell: p.medicines.all()

    def __str__(self):
        return "Đơn thuốc " + str(self.appointment)
