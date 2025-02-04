from aircraft.accounts.serializers import UserSerializer
from aircraft.plane_management.models import Part, PartUsage, PlaneAssembly
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer, SerializerMethodField
from rest_framework.fields import CharField, CurrentUserDefault, HiddenField, IntegerField, ChoiceField, ListField, DictField
from django.db import transaction

class PartCreateSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    plane_type = ChoiceField(choices=Part.PlaneTypes.choices, required=True)
    part_type = ChoiceField(choices=Part.PartTypes.choices, required=True)
    quantity = IntegerField(min_value=1, required=True, write_only=True)  # Modelde yok, sadece istekte olacak

    class Meta:
        model = Part
        fields = ['part_type', 'plane_type', 'user', 'quantity']

    def validate(self, attrs):
        """ Burada clean() çağırarak tüm doğrulamaları yapıyoruz. """
        quantity = attrs.pop('quantity', 1)  # Varsayılan olarak 1 al
        if quantity < 1:
            raise ValidationError({'quantity': 'Miktar en az 1 olmalıdır.'})

        # Kullanıcının takımı ile parça uyumlu mu? Bunu `clean()` içinde kontrol edeceğiz.
        for _ in range(quantity):
            part = Part(**attrs)  # Geçici Part nesnesi oluştur
            part.clean()  # Modelin clean() metodunu çağır
        
        attrs['_quantity'] = quantity  # Geçici olarak validasyon sonrası kullanılacak
        return attrs

    def create(self, validated_data):
        """ `clean()` çağırmamıza gerek yok çünkü `validate()` aşamasında zaten çağırdık. """
        quantity = validated_data.pop('_quantity')  # Önceki adımda eklediğimiz geçici quantity bilgisini al
        parts = [Part(**validated_data) for _ in range(quantity)]  # Belirtilen miktarda Part oluştur
        return Part.objects.bulk_create(parts)  # Toplu olarak kaydet


class PartUsageSerializer(ModelSerializer):
    class Meta:
        model = PartUsage
        fields = ('plane_assembly',)


class PartListSerializer(ModelSerializer):
    team = SerializerMethodField()
    part_type = CharField(source='get_part_type_display', read_only=True)
    user = PresentablePrimaryKeyRelatedField(presentation_serializer=UserSerializer, read_only=True)
    part_usages = SerializerMethodField()  # PartUsage bilgilerini ekleyin, yani uçakta kullanıldıysa hangi uçakta kullanıldı

    def get_part_usages(self, obj: Part) -> list:
        return PartUsageSerializer(obj.usage_history.all(), many=True).data if obj.usage_history.exists() else []

    def get_team(self, obj: Part) -> str:
        return obj.user.team.get_team_type_display() if obj.user and obj.user.team else None

    class Meta:
        model = Part
        fields = ['id', 'part_type', 'plane_type', 'team', 'user', 'used_in_plane', 'created_at', 'updated_at', 'part_usages']


class CreatePlaneAssemblySerializer(Serializer): # Uçak üretme serializerı
    plane_type = ChoiceField(choices=PlaneAssembly.PlaneTypes.choices, required=True)
    parts_used = ListField(child=DictField())
    user = HiddenField(default=CurrentUserDefault())

    def validate_parts_used(self, parts):
        self._validate_part_types(parts)
        self._validate_part_amounts(parts)
        return parts

    def _validate_part_types(self, parts):
        required_part_types = {Part.PartTypes.WING, Part.PartTypes.FUSELAGE, Part.PartTypes.TAIL, Part.PartTypes.AVIONICS}
        received_part_types = set()

        for part_data in parts:
            part_type = part_data.get('part_type')
            part_plane_type = part_data.get('plane_type')

            # Eğer part_type veya part_plane_type eksikse hata ver
            if not part_type or not part_plane_type:
                raise ValidationError("Her parça için 'part_type' ve 'plane_type' gereklidir.")
            
            # Eğer parça tipi, uçağın modeline uymuyorsa hata ver
            if part_plane_type != self.initial_data["plane_type"]:
                raise ValidationError(
                    f"{part_plane_type} {part_type} parçası {self.initial_data['plane_type']} uçağına takılamaz."
                )

            # Gelen parçaları bir sete ekle
            received_part_types.add(part_type)

        # Tüm gerekli parçalar var mı kontrol et
        missing_parts = required_part_types - received_part_types
        if missing_parts:
            raise ValidationError(f"Eksik parçalar var: {', '.join(missing_parts)}")

        return parts

    def _validate_part_amounts(self, parts):
        # Part tiplerinin Türkçe karşılıkları
        part_type_display_map = {
            "WING": "Kanat",
            "FUSELAGE": "Gövde",
            "TAIL": "Kuyruk",
            "AVIONICS": "Aviyonik"
        }

        plane_type = self.initial_data['plane_type']
        parts_used = parts
        
        # Her parça tipi için gereken miktarları kontrol et
        for part_data in parts_used:
            part_type = part_data['part_type']
            part_amount = part_data['amount']
            
            # Parça tipinin Türkçe karşılığını al
            part_type_display = part_type_display_map.get(part_type, part_type)
            
            # Kullanılabilir parçaları bul
            available_parts = Part.objects.filter(
                part_type=part_type,
                plane_type=plane_type,
                used_in_plane=False
            )
            
            # Yeterli parça var mı kontrol et
            if available_parts.count() < part_amount:
                raise ValidationError(
                    f"{plane_type} uçağı için {part_type_display} parçası eksik, "
                    f"{part_amount - available_parts.count()} adet parça bulunamadı."
                )


    def create(self, validated_data):
        parts_data = validated_data.pop('parts_used')
        user = validated_data.pop('user')
        plane_type = validated_data.pop('plane_type')

        with transaction.atomic():
            plane_assembly = PlaneAssembly.objects.create(plane_type=plane_type, user=user)

            # PartUsage nesneleri oluşturuluyor
            for part_data in parts_data:
                part_type = part_data.get('part_type')
                amount = part_data.get('amount')
                part_plane_type = part_data.get('plane_type')

                available_parts = Part.objects.filter(plane_type=part_plane_type, part_type=part_type, used_in_plane=False)
                if available_parts.count() < amount:
                    raise ValidationError(f"{self.initial_data['plane_type']} uçağı için {part_type} parçası eksik, {amount} adet parça bulunamadı.")

                # PartUsage kaydediliyor
                for part in available_parts[:amount]:
                    PartUsage.objects.create(part=part, plane_assembly=plane_assembly)
                    part.used_in_plane = True
                    part.save()

        return plane_assembly


class PlaneAssemblyListSerializer(ModelSerializer):
    parts_used = PartListSerializer(many=True, read_only=True)

    class Meta:
        model = PlaneAssembly
        fields = ('id', 'plane_type', 'parts_used', 'user', 'created_at')