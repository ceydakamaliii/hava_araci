from typing import TYPE_CHECKING

from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from aircraft.core.permissions import AircraftIsAuthenticated, IsAircraftAssemblyTeam, IsNotAircraftAssemblyTeam, AircraftIsAuthenticated, HasTeamAndNotAssembly
from aircraft.plane_management.models import Part, PlaneAssembly
from aircraft.plane_management.serializers import CreatePlaneAssemblySerializer, PartCreateSerializer, PartListSerializer, PlaneAssemblyListSerializer
from rest_framework.views import APIView


if TYPE_CHECKING:
    from typing import Any

    from django.db.models.query import QuerySet
    

class PartView(ListCreateAPIView): # Bu view hem parçaların listelenmesini hem de parça üretilmesini sağlar
    permission_classes = [IsNotAircraftAssemblyTeam] # parça üretme ve listemem montaj ekibi dışında sistemde logi olmuş kullanıcıların hepsi yapabilecek

    def get_serializer_class(self): # Gelen methoda göre uygun serializer sınıfı seçilecek.
        if self.request.method == 'POST':
            return PartCreateSerializer
        return PartListSerializer

    def get_queryset(self, **kwargs: "Any") -> "QuerySet[Part]": # Get metodu yani Parçaları listemek için kullandığımız endpoint
        user = self.request.user

        # Kullanıcının takımı olup olmadığını kontrol ediyorum.
        if not user.team:
            return Part.objects.none()  # Boş queryset dönüyoruz.

        # sistemde var olabilecek takım listesi
        team_part_type_map = {
            "WING": "WING",
            "FUSELAGE": "FUSELAGE",
            "TAIL": "TAIL",
            "AVIONICS": "AVIONICS",
        }
        team_type = user.team.team_type
        part_type = team_part_type_map.get(team_type)

        if not part_type:
            return Part.objects.none()  # Boş queryset dönüyoruz.

        return Part.objects.filter(part_type=part_type).order_by('-created_at')

    def post(self, request, *args, **kwargs): #Parça üretmek için kullandığımız method
        data = request.data.copy() # bodyden gelen değerin kopyasını alıyoruz çünkü buraya user'ı eklicez o şekilde serializera göndericez.
        data['user'] = request.user.id
        serializer = self.get_serializer_class()(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_201_CREATED)


class PartRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [HasTeamAndNotAssembly]
    serializer_class = PartListSerializer

    def get_queryset(self):
        """
        Kullanıcının kendi takımının parçalarını döndürür.
        """
        user = self.request.user
        if not user.team:
            return Part.objects.none()

        # Kullanıcının takım tipine göre parça tipini belirle
        team_part_type_map = {
            "WING": "WING",
            "FUSELAGE": "FUSELAGE",
            "TAIL": "TAIL",
            "AVIONICS": "AVIONICS",
        }
        part_type = team_part_type_map.get(user.team.team_type)
        
        if not part_type:
            return Part.objects.none()

        return Part.objects.filter(part_type=part_type, user__team=user.team)

    def get_object(self):
        """
        Parçayı getirir ve izinleri kontrol eder.
        """
        obj = super().get_object()

        # Kullanılmış parçalar için 404 döndür
        if obj.used_in_plane:
            from django.http import Http404
            raise Http404("Bu parça bir uçakta kullanılmış")

        return obj

    def perform_destroy(self, instance):
        """
        Silme işlemi yerine `is_deleted=True` yapabiliriz.
        """
        instance.delete()

    def perform_update(self, serializer):
        """
        Parça güncellenirken gelen verileri günceller. Burada plane_type güncellenir ve diğer alanlar güncellenmez.
        """
        plane_type = self.request.data.get('plane_type')  # `plane_type`'ı alıyoruz
        if plane_type:
            if plane_type in [choice[0] for choice in Part.PlaneTypes.choices]:
                serializer.save(plane_type=plane_type)  # `plane_type` alanını güncelliyoruz
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f"Geçersiz plane_type: {plane_type}")
        else:
            serializer.save()  # plane_type yoksa diğer alanları güncelle


class PlaneAssemblyCreateView(ListCreateAPIView): #Uçak üretme ve uçakları listeleme endpointimiz budur.
    permission_classes = [IsAircraftAssemblyTeam] #Uçak üretme ve listelemeyi sadece Montaj takımına ait kullanıcılar gerçekleştirebilir.

    def get_serializer_class(self): # Burada get ve post işlemleri yapılabilir bu fonksiyonlada gelen methoda göre uygun serializer belirleniyor
        if self.request.method == 'POST':
            return CreatePlaneAssemblySerializer
        if self.request.method == "GET":
            return PlaneAssemblyListSerializer
    
    def get_queryset(self, **kwargs: "Any") -> "QuerySet[PlaneAssembly]": # Uçak listeleme
        return PlaneAssembly.objects.all().order_by('-created_at')

    def post(self, request, *args, **kwargs): # Uçak üretme
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer_class()(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_201_CREATED)
    


class PartScoreView(APIView): # Burada parçalardan kaç tanesi kullanıldı kaç tanesi kullanılmadı bunu gösteriyorum.
    permission_classes = [AircraftIsAuthenticated]  # Kullanıcı giriş yapmış olmalı

    def get(self, request, *args, **kwargs):
        """ Kullanıcının takımındaki parçaların tüm uçaklardaki kullanım durumunu döndürür. """
        user = request.user

        # Kullanıcının takımı olup olmadığını kontrol et
        if not user.team:
            return Response({"error": "Kullanıcının bir takımı yok."}, status=HTTP_400_BAD_REQUEST)

        # Takımın üretebildiği parçayı belirle
        team_part_type_map = {
            "WING": "WING",
            "FUSELAGE": "FUSELAGE",
            "TAIL": "TAIL",
            "AVIONICS": "AVIONICS",
            "ASSEMBLY": None  # Montaj ekibinin parçası yok
        }
        part_type_display_map = {
            "WING": "Kanat",
            "FUSELAGE": "Gövde",
            "TAIL": "Kuyruk",
            "AVIONICS": "Aviyonik"
        }
        team_type = user.team.team_type
        part_type = team_part_type_map.get(team_type)

        if not part_type:
            return Response({"error": "Bu takım parçalar üretmiyor."}, status=HTTP_400_BAD_REQUEST)

        # Tüm uçak modellerini içeren bir skor tablosu başlatım
        all_plane_types = ["TB2", "TB3", "AKINCI", "KIZILELMA"]
        plane_scores = {plane: {"used": 0, "unused": 0} for plane in all_plane_types}

        # Kullanıcının takımına ait parçaları uçak tiplerine göre gruplayarak filtreledim
        team_parts = Part.objects.filter(part_type=part_type)

        for part in team_parts:
            plane_scores[part.plane_type]["used" if part.used_in_plane else "unused"] += 1

        return Response({
            "team": user.team.get_team_type_display(),
            "part_type": part_type_display_map.get(part_type, part_type),
            "scores": plane_scores  # Her uçak modeli için kullanılan ve kullanılmayan parça sayısı
        }, status=HTTP_200_OK)