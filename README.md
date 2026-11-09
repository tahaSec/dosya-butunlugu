# Dosya Bütünlüğü Denetleyicisi

Seçtiğin klasörün SHA-256 özetlerini kaydeder ve daha sonra yeni, silinmiş ya da değiştirilmiş dosyaları bulur. Dosya içeriklerini değiştirmez; manifest dosyasını senin belirttiğin konuma yazar.

## Gereksinimler

- Python 3.10 veya üzeri
- Harici paket gerekmez

## Kullanım

```bash
python integrity.py baseline ./izlenecek-klasor --output ./integrity-manifest.json
python integrity.py check ./izlenecek-klasor ./integrity-manifest.json
```

Manifesti izlenen klasörün dışında tutmak, kendi manifestinin yeni dosya gibi görünmesini önler. `.git`, sanal ortam klasörleri, `node_modules` ve sembolik bağlantılar kapsam dışıdır.

## Kapsam ve sınırlamalar

Bu araç değişikliği tespit etmeye yardımcı olur; dosyaları geri yüklemez ve manifesti korumalı bir yere kendiliğinden taşımaz. Manifest üzerinde oynanabiliyorsa sonuçlara tek başına güvenme.

## Yapay zekâ desteği

Bu proje, yapay zekâ desteğiyle geliştirildi ve düzenlendi.

## Lisans

MIT
