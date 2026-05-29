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

## Render Ornek Komutlari

Build command:

```bash
./build.sh
```

Start command:

```bash
gunicorn kentradar.wsgi:application
```
