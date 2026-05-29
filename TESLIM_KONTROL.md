# KentRadar Teslim Kontrolu

## Rubrik Maddeleri

| Madde | Durum | Projede Karsiligi |
| --- | --- | --- |
| Kullanici kayit/giris | Tamam | `/kullanici/kayit/`, `/hesap/login/` |
| Sifre sifirlama | Tamam | `/hesap/password_reset/`, SMTP ayarlari `.env.example` |
| Roller ve yetki | Tamam | Admin/staff ve standart kullanici, `UserProfile` |
| Model/veritabani | Tamam | `Complaint`, `UserProfile`, SQLite/migration |
| CRUD | Tamam | Sikayet ekle, detay, duzenle, sil |
| Form validation | Tamam | Zorunlu alanlar, kategori secimi, enlem/boylam siniri |
| Mobil API | Tamam | Token auth, `/api/mobile/register/`, `/api/mobile/login/`, `/api/mobile/complaints/` |
| Yetkili panel | Tamam | `/panel/`, sadece staff |
| Grafik | Tamam | Panelde pasta ve sutun grafik |
| Detayli rapor | Tamam | `/rapor/` |
| Rapor filtreleme | Tamam | Tarih, kategori, durum |
| Yazdir/PDF | Tamam | Rapor ekranindaki `Yazdir / PDF` butonu |
| Responsive arayuz | Tamam | CSS media query ve mobil form/harita |
| Git/GitHub | Tamam | `https://github.com/akifberk/kentradar.git` |
| Hosting/domain | Beklemede | Render/PythonAnywhere uzerinden yayina alinmali |

## Sunumda Gosterilecek Akis

1. Standart kullanici kaydi olustur.
2. Giris yapip `/bildir/` ekranindan sikayet ekle.
3. Haritada renkli sikayet baloncugunu goster.
4. Admin/staff hesabi ile `/panel/` ekranina gir.
5. Grafik ve son sikayetleri goster.
6. `/rapor/` ekraninda tarih veya kategori filtresi uygula.
7. `Yazdir / PDF` butonuyla raporu PDF'e kaydet.

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

Flutter rubrigi icin onerilen klasor yapisi:

```text
lib/
  models/
  views/
  controllers/
  services/
  widgets/
```
