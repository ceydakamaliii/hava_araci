from django.db import models
from aircraft.accounts.models import Team, User
from aircraft.core.mixins import AdminUtilsMixin, BaseModelMixin
from django.core.exceptions import ValidationError



class Part(AdminUtilsMixin, BaseModelMixin): # Parçaları tutmak için oluşturmuş olduğum modeldir. AdminUtilsMixin ile admin panelde yapabileceği işler özelleştiriyorum. BaseModelMixin ile de ortak her modelde bulunan fieldları bu modelede eklemiş oluyorum. 
    class PartTypes(models.TextChoices): # Her parçanın bir tipi olması gerekiyor. Ör: Kanat, Gövde, Kuyruk, Aviyonik.
        WING = "WING", "Kanat"
        FUSELAGE = "FUSELAGE", "Gövde"
        TAIL = "TAIL", "Kuyruk"
        AVIONICS = "AVIONICS", "Aviyonik"
    
    class PlaneTypes(models.TextChoices): # Her parça belirli bir uçağa özel olması gerekir Ör: TB2 uçağı için TB2-gövde, TB2-kuruk....
        TB2 = "TB2", "TB2"
        TB3 = "TB3", "TB3"
        AKINCI = "AKINCI", "AKINCI"
        KIZILELMA = "KIZILELMA", "KIZILELMA"

    part_type = models.CharField(max_length=50, choices=PartTypes.choices, verbose_name="Parça Türü")
    plane_type = models.CharField(max_length=20, choices=PlaneTypes.choices, default=PlaneTypes.TB2, verbose_name="Uçak Tipi")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="parts", verbose_name="Kullanıcı") # Her parçayı üreten bir kullanıcı vardır sistemdeki var olan parçaları kimin ürettiğini tutuyor bu field.
    # is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted?")
    used_in_plane = models.BooleanField(default=False, verbose_name="Kullanıldı mı?") # Parçalar uçak oluşumunda kullanılıyor uçak oluşumunda kullanılan parçalar silinmiyor used_in_plane alanı True olarak güncelleniyor ve daha sonra bu parçalar kullanılmıyor.

    def clean(self): # Bu method aslında sistemem parça eklerken uyulması gereken bazı gereksinimler.
        # öncelikle parça üretmek için sistemde kullanıcı ve kullanıcının takımı olması gerek.
        if not self.user:
            raise ValidationError("Bu parçayı üretmek için bir kullanıcı gereklidir.")

        if not self.user.team:
            raise ValidationError("Kullanıcının takımı yok, parça üretilemez.")
        # Her takım sadece kendi parçasını üretebilir Örneğin Kanat Takımı sadece kanat üretebilir. Montaj takımı ise parça üretemez.
        if self.part_type == "WING" and self.user.team.team_type != "WING":
            raise ValidationError("Kanat parçalarını sadece Kanat ekibi üretebilir.")
        elif self.part_type == "FUSELAGE" and self.user.team.team_type != "FUSELAGE":
            raise ValidationError("Gövde parçalarını sadece Gövde ekibi üretebilir.")
        elif self.part_type == "TAIL" and self.user.team.team_type != "TAIL":
            raise ValidationError("Kuyruk parçalarını sadece Kuyruk ekibi üretebilir.")
        elif self.part_type == "AVIONICS" and self.user.team.team_type != "AVIONICS":
            raise ValidationError("Aviyonik parçalarını sadece Aviyonik ekibi üretebilir.")
        elif self.user.team.team_type == "ASSEMBLY":
            raise ValidationError("Montaj takımı parça üretemez.")

    def __str__(self):
        return f"{self.get_part_type_display()} for {self.get_plane_type_display()}"
    

class PlaneAssembly(AdminUtilsMixin, BaseModelMixin): #Montaj takımının ürettiği uçakları tuttuğum modeldir.
    class PlaneTypes(models.TextChoices): # Ürettiği uçağın tipi için bu alana ihtiyacım var.
        TB2 = "TB2", "TB2"
        TB3 = "TB3", "TB3"
        AKINCI = "AKINCI", "AKINCI"
        KIZILELMA = "KIZILELMA", "KIZILELMA"
    plane_type = models.CharField(max_length=20, choices=PlaneTypes.choices, verbose_name="Uçak tipi")
    parts_used = models.ManyToManyField(
        Part,
        through="PartUsage",
        related_name='plane_assemblies',
        verbose_name="Kullanılan parçalar"
    ) # Bu alan uçak üretilirken kullanıclan parça listesidir.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="plane_assemblies", verbose_name="Kullanıcı") # Uçağı üreten kullanıcıdır.

    def clean(self):
        # Burada uçak üretimini yapıcak olan kullanıcı montaj ekibi içinde olmalı yoksa hata fırlatıcak.
        if self.user and self.user.team and self.user.team.team_type != Team.Team.ASSEMBLY:
            raise ValidationError("Uçak üretimi sadece 'MONTAJ' takımına ait kullanıcılar tarafından yapılabilir.")

    def __str__(self):
        return f"{self.id} - {self.plane_type}"


class PartUsage(AdminUtilsMixin, BaseModelMixin): # Uçak üretiminde kullanılan parçaları tutan bir modedlir.
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="usage_history", verbose_name="Parça") # Parça ile ilişkisi 1:N şeklindedir. Bu yüzden Foreignkey olarak ekliyoruz.
    plane_assembly = models.ForeignKey(PlaneAssembly, on_delete=models.CASCADE, related_name="part_usage_history", verbose_name="Üretilen Uçak")  # Bu ise üretilen uçak ile ilişkisidir. Parça hangi uçakda kullanıldı bunu bize sağlar.

    class Meta:
        unique_together = ('part', 'plane_assembly')  # Aynı parça, aynı uçakta birden fazla kaydın olmasını engeller

    def __str__(self):
        return f"{self.part.part_type} - {self.plane_assembly}"
