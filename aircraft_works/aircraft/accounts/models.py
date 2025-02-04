from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.models import Group, Permission

from aircraft.accounts.managers import UserManager
from aircraft.core.mixins import AdminUtilsMixin, BaseModelMixin

# Sistemde bulunan kullanıcılar için bir model yarattım ve model ismi User'dır.
'''
    Burada miras aldığımız mixinler var 
    AdminUtilsMixin bize admin sayfasında kolaylık sağlar bu mixinde ne iş yaptığını anlatıyorum.
    PermissionsMixin ise djangonun database de bulunan kullanıcılara yetkilendirme vermesini sağlar. Örneğin kullanıcılara yönetici(is_staff), superuser(is_superuser) yetkileir verebiliriz.
    BaseModelMixin her modelde ortak kullandığım fieldları topladığım bir mixindir. Burada id, created_at, updated_at değerleri var. Bu mixini yazarak kod tekrarını engellemiş oldum.
'''
class User(AdminUtilsMixin, PermissionsMixin, AbstractBaseUser, BaseModelMixin):
    email = models.EmailField(unique=True, db_index=True, verbose_name="Email") #sisteme login olabilmek için email fieldına ihtiyaç vardır ve email fieldı unique bir fielddır.
    password = models.CharField(max_length=128, verbose_name="şifre", blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="Ad", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Soyad", blank=True, null=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Takım") #Bir takımda birden fazla kullanıcı olabilir ve 1 kullanıcı sadece 1 takıma ait olabilir bu ilişki 1:N ilişkisidir. Kullanıcı modelini takımı foreign key (FK) olarak ekliyoruz bu sayede bir kullanıcının takım bilgisine erişebilir oluyoruz.
    last_seen = models.DateTimeField(null=True, verbose_name="Last Seen")
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin?")
    is_staff = models.BooleanField(default=True, verbose_name="Is Staff?")
    is_active = models.BooleanField(default=True, verbose_name="Is Active?")
    is_deleted = models.BooleanField(default=False, verbose_name="Is Deleted?")
    groups = models.ManyToManyField(Group, blank=True, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="custom_user_permissions")

    USERNAME_FIELD = "email" # username fieldı email olarak ayarlıyoruz çünkü user tablomuzda username alanı tutmuyorum.
    objects = UserManager() # modelimize özel bir UserManager sınıfı atamanızı sağlıyoruz. Bu sayede, kullanıcı modelimize ait nesneleri yaratırken (create_user, create_superuser gibi metodlarla) özel kullanıcı oluşturabiliriz.

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.id} - {self.email}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)


# Sistemde bulunan takımlar için bir model yarattım ve model ismi Team'dir.
'''
    Burada miras aldığımız mixinler var 
    AdminUtilsMixin bize admin sayfasında kolaylık sağlar bu mixinde ne iş yaptığını anlatıyorum.
    BaseModelMixin her modelde ortak kullandığım fieldları topladığım bir mixindir. Burada id, created_at, updated_at değerleri var. Bu mixini yazarak kod tekrarını engellemiş oldum.
'''
class Team(AdminUtilsMixin, BaseModelMixin):
    class Team(models.TextChoices):
        WING = "WING", "Kanat Takımı"
        FUSELAGE = "FUSELAGE", "Gövde Takımı"
        TAIL = "TAIL", "Kuyruk Takımı"
        AVIONICS = "AVIONICS", "Aviyonik Takımı"
        ASSEMBLY = "ASSEMBLY", "Montaj Takımı"

    team_type = models.CharField(max_length=20, choices=Team.choices, default=Team.WING, verbose_name="Takım Türü", unique=True)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self) -> str:
        return f"{self.id} - {self.team_type}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

