from rest_framework.pagination import PageNumberPagination

"""
    Bu sınıf, Django'nun sayfalama (pagination) işlemini özelleştirir. Frontend, API sorgusunda
    sayfa numarasını ve sayfa boyutunu belirlemek için parametreler kullanabilir. 
    - page_size: Varsayılan sayfa boyutunu belirler.
    - page_size_query_param: İstemcinin URL'de belirleyeceği parametre adıdır.
    - max_page_size: İstemcinin talep edebileceği en büyük sayfa boyutudur. 
"""
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10 # Varsayılan sayfa boyutu 10 olarak ayarlanmıştır. Bu, her sayfada gösterilecek öğe sayısını belirler.
    page_size_query_param = "page_size" # URL parametresi olarak 'page_size' ile frontend sayfa boyutunu değiştirebilir.
    max_page_size = 10000 # Sayfa boyutunun üst sınırıdır. Frontend bu sınırdan büyük bir sayfa boyutu isteyemez.