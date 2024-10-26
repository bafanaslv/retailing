from rest_framework.pagination import PageNumberPagination


class CategoryPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class SupplierPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
