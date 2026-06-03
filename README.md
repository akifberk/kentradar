# KentRadar

KentRadar, vatandaş şikayetlerini konum, fotoğraf, kategori ve açıklama ile toplayan; yetkili kullanıcılara harita, panel, grafik ve rapor ekranları sunan Django projesidir.

## Yerelde Calistirma

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Adresler:

- Harita: `http://127.0.0.1:8000/`
- Şikayet bildir: `http://127.0.0.1:8000/bildir/`
- Panel: `http://127.0.0.1:8000/panel/`
- Rapor: `http://127.0.0.1:8000/rapor/`
- Admin: `http://127.0.0.1:8000/admin/`

## Deploy Ortam Degiskenleri

`.env.example` dosyasındaki değerleri hosting panelindeki environment variables alanına ekleyin.

`DEBUG=False` yapıldığında `SECRET_KEY`, `ALLOWED_HOSTS` ve `CSRF_TRUSTED_ORIGINS` değerlerini canlı domaininize göre girin.

Mobil uygulamadan yetkili POST atmak için `MOBILE_API_KEY` belirleyin ve isteğe `X-API-Key` header'ı olarak ekleyin. Giriş yapmış web kullanıcıları da API üzerinden kayıt oluşturabilir.

Flutter uygulaması için token tabanlı endpointler:

- `POST /api/mobile/register/`
- `POST /api/mobile/login/`
- `POST /api/mobile/logout/`
- `POST /api/mobile/password-reset/`
- `GET,POST /api/mobile/complaints/`
- `GET,PATCH,DELETE /api/mobile/complaints/<id>/`
- `GET /api/mobile/panel/`
- `GET /api/mobile/report/?start_date=2026-05-01&end_date=2026-05-31&category=road&status=open`

Login/register cevabindaki token sonraki isteklerde `Authorization: Token TOKEN_DEGERI` header'i ile gonderilir.

## Render Ornek Komutlari

Bu repo Render Blueprint ile hazırlanmıştır. GitHub/GitLab/Bitbucket reposuna push ettikten sonra Render Dashboard > Blueprints > New Blueprint Instance adımından repoyu seçin ve `render.yaml` dosyasını uygulatın. Render web servisini, Postgres veritabanını ve gerekli ortam değişkenlerini otomatik oluşturur.

Blueprint disinda manuel kurulum yapmak isterseniz:

Build command:

```bash
./build.sh
```

Start command:

```bash
gunicorn kentradar.wsgi:application
```

Gerekli ortam değişkenleri:

- `DATABASE_URL`: Render Postgres internal connection string
- `SECRET_KEY`: Render uzerinden uretilmis gizli anahtar
- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com` veya kendi domaininiz
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com` veya kendi domaininizin HTTPS adresi
- `MOBILE_API_KEY`: Mobil uygulama için ortak API anahtarı

Canlı URL oluştuktan sonra Render Shell'de admin kullanıcı oluşturun:

```bash
python manage.py createsuperuser
```

Not: Render'in geçici dosya sistemi yüklenen medya dosyalarını kalıcı tutmaz. Şikayet fotoğraflarını kalıcı saklamak için production ortamında S3/Cloudinary gibi harici medya depolama ekleyin veya uygun Render disk planı kullanın.

## Teslim Kontrol

- Login/Register: `/hesap/login/`, `/kullanici/kayit/`
- Şifre sıfırlama: `/hesap/password_reset/`
- Roller: Admin/staff ve standart kullanıcı profilleri
- CRUD: `/bildir/`, `/sikayet/<id>/`, düzenle ve sil ekranları
- Mobil API: `/api/mobile/complaints/`
- Mobil Auth API: `/api/mobile/register/`, `/api/mobile/login/`, `/api/mobile/password-reset/`
- Yetkili panel: `/panel/`
- Grafik: panelde kategori pasta grafik ve aylık kayıt sütun grafik
- Rapor: `/rapor/`, tarih/kategori/durum filtresi ve Yazdır/PDF butonu
- Harita: `/`, kategori renklerine göre baloncuklar
