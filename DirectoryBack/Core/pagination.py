from rest_framework.pagination import PageNumberPagination

class FilePagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    min_page_size = 12
    max_page_size = 240