from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from aircraft.accounts.models import User, Team
from aircraft.plane_management.models import Part
from rest_framework_simplejwt.tokens import RefreshToken

class SignUpTests(APITestCase):
    def test_successful_signup(self):
        """Başarılı kayıt testi"""
        url = reverse('sign_up')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "user@example.com",
            "team_name": "WING",  # Team.Team choices'dan biri
            "password": "test1234"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Kayıt başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Kullanıcı ve takım oluşturulmuş olmalı
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Team.objects.count(), 1)
        
        # Kullanıcı bilgileri doğru kaydedilmiş olmalı
        user = User.objects.get()
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.team.team_type, "WING")

    def test_signup_with_invalid_team(self):
        """Geçersiz takım ile kayıt testi"""
        url = reverse('sign_up')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "user@example.com",
            "team_name": "INVALID_TEAM",  # Geçersiz takım tipi
            "password": "test1234"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Kayıt başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('team_name', response.data['detail'])
        self.assertIn('Geçersiz takım adı', str(response.data['detail']['team_name'][0]))
        
        # Kullanıcı ve takım oluşturulmamalı
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Team.objects.count(), 0)

    def test_signup_without_team_name(self):
        """Takım adı olmadan kayıt testi"""
        url = reverse('sign_up')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "user@example.com",
            "password": "test1234"
            # team_name eksik
        }
        
        response = self.client.post(url, data, format='json')
        
        # Kayıt başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # API'nin döndüğü gerçek hata mesajını kontrol et
        self.assertIn('team_name', response.data['detail'])
        
        # Kullanıcı ve takım oluşturulmamalı
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Team.objects.count(), 0)

    def test_signup_with_existing_email(self):
        """Var olan email ile kayıt testi"""
        # Önce bir kullanıcı oluşturalım
        User.objects.create_user(
            email="user@example.com",
            password="test1234",
            team=Team.objects.create(team_type="WING")
        )
        
        url = reverse('sign_up')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "user@example.com",  # Var olan email
            "team_name": "WING",
            "password": "test1234"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Kayıt başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['detail'])
        
        # Yeni kullanıcı oluşturulmamalı
        self.assertEqual(User.objects.count(), 1)

    def test_signup_with_long_names(self):
        """Uzun isimlerle kayıt testi"""
        url = reverse('sign_up')
        data = {
            "first_name": "H" * 101,  # 101 karakter (max 100)
            "last_name": "U" * 101,   # 101 karakter (max 100)
            "email": "user@example.com",
            "team_name": "WING",
            "password": "test1234"
        }
        
        response = self.client.post(url, data, format='json')
        
        # Kayıt başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data['detail'])
        self.assertIn('last_name', response.data['detail'])
        
        # Kullanıcı oluşturulmamalı
        self.assertEqual(User.objects.count(), 0)


class LoginTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruz"""
        # Test için takım oluştur
        self.team = Team.objects.create(team_type="WING")
        
        # Test için kullanıcı oluştur
        self.user = User.objects.create(
            email="test@example.com",
            team=self.team
        )
        self.user.set_password("test1234")
        self.user.save()

    def test_successful_login(self):
        """Başarılı giriş testi"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'test1234'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Token'lar dönmeli
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Token'lar string olmalı
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)

    def test_login_with_nonexistent_email(self):
        """Var olmayan email ile giriş testi"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'test1234'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarısız olmalı - API 400 dönüyor
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Sağlanan kimlik bilgilerine sahip böyle bir kullanıcı yok', str(response.data))

    def test_login_with_wrong_password(self):
        """Yanlış şifre ile giriş testi"""
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrong_password'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('No active account found with the given credentials', str(response.data))

    def test_login_without_email(self):
        """Email olmadan giriş testi"""
        url = reverse('login')
        data = {
            'password': 'test1234'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['detail'])

    def test_login_without_password(self):
        """Şifre olmadan giriş testi"""
        url = reverse('login')
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['detail'])

    def test_login_with_inactive_user(self):
        """Aktif olmayan kullanıcı ile giriş testi"""
        # Kullanıcıyı deaktif et
        self.user.is_active = False
        self.user.save()
        
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'test1234'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Giriş başarısız olmalı
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserDetailTests(APITestCase):
    def setUp(self):
        """Test öncesi gerekli verileri oluşturuyoruz"""
        # Test için takım oluştur
        self.team = Team.objects.create(team_type="WING")
        
        # Test için kullanıcı oluştur
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            team=self.team,
            is_active=True
        )
        self.user.set_password("test1234")
        self.user.save()

    def test_successful_user_detail_retrieval(self):
        """Başarılı kullanıcı detayı görüntüleme testi"""
        # Kullanıcı girişi yap
        self.client.force_authenticate(user=self.user)
        
        url = reverse('my_user_details')
        response = self.client.get(url)
        
        # İstek başarılı olmalı
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Dönen veriler doğru olmalı
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertEqual(response.data['team_name'], 'WING')
        self.assertTrue(response.data['is_active'])
        self.assertFalse(response.data['is_admin'])

    def test_user_detail_without_auth(self):
        """Giriş yapmadan kullanıcı detayı görüntüleme testi"""
        url = reverse('my_user_details')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_detail(self):
        """Deaktif edilmiş kullanıcı ile detay görüntüleme testi"""
        # Kullanıcıyı deaktif et
        self.user.is_active = False
        self.user.save()
        
        # Kullanıcı girişi yap
        self.client.force_authenticate(user=self.user)
        
        url = reverse('my_user_details')
        response = self.client.get(url)
        
        # Yetkisiz erişim hatası almalıyız - deaktif kullanıcılar için 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)