# BACKEND KULLANIM KILAVUZU

## Projeyi başlatma adımları ve bazı önemli bilgiler

1. Docker içine girmeliyiz bilgisayarınızda docker yoksa kurunuz. Python versiyonum 3.13.1'dir.
2. Containerları oluşturmak için `source tools/docker-development.sh` komutunu çalıştırınız.
3. Docker dashboarddan 2 tane container oluştuğunu doğrulayın veya `docker ps` komutu ile oluşan containerların çalışıyor durumda olduğunu kontrol edin 2 cointainerda çalışır durumda olmalı ve docker ps komutu çıktısında gözükmeli. Eğer gözükmeyen varsa docker dashboarddan container'ı run edebilirsiniz.
4. Container içine girmek için `docker exec -it aircraft bash` komutunu çalıştırabilirsiniz. Venv oluşturmak için `python -m venv venv` komutunu çalıştırınız. Venv'i aktif etmek için `source venv/bin/activate` komutunu çalıştırınız. Veya tools olarak yazmış olduğum `source tools/activate-venv.sh` komutunu çalıştırabilirsiniz.
5. Containerlar oluşma aşamasında zaten gerekli paketler yüklenecektir. Ama ayrıyetten manuel olarakda yüklemek isterseniz container içindeyken `pip install -r requirements/base.pip` komutunu ardından `pip install -r requirements/dev.pip` komutunu ve en son `pip install -r requirements/constraints.pip` komutunu çalıştırabilirsiniz.
6. Proje gereksinimleri yüklendiğine göre artık projemizi çalıştırabiliriz docker içindeyken `python manage.py runserver 0:8000` komutunu çalıştırın. burada sizden migrate işlemleri yapmanız istenicek. `python manage.py migrate` komutunu çalıştırınız.
7. Projeyi çalıştırdıktan sonra `http://localhost:8000` adresine giderek projeyi görebilirsiniz.
8. Admin panele erişmek için `http://localhost:8000/cp` adresine gidebilirsiniz.
9. Admin panelde giriş yapmak için superuser oluşturmanız gerekir. Bunun adımları şu şekildedir:
   - Docker içindeyken `python manage.py createsuperuser` komutunu çalıştırın.
   - Bu komut size email, password ve confirm password değerlerini soracak bu bilgileri girdikten sonra database'e kaydedecektir.
10. Admin panele giriş yaptıktan sonra modelleri görüntüleyebilirsiniz. Modellere eleman ekleyebilirsiniz.
11. Swagger entegre edilmiş durumdadır ve swagger'a erişmek için `http://0.0.0.0:8000/api/schema/swagger-ui/` adresine gidebilirsiniz.
12. Swagger'da endpointleri test edebilir dönen response'ları görüntüleyebilirsiniz.
13. Bazı endpointlere erişmek için token gerekmektedir. Token almak için swaggerda POST isteği olan `/api/v1/users/token/` endpointine istekte bulunmanız gerekicek. Bu endpointe bodyde email ve password bilgilerini göndererek token alabilirsiniz. `Access token` ve Refresh token değerleri dönecektir. Buradan dönen Access token değerini kopyalayınız. Kopyaladığınız değeri sayfanın en üstünde sağ tarafta bulunan `Authorize` butonunun `jwtAuth` kısmına yapıştırınız ve Authorize butonuna tıklayınız.
14. Projeyi çalıştırdığınızda takımlar daha oluşmamış olucaktır. Bu durum için bir management command yazdım. Bu management command accounts folderı altında management klasörü altında create_teams.py adıyla mevcuttur. Bu command'i çalıştırdığınızda takımlar veritabanınıza kaydedilecektir. Bu management command'i çalıştırmak için docker içinde `python manage.py create_teams` kodunu çalıştırınız. Veya dilerseniz admin panelden ekleyebilirsiniz. Eğer bu iki yoluda yapmak istemezseniz zaten kullanıcı oluşturma aşamasında backendde yollamış olduğunuz team_name'e göre bir sorgu atıyoruz(get_or_create) geçerli bir takım adı (WING, FUSELAGE, TAIL, AVIONICS, ASSEMBLY) girerseniz kullanıcıdan önce takımınız oluşturulmuş oluyor.
15. Önemli bir nokta olan Uçak üretme endpointine vermeniz gereken body formatı şu şekildedir:
    ```json
    {
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
    ```
16. Uçak 1 gövdeden, 2 kanatten, 1 kuyruktan ve 1 veya da fazla avionikten oluşmaktadır. bu yüzden bu değerlerden fazla veya az değer gönderirseniz hata alırsınız.
17. Team modeli yani Takım modeli için team_type değeri için 5 farklı değer vardır. Bunlar:
    - WING
    - FUSELAGE
    - TAIL
    - AVIONICS
    - ASSEMBLY
      Burada ingilizce değerleri ile backendde istekte bulunuyoruz ve backendden bazı endpointler için response'u ingilizce döndürüyorum ama unutmamız gereken nokta burada WING kanatı ifade eder, FUSELAGE ise gövdeyi ifade eder, TAIL ise kuyruğu ifade eder, AVIONICS ise avionikleri ifade eder ve ASSEMBLY ise montajı ifade eder.
18. Unutmayın swaggerdan endpoint test ederken team değeri göndericekseniz ingilizce değerini göndermelisiniz.
19. Parçaları tuttuğum modelin adı `Part` modelidir. Bu modelde part_type değeri için 4 farklı değer vardır. Bunlar:
    - FUSELAGE
    - WING
    - TAIL
    - AVIONICS
      Burada da Team modelinde olduğu gibi ingilizce değerleri ile backendde istekte bulunuyoruz ve backendden bazı endpointler için response'u ingilizce karşılığını döndürüyorum ama burada FUSELAGE gövdeyi ifade eder, WING ise kanatı ifade eder, TAIL ise kuyruğu ifade eder ve AVIONICS ise avionikleri ifade eder.
20. Yazmış olduğum endpointlerin hepsi swaggerda mevcuttur.
21. Yazmış olduğum endpointler için birim testleri yazdım.
22. Birim testleri çalıştırmak için docker içinde olmanız gerekir.
23. Account işlemleri yani kullanıcı işlemleri için (SignUp, Login, Logout, UserDetail...) yazmış olduğum testleri çalıştırmak isterseniz `python manage.py test aircraft.accounts.tests.SignUpTests -v 2`,`python manage.py test aircraft.accounts.tests.LoginTests -v 2`,`python manage.py test aircraft.accounts.tests.UserDetailTests -v 2`komutlarını terminalinizde çalıştırınız.
24. Uçak işlemleri için (Uçak oluşturma, Uçak listeleme, Parça oluşturma, Parça listeleme, Parça silme, Parça istatistiklerini görme...) yazmış olduğum testleri çalıştırmak isterseniz `python manage.py test aircraft.plane_management.tests.PartViewTests -v 2`, `python manage.py test aircraft.plane_management.tests.PartScoreTests -v 2`, `python manage.py test aircraft.plane_management.tests.PlaneAssemblyTests -v 2`,`python manage.py test aircraft.plane_management.tests.PartDetailTests -v 2` komutlarını çalıştırabilirsiniz.

# FRONTEND KULLANIM KILAVUZU

## Aircraft Parça Yönetim Sistemi

Bu proje, uçak parçalarının üretim ve montaj süreçlerini yönetmek için geliştirilmiş bir web uygulamasıdır. Farklı takımların ürettikleri parçaları takip edebilecekleri ve montaj ekibinin bu parçaları uçaklarda kullanabilecekleri bir platform sunar.

## Başlangıç

### Gereksinimler

- Node.js (v18 veya üzeri)
- Bilgisayarınızda pnpm yüklü olmalıdır yüklü değilse pnpm'i bilgisayarınıza yükleyiniz. Bilgisayarınızda npm yüklü ise `npm install -g pnpm` ile yükleyebilirsiniz. Mac kullanıyorsanız homebrew ile yükleyebilirsiniz `brew install pnpm`. 

### Kurulum

1. " pnpm install " ile gerekli paketleri yükleyin

2. Geliştirme sunucusunu başlatma:
   " pnpm dev " veya "pnpm run dev"

Uygulama http://localhost:3000 adresinde çalışmaya başlayacaktır.

## Özellikler

- 🔐 Kullanıcı Yetkilendirme Sistemi

  - Güvenli giriş ve kayıt işlemleri
  - Takım bazlı yetkilendirme
  - JWT tabanlı kimlik doğrulama

- 👥 Takım Yönetimi

  - Kanat Takımı
  - Gövde Takımı
  - Kuyruk Takımı
  - Aviyonik Takımı
  - Montaj Takımı

- ✈️ Uçak Modelleri

  - TB2
  - TB3
  - AKINCI
  - KIZILELMA

- 📊 Parça Yönetimi
  - Parça oluşturma ve silme
  - Parça durumu takibi (Depoda/Kullanımda)
  - Parça skorları ve istatistikleri

## Teknolojiler

- **Frontend**

  - Next.js 15.1.6
  - TypeScript
  - Tailwind CSS
  - Radix UI
  - Tanstack Table
  - date-fns
  - Lucide Icons

- **State Yönetimi**

  - React Context API
  - Custom Hooks

- **Kimlik Doğrulama**
  - JWT (Access ve Refresh Token)
  - HTTP-only Cookies

### Kayıt ve Giriş

1. Yeni kullanıcılar "/signup" sayfasından kayıt olabilir
2. Kayıt sırasında:

   - Email
   - Şifre
   - Ad
   - Soyad
   - Takım seçimi gereklidir

3. Mevcut kullanıcılar "/login" sayfasından giriş yapabilir

### Dashboard

- Her takım kendi ürettiği parçaları görebilir ve yönetebilir
- Montaj takımı tüm parçaları görüntüleyebilir ve uçaklara atayabilir
- Parça skorları ve istatistikler dashboard üzerinden takip edilebilir

### Parça İşlemleri

- Yeni parça oluşturma
- Parça silme (kullanımda olmayan parçalar için)
- Parça durumu güncelleme
- Parça kullanım geçmişi görüntüleme

## Güvenlik

- Tüm API istekleri JWT token ile yetkilendirilir
- Access ve Refresh token'lar güvenli cookie'lerde saklanır
- CSRF koruması implementedir
- Rate limiting uygulanmıştır

## Hata Yönetimi

- Kullanıcı dostu hata mesajları
- Toast bildirimleri ile anlık geri bildirim
- Form validasyonları
- API hata yakalama ve işleme
