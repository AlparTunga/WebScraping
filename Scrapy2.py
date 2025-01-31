import requests
from bs4 import BeautifulSoup
import pandas as pd

# Kategorilerin URL'leri
categories = [
  "https://www.sanec.net/tr/elektronik-imalat-urunleri",
  "https://www.sanec.net/tr/arduino-ve-elektronik-devre-elemanlari-1",
 "https://www.sanec.net/tr/3d-yazici-cnc",
  "https://www.sanec.net/tr/raspberry-pi-1"
  "https://www.sanec.net/tr/komponent",
  "https://www.sanec.net/tr/led-ve-aydinlatma",
  "https://www.sanec.net/tr/deri-hobi-el-aletleri",
  "https://www.sanec.net/tr/diger-urunler"
    #Diğer kategorileri buraya ekleyin
]

# Çekilen verileri saklamak için bir liste
data = []

# Her bir kategori için döngü
for category_url in categories:
    print(f"Kategori işleniyor: {category_url}")
    
    page = 1  # İlk sayfadan başla
     #izyet edilen sayfaları saklayan bir küme
    visited_pages = []
    
    while True:
        url = f"{category_url}/sayfa/{page}"
        

        response = requests.get(url) 
        if response.status_code != 200:
            print(f"{url} sayfasına erişilemedi. Durum kodu: {response.status_code}")
            break
        
             
        
        soup = BeautifulSoup(response.content, "html.parser")
        products = soup.select(".product-default")  # Ürünler için doğru HTML sınıfını seçin

        # Eğer sayfada ürün yoksa, kategori bitmiştir
        if not products:
            print(f"{url} sayfasında ürün bulunamadı. Kategori tamamlandı.")
            break

        for product in products:
            # Ürün URL'si
            product_url = product.select_one("a")["href"]
            #product_url = "https://www.robo90.com/" + product_url

            # Ürün adı
            name = product.select_one(".product-title").get_text(strip=True)

            # Ürün fiyatı
            product_response = requests.get(product_url)
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.content, "html.parser")
                price = product_soup.select_one(".kdvDahilPrice").get_text(strip=True) if product_soup.select_one(".kdvDahilPrice") else "Fiyat bilgisi yok"

            # Ürün detaylarına gitmek için URL'yi ziyaret et
            product_response = requests.get(product_url)
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.content, "html.parser")
                

                # Stok bilgisi
                # product_url = product.select_one("td")["margin-right: 10px;"]
                stock = product_soup.select_one(".margin-right").get_text(strip=True) if product_soup.select_one(".margin-right") else "Stok bilgisi yok"
            else:
                stock = "Stok bilgisi alınamadı"

            # Kategori bilgisi
            category_name = category_url.split("/")[4]  # URL'den kategori ismini çıkar

            # Verileri listeye ekle
            data.append({
                "Kategori": category_name,
                "Ürün Adı": name,
                "Fiyat": price,
                "Stok": stock,
                "URL": product_url
            })
          # Sayfa URL'sini ziyaret edilmiş olarak işaretle
        print(f"{url} Sayfa {page} tamamlandı.")
        visited_pages.append(url)
        page += 1  # Bir sonraki sayfaya geç
        url = f"{category_url}?pg={page}"
        
        response = requests.get(url)
        # Eğer aynı sayfa URL'si daha önce işlenmişse, kategori tamamlanmıştır
        if response.url == visited_pages[0]:
            print(f"{url} daha önce işlenmiş. Kategori tamamlandı.")
            break


# Verileri bir Excel dosyasına kaydet
df = pd.DataFrame(data)
df.to_excel("sanec_tum_urunler.xlsx", index=False)
print("Veriler Excel dosyasına kaydedildi.")
