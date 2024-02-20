import cloudinary
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, DepartmentSchedule
# Register your models here.


class PatientAdmin(admin.ModelAdmin):
    readonly_fields = ['Avatar_Preview']

    def Avatar_Preview(self, patient):
        if patient:
            return mark_safe(
                '<img src="{url}" width="120" />'.format(url=patient.user_info.avatar)
            )


class PrescriptionMedicineAdmin(admin.StackedInline):
    model = Prescription.medicines.through


class MedicineAdmin(admin.ModelAdmin):
    search_fields = ['name']


class PrescriptionAdmin(admin.ModelAdmin):
    inlines = [PrescriptionMedicineAdmin, ]


class DepartmentScheduleAdmin(admin.ModelAdmin):
    list_filter = ['date']
    search_fields = ['date', 'name']


class UserAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if obj.avatar:
            if obj.avatar.size > 0:  # Check if the file size is greater than 0
                cloudinary_response = cloudinary.uploader.upload(obj.avatar)
                obj.avatar = 'https://res.cloudinary.com/drbd9x4ha/' + cloudinary_response['secure_url']
        if not obj.pk:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Medicine, MedicineAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment)
admin.site.register(Department)
admin.site.register(Service)
admin.site.register(DepartmentSchedule, DepartmentScheduleAdmin)
admin.site.register(Receipt)
admin.site.register(User, UserAdmin)

