# URL Shortener API

Bu proje, uzun URL'leri kısaltmak ve yönetmek için geliştirilmiş bir Django REST API'sidir.

## Özellikler

- Kullanıcı hesap yönetimi
- API Key tabanlı kimlik doğrulama
- URL kısaltma ve yönlendirme
- Günlük URL kısaltma kotası (varsayılan: 50)
- URL kullanım istatistikleri

## Kurulum

1. Projeyi klonlayın:

```bash
git clone [repository-url]
cd shortenit
```

2. Sanal ortam oluşturun ve aktifleştirin:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını uygulayın:

```bash
python manage.py migrate
```

5. Süper kullanıcı oluşturun:

```bash
python manage.py createsuperuser
```

6. Sunucuyu başlatın:

```bash
python manage.py runserver
```

## API Endpoints

### Hesap İşlemleri

- `GET /api/accounts/` - Hesap bilgilerini görüntüle
- `POST /api/accounts/` - Yeni hesap oluştur

### URL İşlemleri

- `POST /api/urls/` - URL kısalt
- `GET /api/urls/` - Kısaltılmış URL'leri listele
- `GET /api/urls/{id}/` - Belirli bir URL'nin detaylarını görüntüle

### Analytics

- `GET /api/analytics/` - URL kullanım istatistiklerini görüntüle

### Yönlendirme

- `GET /{short_code}/` - Kısa URL'den orijinal URL'ye yönlendirme

## Kullanım

1. Admin panelinden (`/admin/`) bir hesap oluşturun
2. API Key'inizi alın
3. API isteklerinde Authentication header'ında API Key'inizi kullanın:

```
Authorization: Token your-api-key
```

## Kota Limitleri

- Her hesap için günlük URL kısaltma limiti: 50
- Limit aşıldığında API uygun bir hata mesajı döndürür

## Geliştirme

Projeye katkıda bulunmak için:

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun
