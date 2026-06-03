# KentRadar Teslim Kontrolu

## Rubrik Maddeleri

| Madde | Durum | Projede Karsiligi |
| --- | --- | --- |
| Kullanıcı kayıt/giriş | Tamam | `/kullanici/kayit/`, `/hesap/login/` |
| Şifre sıfırlama | Tamam | `/hesap/password_reset/`, SMTP ayarları `.env.example` |
| Roller ve yetki | Tamam | Admin/staff ve standart kullanıcı, `UserProfile` |
| Model/veritabani | Tamam | `Complaint`, `UserProfile`, SQLite/migration |
| CRUD | Tamam | Şikayet ekle, detay, düzenle, sil |
| Form validation | Tamam | Zorunlu alanlar, kategori secimi, enlem/boylam siniri |
| Mobil API | Tamam | Token auth, `/api/mobile/register/`, `/api/mobile/login/`, `/api/mobile/complaints/` |
| Yetkili panel | Tamam | `/panel/`, sadece staff |
| Grafik | Tamam | Panelde pasta ve sutun grafik |
| Detaylı rapor | Tamam | `/rapor/` |
| Rapor filtreleme | Tamam | Tarih, kategori, durum |
| Yazdır/PDF | Tamam | Rapor ekranındaki `Yazdır / PDF` butonu |
| Responsive arayuz | Tamam | CSS media query ve mobil form/harita |
| Git/GitHub | Tamam | `https://github.com/akifberk/kentradar.git` |
| Hosting/domain | Beklemede | Render/PythonAnywhere uzerinden yayina alinmali |

## Sunumda Gosterilecek Akis

1. Standart kullanıcı kaydı oluştur.
2. Giriş yapıp `/bildir/` ekranından şikayet ekle.
3. Haritada renkli şikayet baloncuğunu göster.
4. Admin/staff hesabi ile `/panel/` ekranina gir.
5. Grafik ve son şikayetleri göster.
6. `/rapor/` ekraninda tarih veya kategori filtresi uygula.
7. `Yazdır / PDF` butonuyla raporu PDF'e kaydet.

## Flutter Icin API Notlari

Login/register cevabinda gelen token saklanir ve sonraki isteklerde su header ile gonderilir:

```text
Authorization: Token TOKEN_DEGERI
```

Ana endpointler:

- `POST /api/mobile/register/`
- `POST /api/mobile/login/`
- `POST /api/mobile/logout/`
- `POST /api/mobile/password-reset/`
- `GET,POST /api/mobile/complaints/`
- `GET,PATCH,DELETE /api/mobile/complaints/<id>/`
- `GET /api/mobile/panel/`
- `GET /api/mobile/report/`

Flutter rubriği için önerilen klasör yapısı:

```text
lib/
  models/
  views/
  controllers/
  services/
  widgets/
```
