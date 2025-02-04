from django.db.models.fields import CharField

from aircraft.core.helpers import generate_unique_id


class AircraftPrimaryKeyField(CharField): # Custom oluşturduğumuz field CharField sınıfını miras alıyor.
    def __init__(self, *args, **kwargs):
        kwargs["primary_key"] = True # Alanı pk yani birincil anahtar olarak ayarlıyoruz.
        kwargs["default"] = generate_unique_id # Bu anahtarın değeri için helpersda yazmış olduğum fonksiyon kullanılıyor.
        kwargs["editable"] = False # Alanın editlenmesini yani düzenlenmesini engelliyoruz çünkü db'de bulunan id'ler yani pk'lar değiştirilemez.
        kwargs["max_length"] = 64 # Bu alanın max uzunluğunu 64 karakter olarak ayarlıyoruz.
        super().__init__(*args, **kwargs)
