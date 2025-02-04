from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from aircraft.core.fields import AircraftPrimaryKeyField

class AdminUtilsMixin(object): #Djangonun admin paneli için yazmışl olduğum mixindir. Admin panele model sınıfları için yardımcı işlevler ekleyebilmemi sağlıyor. Örneğin admin panelde bir nesnenin detay sayfasına yönlendirmek için bu mixin kullanılır.
    @classmethod
    def get_content_type(cls): # Bu method, modelin içerik türünü alır. Modelin içerik türü, djangonun temel tipini temsil eder ve admin paneldeki işlemleri için kullanılır.
        return ContentType.objects.get_for_model(cls)

    def get_admin_change_url(self) -> str: # Bu method, model nesnesinin admin panelindeki değişiklik sayfasının URL'sini döndürür. URL, admin panelinde ilgili modelin detay sayfasına yönlendirir.
        admin_url_name = "admin:%s_%s_change" % (
            self.get_content_type().app_label, # Uygulama etiketini alır.
            self.get_content_type().model, # Model ismini alır.
        )
        return reverse(admin_url_name, args=[self.id]) # Modelin ID'sini kullanarak admin sayfasına yönlendirir.


class BaseModelMixin(models.Model): # Her modelde ortak bulunan fieldları her defasında yazmamk için bir mixin oluşturdum model sınıflarına bu mixini vererek modellere id, created_at ve updated_at değerlerini sağlamış oluyorum.
    id = AircraftPrimaryKeyField() # Custom yazmış olduğum fieldı kullanıyorum 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date") # Objenin database'e kaydedilme tarihini tutuyot.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date") # Objenin database'de en son güncellenme tarihini tutuyor.

    class Meta:
        abstract = True
