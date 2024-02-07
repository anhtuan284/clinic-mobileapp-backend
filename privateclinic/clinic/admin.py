from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User
# Register your models here.


class PatientAdmin(admin.ModelAdmin):
    readonly_fields = ['Avatar_Preview']

    def Avatar_Preview(self, patient):
        if patient:
            return mark_safe(
                '<img src="https://res.cloudinary.com/drbd9x4ha/{url}" width="120" />'.format(url=patient.avatar)
            )


class PrescriptionMedicineAdmin(admin.StackedInline):
    model = Prescription.medicines.through


class MedicineAdmin(admin.ModelAdmin):
    inlines = [PrescriptionMedicineAdmin, ]


class PrescriptionAdmin(admin.ModelAdmin):
    inlines = [PrescriptionMedicineAdmin, ]


class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment)
admin.site.register(User, UserAdmin)

