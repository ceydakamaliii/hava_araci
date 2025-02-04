from rest_framework.fields import CharField, CurrentUserDefault, HiddenField, IntegerField, ChoiceField
from rest_framework.serializers import ModelSerializer, Serializer, SerializerMethodField
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import HybridImageField, LowercaseEmailField
from django.core.validators import validate_email
from aircraft.accounts.models import Team, User
from aircraft.accounts.validators import validate_name
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LogoutSerializer(Serializer):
    refresh = CharField(required=True)

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise ValidationError("Token is invalid or expired")
    

class CreateUserSerializer(ModelSerializer):
    team_name = CharField(write_only=True, required=True)
    email = LowercaseEmailField(required=True, validators=[validate_email])
    first_name = CharField(required=False, allow_blank=True, validators=[validate_name])
    last_name = CharField(required=False, allow_blank=True, validators=[validate_name])
    password = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "team_name", "password"]
        extra_kwargs = {
            'first_name': {'required': True, 'max_length': 100},
            'last_name': {'required': True, 'max_length': 100}
        }

    def validate_email(self, value): # Frontendden gönderilen email sistemde mevcutsa sisteme bu kullanıcı kaydedilmez.
        if User.objects.filter(email=value).exists():
            raise ValidationError("Bu e-postaya sahip bir kullanıcı zaten mevcut.")
        return value

    def validate_first_name(self, value):
        if len(value) > 100:
            raise ValidationError('İsim 100 karakterden uzun olamaz.')
        return value

    def validate_last_name(self, value):
        if len(value) > 100:
            raise ValidationError('Soyisim 100 karakterden uzun olamaz.')
        return value

    def validate_team_name(self, value):
        valid_team_names = [team[0] for team in Team.Team.choices]
        if value not in valid_team_names:
            raise ValidationError(f'Geçersiz takım adı: {value}')
        return value

    def create(self, validated_data): # User oluşturma yani post metodunda kullanılır.
        team_name = validated_data.pop("team_name")
        team, _ = Team.objects.get_or_create(team_type=team_name)
        validated_data["team"] = team
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)  # Kullanıcıyı oluşturduktan sonra frontendden gelen passwordü kullanıya setliyoruz. Hashlenmiş bir şekilde gözükücek artık password.
        user.is_active = True # Kullanıcı is_active'i True olarak ayarlıyoruz.
        user.save()
        return user
    

class AircraftObtainPairSerializer(TokenObtainPairSerializer): # Login işlemi için kullanılan serializer
    def validate(self, attrs) -> dict:
        email = attrs.get("email") # frontendden gelen email
        password = attrs.get("password") # frontendden gelen password
        try:
            user = User.objects.get(email=email) # Bu emaile sahip sistemde kullanıcı var mı kontrolü yapıyorum.
            if user.check_password(password): # Eğer varsa frontendden gönderilen passwordle üser passwordünü kontrol ediyorum.
                attrs["email"] = user.email # Aynı ise emaili kaydediyorum
        except User.DoesNotExist: # Bu emaile sahip kullanıcı yoksa except bloğuna giricek ve hata vericek.
            raise ValidationError("Sağlanan kimlik bilgilerine sahip böyle bir kullanıcı yok")
        data = super().validate(attrs) # eklenen bilgilere göre TokenObtainPairSerializer'ın validate fonksiyonuna emaili gönderiyorum ve bu fonksiyon bana access_token ve refresh_token döndürüyor.
        return data


class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'team_type']


class UserSerializer(ModelSerializer):
    team_name = SerializerMethodField()

    def get_team_name(self, obj):
        return obj.team.team_type if obj.team else None
            
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'team_name', 'is_active', 'is_admin']