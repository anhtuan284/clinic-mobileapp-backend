from rest_framework.pagination import PageNumberPagination


class PatientPaginator(PageNumberPagination):
    page_size = 2


class DoctorPaginator(PageNumberPagination):
    page_size = 10