import cloudinary
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.contrib.admin.views.decorators import staff_member_required
from .models import Doctor, Nurse, Medicine, Prescription, Patient, Appointment, User, Receipt, Service, Department, DepartmentSchedule
from .dao import *
# Register your models here.


class ClinicAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản trị phòng mạch tư'

    def get_urls(self):
        return [
            path('clinic-stats/', self.stats_view)
        ] + super().get_urls()

    def stats_view(self, request):
        period = request.GET.get('period', 'month')
        stats = count_patients_by_period(period=period)
        revenue_stats = calculate_revenue_by_period(period=period)

        context = {
            'stats': stats,
            'revenue_stats': revenue_stats,
            'period': period
        }

        return render(request, 'admin/stats.html', context)


admin_site = ClinicAdminSite(name='myadmin')


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


admin_site.register(Doctor)
admin_site.register(Nurse)
admin_site.register(Medicine, MedicineAdmin)
admin_site.register(Prescription, PrescriptionAdmin)
admin_site.register(Patient, PatientAdmin)
admin_site.register(Appointment)
admin_site.register(Department)
admin_site.register(Service)
admin_site.register(DepartmentSchedule, DepartmentScheduleAdmin)
admin_site.register(Receipt)
admin_site.register(User, UserAdmin)

