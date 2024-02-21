from .models import Patient, Receipt
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear


def count_patients_by_period(period):
    trunc_function = TruncMonth if period == 'month' else TruncQuarter if period == 'quarter' else TruncYear
    group_field = 'month' if period == 'month' else 'quarter' if period == 'quarter' else 'year'

    return (
        Patient.objects.annotate(**{group_field: trunc_function('appointments__scheduled_date')})
        .values(group_field)
        .annotate(patient_count=Count('user_info_id'))
        .order_by(group_field)
    )


def calculate_revenue_by_period(period):
    trunc_function = TruncMonth if period == 'month' else TruncQuarter if period == 'quarter' else TruncYear
    group_field = 'month' if period == 'month' else 'quarter' if period == 'quarter' else 'year'

    return (
        Receipt.objects.annotate(**{group_field: trunc_function('created_date')})
        .values(group_field)
        .annotate(total_revenue=Sum('total'))
        .order_by(group_field)
    )