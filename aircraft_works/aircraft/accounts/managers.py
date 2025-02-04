from typing import Any

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True # Bu özellik, manager sınıfının migrasyonlarda kullanılacağını belirtir.

    def _create_user(self, email: str, password: str, **extra_fields: Any):
        """
            Kullanıcı oluşturma işlemi. Kullanıcı e-posta ve şifre ile yeni bir kullanıcı oluşturur.
            Bu, normal kullanıcı ve süper kullanıcı için ortak temel oluşturma fonksiyonudur.
        """
        email = self.normalize_email(email) # E-posta adresini normalize eder (küçük harfe dönüştürür).
        user = self.model(email=email, **extra_fields) # Kullanıcı modelini oluşturur.
        user.set_password(password) # Kullanıcının şifresini şifreler.
        user.save(using=self._db) # Kullanıcıyı veritabanına kaydeder.

        return user

    def create_user(self, email: str = None, password: str = None, **extra_fields: Any):
        """
            Normal bir kullanıcı oluşturur. `is_staff`, `is_superuser` ve `is_active` gibi alanları 
            varsayılan olarak False olarak ayarlar.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields: Any):
        """
            Süper kullanıcı (admin) oluşturur. `is_staff`, `is_superuser`, ve `is_active` alanlarını
            True olarak ayarlar. 
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)