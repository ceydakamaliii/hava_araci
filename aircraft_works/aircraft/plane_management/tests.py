from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from aircraft.accounts.models import User, Team
from aircraft.plane_management.models import Part, PlaneAssembly


class PartViewTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruzuyoruz"""
        # Test için takımları oluşturuyoruz
        self.wing_team = Team.objects.create(team_type="WING")
        self.assembly_team = Team.objects.create(team_type="ASSEMBLY")
        
        # Test için kullanıcıları oluşturuyoruz
        self.wing_user = User.objects.create_user(
            email="wing@example.com",
            password="test1234",
            team=self.wing_team
        )
        
        self.assembly_user = User.objects.create_user(
            email="assembly@example.com",
            password="test1234",
            team=self.assembly_team
        )
        
        self.no_team_user = User.objects.create_user(
            email="noteam@example.com",
            password="test1234"
        )
        
        # Test için örnek parçalar oluşturuyoruz
        self.wing_part = Part.objects.create(
            part_type="WING",
            plane_type="TB2",
            user=self.wing_user
        )

    def test_successful_part_listing(self):
        """Başarılı parça listeleme testi"""
        # Kanat takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_management')
        response = self.client.get(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Sadece kendi takımının parçalarını görebilmeli
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['part_type'], 'Kanat')

    def test_part_listing_without_auth(self):
        """Giriş yapmadan parça listeleme testi"""
        url = reverse('part_management')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_part_listing_without_team(self):
        """Takımı olmayan kullanıcı ile parça listeleme testi"""
        # Takımı olmayan kullanıcı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.no_team_user)
        
        url = reverse('part_management')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_part_listing_with_assembly_team(self):
        """Montaj takımı ile parça listeleme testi"""
        # Montaj takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('part_management')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_part_creation(self):
        """Başarılı parça oluşturma testi"""
        # Kanat takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_management')
        data = {
            'part_type': 'WING',
            'plane_type': 'TB2',
            'quantity': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Parça oluşturuyoruzulmuş olmalı
        self.assertEqual(Part.objects.count(), 2)  # setUp'taki parça + yeni parça
        
        # Parça bilgileri doğru kaydedilmiş olmalı
        new_part = Part.objects.latest('created_at')
        self.assertEqual(new_part.part_type, 'WING')
        self.assertEqual(new_part.plane_type, 'TB2')
        self.assertEqual(new_part.user, self.wing_user)

    def test_part_creation_with_wrong_part_type(self):
        """Yanlış parça tipi ile oluşturuyoruzma testi"""
        # Kanat takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_management')
        data = {
            'part_type': 'INVALID_TYPE',  # Geçersiz parça tipi
            'plane_type': 'TB2',
            'quantity': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('part_type', str(response.data))

    def test_part_creation_with_wrong_team_type(self):
        """Takımına uygun olmayan parça oluşturuyoruzma testi"""
        # Kanat takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_management')
        data = {
            'part_type': 'FUSELAGE',  # Kanat takımı gövde parçası üretemez
            'plane_type': 'TB2',
            'quantity': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Gövde parçalarını sadece Gövde ekibi üretebilir', str(response.data))

    def test_part_creation_with_assembly_team(self):
        """Montaj takımı ile parça oluşturuyoruzma testi"""
        # Montaj takımı kullanıcısı ile giriş yapıyoruz
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('part_management')
        data = {
            'part_type': 'WING',
            'plane_type': 'TB2',
            'quantity': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_part_creation_without_auth(self):
        """Giriş yapmadan parça oluşturma testi"""
        url = reverse('part_management')
        data = {
            'part_type': 'WING',
            'plane_type': 'TB2',
            'quantity': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PartScoreTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruz"""
        # Test için takımları oluştur
        self.wing_team = Team.objects.create(team_type="WING")
        self.assembly_team = Team.objects.create(team_type="ASSEMBLY")
        
        # Test için kullanıcıları oluştur
        self.wing_user = User.objects.create_user(
            email="wing@example.com",
            password="test1234",
            team=self.wing_team
        )
        
        self.assembly_user = User.objects.create_user(
            email="assembly@example.com",
            password="test1234",
            team=self.assembly_team
        )
        
        self.no_team_user = User.objects.create_user(
            email="noteam@example.com",
            password="test1234"
        )
        
        # Test için örnek parçalar oluştur
        # TB2 için parçalar
        self.wing_part_tb2_used = Part.objects.create(
            part_type="WING",
            plane_type="TB2",
            user=self.wing_user,
            used_in_plane=True
        )
        
        self.wing_part_tb2_unused = Part.objects.create(
            part_type="WING",
            plane_type="TB2",
            user=self.wing_user,
            used_in_plane=False
        )
        
        # TB3 için parçalar
        self.wing_part_tb3_used = Part.objects.create(
            part_type="WING",
            plane_type="TB3",
            user=self.wing_user,
            used_in_plane=True
        )
        
        self.wing_part_tb3_unused1 = Part.objects.create(
            part_type="WING",
            plane_type="TB3",
            user=self.wing_user,
            used_in_plane=False
        )
        
        self.wing_part_tb3_unused2 = Part.objects.create(
            part_type="WING",
            plane_type="TB3",
            user=self.wing_user,
            used_in_plane=False
        )

    def test_successful_part_score_retrieval(self):
        """Başarılı parça skor görüntüleme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('parts_score')
        response = self.client.get(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Dönen veriler doğru olmalı
        self.assertEqual(response.data['team'], 'Kanat Takımı')
        self.assertEqual(response.data['part_type'], 'Kanat')
        
        # TB2 skorları kontrol et
        self.assertEqual(response.data['scores']['TB2']['used'], 1)
        self.assertEqual(response.data['scores']['TB2']['unused'], 1)
        
        # TB3 skorları kontrol et
        self.assertEqual(response.data['scores']['TB3']['used'], 1)
        self.assertEqual(response.data['scores']['TB3']['unused'], 2)
        
        # AKINCI ve KIZILELMA skorları 0 olmalı
        self.assertEqual(response.data['scores']['AKINCI']['used'], 0)
        self.assertEqual(response.data['scores']['AKINCI']['unused'], 0)
        self.assertEqual(response.data['scores']['KIZILELMA']['used'], 0)
        self.assertEqual(response.data['scores']['KIZILELMA']['unused'], 0)

    def test_part_score_without_auth(self):
        """Giriş yapmadan parça skor görüntüleme testi"""
        url = reverse('parts_score')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED or status.HTTP_403_FORBIDDEN)

    def test_part_score_without_team(self):
        """Takımı olmayan kullanıcı ile parça skor görüntüleme testi"""
        # Takımı olmayan kullanıcı ile giriş yap
        self.client.force_authenticate(user=self.no_team_user)
        
        url = reverse('parts_score')
        response = self.client.get(url)
        
        # Bad request veya Forbidden almalıyız
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEqual(response.data['error'], "Kullanıcının bir takımı yok.")

    def test_part_score_with_assembly_team(self):
        """Montaj takımı ile parça skor görüntüleme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('parts_score')
        response = self.client.get(url)
        
        # Bad request veya Forbidden almalıyız
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertEqual(response.data['error'], "Bu takım parçalar üretmiyor.")


class PlaneAssemblyTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruz"""
        # Test için takımları oluştur
        self.wing_team = Team.objects.create(team_type="WING")
        self.fuselage_team = Team.objects.create(team_type="FUSELAGE")
        self.tail_team = Team.objects.create(team_type="TAIL")
        self.avionics_team = Team.objects.create(team_type="AVIONICS")
        self.assembly_team = Team.objects.create(team_type="ASSEMBLY")
        
        # Test için kullanıcıları oluştur
        self.wing_user = User.objects.create_user(
            email="wing@example.com",
            password="test1234",
            team=self.wing_team
        )
        
        self.fuselage_user = User.objects.create_user(
            email="fuselage@example.com",
            password="test1234",
            team=self.fuselage_team
        )
        
        self.tail_user = User.objects.create_user(
            email="tail@example.com",
            password="test1234",
            team=self.tail_team
        )
        
        self.avionics_user = User.objects.create_user(
            email="avionics@example.com",
            password="test1234",
            team=self.avionics_team
        )
        
        self.assembly_user = User.objects.create_user(
            email="assembly@example.com",
            password="test1234",
            team=self.assembly_team
        )
        
        self.no_team_user = User.objects.create_user(
            email="noteam@example.com",
            password="test1234"
        )
        
        # Test için örnek parçalar oluştur
        # AKINCI için parçalar
        self.wing_parts = [
            Part.objects.create(
                part_type="WING",
                plane_type="AKINCI",
                user=self.wing_user
            ) for _ in range(2)
        ]
        
        self.fuselage_part = Part.objects.create(
            part_type="FUSELAGE",
            plane_type="AKINCI",
            user=self.fuselage_user
        )
        
        self.tail_part = Part.objects.create(
            part_type="TAIL",
            plane_type="AKINCI",
            user=self.tail_user
        )
        
        self.avionics_part = Part.objects.create(
            part_type="AVIONICS",
            plane_type="AKINCI",
            user=self.avionics_user
        )

    def test_successful_plane_assembly(self):
        """Başarılı uçak üretme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": [
                {
                    "part_type": "FUSELAGE",
                    "plane_type": "AKINCI",
                    "amount": 1
                },
                {
                    "part_type": "WING",
                    "plane_type": "AKINCI",
                    "amount": 2
                },
                {
                    "part_type": "TAIL",
                    "plane_type": "AKINCI",
                    "amount": 1
                },
                {
                    "part_type": "AVIONICS",
                    "plane_type": "AKINCI",
                    "amount": 1
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Uçak oluşturulmuş olmalı
        self.assertEqual(PlaneAssembly.objects.count(), 1)
        
        # Parçalar kullanılmış olarak işaretlenmeli
        for wing_part in self.wing_parts:
            wing_part.refresh_from_db()
            self.assertTrue(wing_part.used_in_plane)
        
        self.fuselage_part.refresh_from_db()
        self.assertTrue(self.fuselage_part.used_in_plane)
        
        self.tail_part.refresh_from_db()
        self.assertTrue(self.tail_part.used_in_plane)
        
        self.avionics_part.refresh_from_db()
        self.assertTrue(self.avionics_part.used_in_plane)

    def test_plane_assembly_without_auth(self):
        """Giriş yapmadan uçak üretme testi"""
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": []
        }
        
        response = self.client.post(url, data, format='json')
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_plane_assembly_with_non_assembly_team(self):
        """Montaj takımı dışındaki takımla uçak üretme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": []
        }
        
        response = self.client.post(url, data, format='json')
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_plane_assembly_with_missing_parts(self):
        """Eksik parçalarla uçak üretme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": [
                {
                    "part_type": "WING",
                    "plane_type": "AKINCI",
                    "amount": 2
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Eksik parçalar var", str(response.data))

    def test_plane_assembly_with_wrong_part_amounts(self):
        """Yanlış parça miktarlarıyla uçak üretme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": [
                {
                    "part_type": "FUSELAGE",
                    "plane_type": "AKINCI",
                    "amount": 2  # Gövde 1 adet olmalı
                },
                {
                    "part_type": "WING",
                    "plane_type": "AKINCI",
                    "amount": 1  # Kanat 2 adet olmalı
                },
                {
                    "part_type": "TAIL",
                    "plane_type": "AKINCI",
                    "amount": 1
                },
                {
                    "part_type": "AVIONICS",
                    "plane_type": "AKINCI",
                    "amount": 1
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_plane_assembly_with_mismatched_plane_types(self):
        """Farklı uçak tiplerinin parçalarıyla uçak üretme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('plane_management')
        data = {
            "plane_type": "AKINCI",
            "parts_used": [
                {
                    "part_type": "FUSELAGE",
                    "plane_type": "TB2",  # AKINCI için TB2 parçası kullanılamaz
                    "amount": 1
                },
                {
                    "part_type": "WING",
                    "plane_type": "AKINCI",
                    "amount": 2
                },
                {
                    "part_type": "TAIL",
                    "plane_type": "AKINCI",
                    "amount": 1
                },
                {
                    "part_type": "AVIONICS",
                    "plane_type": "AKINCI",
                    "amount": 1
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("TB2 FUSELAGE parçası AKINCI uçağına takılamaz", str(response.data))

    def test_successful_plane_listing(self):
        """Başarılı uçak listeleme testi"""
        # Önce bir uçak oluştur
        self.test_successful_plane_assembly()
        
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('plane_management')
        response = self.client.get(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Bir uçak listelenmiş olmalı
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['plane_type'], 'AKINCI')
        
        # Parçalar da listelenmiş olmalı
        parts_used = response.data['results'][0]['parts_used']
        self.assertGreaterEqual(len(parts_used), 5)  # En az 2 kanat + 1 gövde + 1 kuyruk + 1 aviyonik olmalı


class PartDetailTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruz"""
        # Test için takımları oluştur
        self.wing_team = Team.objects.create(team_type="WING")
        self.fuselage_team = Team.objects.create(team_type="FUSELAGE")
        self.assembly_team = Team.objects.create(team_type="ASSEMBLY")
        
        # Test için kullanıcıları oluştur
        self.wing_user = User.objects.create_user(
            email="wing@example.com",
            password="test1234",
            team=self.wing_team
        )
        
        self.fuselage_user = User.objects.create_user(
            email="fuselage@example.com",
            password="test1234",
            team=self.fuselage_team
        )
        
        self.assembly_user = User.objects.create_user(
            email="assembly@example.com",
            password="test1234",
            team=self.assembly_team
        )
        
        self.no_team_user = User.objects.create_user(
            email="noteam@example.com",
            password="test1234"
        )
        
        # Test için örnek parçalar oluştur
        self.wing_part = Part.objects.create(
            part_type="WING",
            plane_type="TB2",
            user=self.wing_user
        )
        
        self.used_wing_part = Part.objects.create(
            part_type="WING",
            plane_type="TB2",
            user=self.wing_user,
            used_in_plane=True
        )
        
        self.fuselage_part = Part.objects.create(
            part_type="FUSELAGE",
            plane_type="TB2",
            user=self.fuselage_user
        )

    def test_successful_part_detail_retrieval(self):
        """Başarılı parça detay görüntüleme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        response = self.client.get(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Dönen veriler doğru olmalı
        self.assertEqual(response.data['part_type'], 'Kanat')
        self.assertEqual(response.data['plane_type'], 'TB2')
        self.assertEqual(response.data['team'], 'Kanat Takımı')
        self.assertFalse(response.data['used_in_plane'])

    def test_part_detail_without_auth(self):
        """Giriş yapmadan parça detay görüntüleme testi"""
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_part_detail_with_assembly_team(self):
        """Montaj takımı ile parça detay görüntüleme testi"""
        # Montaj takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.assembly_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        response = self.client.get(url)
        
        # Boş queryset dönmeli
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_part_detail_with_wrong_team(self):
        """Yanlış takım ile parça detay görüntüleme testi"""
        # Gövde takımı kullanıcısı ile kanat parçasına erişmeye çalış
        self.client.force_authenticate(user=self.fuselage_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        response = self.client.get(url)
        
        # Parça bulunamadı hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_used_part_detail(self):
        """Kullanılmış parça detay görüntüleme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_details', kwargs={'pk': self.used_wing_part.id})
        response = self.client.get(url)
        
        # Parça bulunamadı hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Bu parça bir uçakta kullanılmış", str(response.data))

    def test_successful_part_update(self):
        """Başarılı parça güncelleme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        data = {
            'plane_type': 'TB3'
        }
        
        response = self.client.patch(url, data, format='json')
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parça güncellenmiş olmalı
        self.wing_part.refresh_from_db()
        self.assertEqual(self.wing_part.plane_type, 'TB3')

    def test_part_update_with_invalid_plane_type(self):
        """Geçersiz uçak tipi ile parça güncelleme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        data = {
            'plane_type': 'INVALID_TYPE'
        }
        
        response = self.client.patch(url, data, format='json')
        
        # Validasyon hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is not a valid choice', str(response.data))

    def test_successful_part_deletion(self):
        """Başarılı parça silme testi"""
        # Kanat takımı kullanıcısı ile giriş yap
        self.client.force_authenticate(user=self.wing_user)
        
        url = reverse('part_details', kwargs={'pk': self.wing_part.id})
        response = self.client.delete(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Parça silinmiş olmalı
        with self.assertRaises(Part.DoesNotExist):
            self.wing_part.refresh_from_db()


