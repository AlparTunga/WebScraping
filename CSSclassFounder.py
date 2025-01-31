import requests
from bs4 import BeautifulSoup

# E-ticaret sitesinin URL'si
url =   "https://robolinkmarket.com/arduino"

# Web sitesine istek gönder
response = requests.get(url)
response.raise_for_status()  # Hata varsa durdur

# Sayfa içeriğini BeautifulSoup ile parse et
soup = BeautifulSoup(response.text, 'html.parser')

# Sayfadaki tüm HTML etiketlerinden class özniteliklerini bul
css_siniflari = set()  # Benzersiz sınıfları tutmak için set kullanıyoruz

# Tüm etiketleri döngüye al
for tag in soup.find_all(True):  # True, tüm etiketleri seçer
    if tag.has_attr('class'):
        for class_name in tag['class']:
            css_siniflari.add(class_name)

# Sonuçları yazdır
print("CSS Sınıfları:")
for sinif in sorted(css_siniflari):
    print(sinif)
