import random
import time

def generate_unique_id() -> str: # model objeleri için unique id oluşturan fonksiyon.
    total_bits = 63
    bits_reserved_for_timestamp = 42 # Ürettiğimiz 63 bitlik unique id'nin 42 biti timestamp'den gelicek
    bits_reserved_for_randomness = 21 # Ürettiğimiz 63 bitlik unique id'nin 21 biti random bir şekilde oluşturulacak.

    assert bits_reserved_for_timestamp + bits_reserved_for_randomness == total_bits # bitlerin toplamı 63 olduğundan emin olmalıyız

    total_milliseconds = int(time.time() * 1000) # Şu anki zamanı milisaniye cinsinden alıyoruz
    unique_id = total_milliseconds << bits_reserved_for_randomness # Zaman damgasını 21 bit sola kaydırarak randomness'e yer açıyoruz

    random_bits = random.SystemRandom().getrandbits(bits_reserved_for_randomness) # 21 bitlik sayı üretiyoruz
    unique_id |= random_bits # random ürettiğimiz 21 bitlik sayıyı timestampden aldığımız 42 bitlik sayının sonuna ekliyoruz.

    return str(unique_id) # id'i string formatında dönüyoruz.
