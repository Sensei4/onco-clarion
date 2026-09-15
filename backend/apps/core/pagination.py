from rest_framework.pagination import PageNumberPagination


class StandardPageNumberPagination(PageNumberPagination):
    """Default pagination for OncoClarion API.

    - Default page size: 20
    - Client can request larger pages up to 100 via ?page_size=N
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"
