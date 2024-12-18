from rest_framework.pagination import PageNumberPagination


class CategoryPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class CountryPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class SupplierPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class ProductPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class WarehousePaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class OrderPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class PayablePaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
