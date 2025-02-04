import re

from django.core.validators import RegexValidator
validate_name = RegexValidator(r"^[-'\w\s]*\Z", ("Yalnızca harf ve rakam girin"), flags=re.U) #Signup akışında frontendden gelen first_name, last_name için bu validatorü kullanıyorum. Bu validatör yalnızca harf ve rakamdan oluşan değer olmasını kontrol eder.