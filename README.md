# KentRadar

KentRadar, vatandas sikayetlerini konum, fotograf, kategori ve aciklama ile toplayan; yetkili kullanicilara harita, panel, grafik ve rapor ekranlari sunan Django projesidir.

## Yerelde Calistirma

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Adresler:

- Harita: `http://127.0.0.1:8000/`
- Sikayet bildir: `http://127.0.0.1:8000/bildir/`
- Panel: `http://127.0.0.1:8000/panel/`
- Rapor: `http://127.0.0.1:8000/rapor/`
- Admin: `http://127.0.0.1:8000/admin/`

## Deploy Ortam Degiskenleri

`.env.example` dosyasindaki degerleri hosting panelindeki environment variables alanina ekleyin.

`DEBUG=False` yapildiginda `SECRET_KEY`, `ALLOWED_HOSTS` ve `CSRF_TRUSTED_ORIGINS` degerlerini canli domaininize gore girin.

Mobil uygulamadan yetkili POST atmak icin `MOBILE_API_KEY` belirleyin ve istege `X-API-Key` header'i olarak ekleyin. Giris yapmis web kullanicilari da API uzerinden kayit olusturabilir.

Flutter uygulamasi icin token tabanli endpointler:

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

Bu repo Render Blueprint ile hazirlanmistir. GitHub/GitLab/Bitbucket reposuna push ettikten sonra Render Dashboard > Blueprints > New Blueprint Instance adimindan repoyu secin ve `render.yaml` dosyasini uygulatin. Render web servisini, Postgres veritabanini ve gerekli ortam degiskenlerini otomatik olusturur.

Blueprint disinda manuel kurulum yapmak isterseniz:

Build command:

```bash
./build.sh
```

Start command:

```bash
gunicorn kentradar.wsgi:application
```

Gerekli ortam degiskenleri:

- `DATABASE_URL`: Render Postgres internal connection string
- `SECRET_KEY`: Render uzerinden uretilmis gizli anahtar
- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com` veya kendi domaininiz
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com` veya kendi domaininizin HTTPS adresi
- `MOBILE_API_KEY`: Mobil uygulama icin ortak API anahtari

Canli URL olustuktan sonra Render Shell'de admin kullanici olusturun:

```bash
python manage.py createsuperuser
```

Not: Render'in gecici dosya sistemi yuklenen medya dosyalarini kalici tutmaz. Sikayet fotograflarini kalici saklamak icin production ortaminda S3/Cloudinary gibi harici medya depolama ekleyin veya uygun Render disk plani kullanin.

## Teslim Kontrol

- Login/Register: `/hesap/login/`, `/kullanici/kayit/`
- Sifre sifirlama: `/hesap/password_reset/`
- Roller: Admin/staff ve standart kullanici profilleri
- CRUD: `/bildir/`, `/sikayet/<id>/`, duzenle ve sil ekranlari
- Mobil API: `/api/mobile/complaints/`
- Mobil Auth API: `/api/mobile/register/`, `/api/mobile/login/`, `/api/mobile/password-reset/`
- Yetkili panel: `/panel/`
- Grafik: panelde kategori pasta grafik ve aylik kayit sutun grafik
- Rapor: `/rapor/`, tarih/kategori/durum filtresi ve Yazdir/PDF butonu
- Harita: `/`, kategori renklerine gore baloncuklar
