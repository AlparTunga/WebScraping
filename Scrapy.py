import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
# Kategorilerin URL'leri
categories = [
    "https://fapatech.com/kategori/birlestiriciler/",
    "https://fapatech.com/kategori/egitim-kitleri/",
    "https://fapatech.com/kategori/el-aletleri/",
    "https://fapatech.com/kategori/elektronik/",
    "https://fapatech.com/kategori/enerji/",
    "https://fapatech.com/kategori/fapatech/",
    "https://fapatech.com/kategori/hareket/",
    "https://fapatech.com/kategori/kablolama/",
    "https://fapatech.com/kategori/kompanentler/",
    "https://fapatech.com/kategori/mekanik/"
    
    # Diğer kategori URL'lerini buraya ekleyebilirsiniz
]

# Çekilen verileri saklamak için bir liste
data = []

# Her bir kategori için döngü
for category_url in categories:
    page = 1  # İlk sayfadan başla
    
    while True:
        
        url = f"{category_url}page/{page}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Ürün bilgilerini çekmek için uygun HTML elemanlarını seçin
         
            products = soup.select(".product")  # Ürünler için doğru sınıf
         

            # Eğer bu sayfada ürün yoksa döngüyü bitir
            if not products:
                print(f"{url} Sayfa {page} boş. Çekme işlemi sona erdi.")
                break
            
            for product in products:
                # Ürün adı
                name = product.select_one(".name").get_text(strip=True)
                
                # Ürün fiyatı
                price = product.select_one(".price").get_text(strip=True) if product.select_one(".price") else "Fiyat bilgisi yok"
                
                # Ürün URL'si
                product_url = product.select_one("a")["href"]
                #product_url = "https://robolinkmarket.com" + product_url
                
                # Ürün detaylarına gitmek için URL'yi ziyaret et
                product_response = requests.get(product_url)
                if product_response.status_code == 200:
                    product_soup = BeautifulSoup(product_response.content, "html.parser")
                    
                    # Stok bilgisi
                    stock = product_soup.select_one(".stock").get_text(strip=True) if product_soup.select_one(".stock") else "Stok bilgisi yok"
                    
                    # Açıklama
                    #category_name = product_soup.select_one(".woocommerce-product-details__short-description").get_text(strip=True) if product_soup.select_one(".woocommerce-product-details__short-description") else "Açıklama yok"
                else:
                    stock = "Stok bilgisi alınamadı"
                    description = "Detaylara ulaşılamadı"
                
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
            
            print(f"{url} Sayfa {page} tamamlandı.")
            page += 1  # Bir sonraki sayfaya geç
        else:
            print(f"{url} Sayfa {page} yüklenemedi. Durum kodu: {response.status_code}")
            break

# Verileri bir Excel dosyasına kaydet
df = pd.DataFrame(data)
df.to_excel("fapatech_tum_urunler.xlsx", index=False)
print("Veriler Excel dosyasına kaydedildi.")
