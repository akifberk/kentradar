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
| Mobil API | Tamam | `/api/mobile/complaints/`, `X-API-Key` veya login |
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
