from rest_framework.pagination import PageNumberPagination


class PatientPaginator(PageNumberPagination):
    page_size = 2
