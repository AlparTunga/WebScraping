from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from webdriver_manager.chrome import ChromeDriverManager

# 🚀 Tarayıcıyı hızlı çalıştırmak için Selenium ayarları
options = Options()
options.add_argument("--headless")  # Arka planda çalıştır (görünmez)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# WebDriver başlat
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Çekilecek kategori URL'leri
categories = [
    "https://www.robotistan.com/arduino",
    "https://www.robotistan.com/raspberry-pi-turkiye",
    "https://www.robotistan.com/3d",
    "https://www.robotistan.com/egitici-setler",
    "https://www.robotistan.com/cocuklar-icin-robotik-kodlama",
    "https://www.robotistan.com/gelistirme-kartlari-1",
    "https://www.robotistan.com/elektronik-kart-modul",
    "https://www.robotistan.com/motor",
    "https://www.robotistan.com/sensor",
    "https://www.robotistan.com/guc-kaynagi-batarya",
    "https://www.robotistan.com/prototipleme-lehim",
    "https://www.robotistan.com/kablosuz-haberlesme",
    "https://www.robotistan.com/elektronik-komponent",
    "https://www.robotistan.com/mekanik",
    "https://www.robotistan.com/teker",
    "https://www.robotistan.com/olcu-test",
    "https://www.robotistan.com/arac-gerec",
    "https://www.robotistan.com/drone",
    "https://www.robotistan.com/outlet",
    "https://www.robotistan.com/kitap"
    "https://www.robotistan.com/robot-yarismalari"
]

# Çekilen verileri saklamak için liste
data = []

# 📌 Sayfa kaydırmayı optimize eden fonksiyon
def scroll_page(driver):
    scroll_pause_time = 3
    screen_height = driver.execute_script("return window.innerHeight;")
    i = 1
    while True:
        driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
        time.sleep(scroll_pause_time)
        i += 1
        new_height = driver.execute_script("return document.body.scrollHeight")
        if screen_height * i >= new_height:
            break

# 🌍 Kategori içindeki tüm ürünleri çek
for category_url in categories:
    driver.get(category_url)
    time.sleep(3)  # Sayfanın yüklenmesini bekle

    # Sayfayı kaydırarak tüm ürünleri yükle
    scroll_page(driver)
    
    # Sayfa kaynağını çek
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Ürünleri seç
    products = soup.select(".product-item")
    
    if not products:
        print(f"{category_url} kategorisinde ürün bulunamadı.")
        continue

    product_urls = []
    for product in products:
        # Ürün adı
        name = product.select_one(".product-title").get_text(strip=True)
        
        # Ürün fiyatı
        price = product.select_one(".product-price").get_text(strip=True) if product.select_one(".product-price") else "Fiyat bilgisi yok"
        
        # Ürün URL'si
        relative_url = product.select_one("a")["href"]
        product_url = urljoin("https://www.robotistan.com", relative_url)  # ✅ URL'yi doğru birleştir
        
        print(f"Ürün URL: {product_url}")  # Debug için URL kontrolü
        
        product_urls.append((name, price, product_url, category_url))

    # 🚀 Çoklu işlem ile ürün detaylarını çek
    def fetch_product_details(product_info):
        name, price, product_url, category_url = product_info
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            time.sleep(1)  # Web sitesinin engellememesi için bekleme süresi
            response = requests.get(product_url, headers=headers, timeout=10)
            response.raise_for_status()  # HTTP hatalarını yakala
        except requests.exceptions.RequestException as e:
            print(f"Hata: {e}")
            return None

        # Kategori ismi
        category_name = category_url.split("/")[-1]

        return {
            "Kategori": category_name,
            "Ürün Adı": name,
            "Fiyat": price,
            "URL": product_url,
            "Stok": "Stok bilgisi yok"
        }
    
    # 🚀 Paralel işlem (5 ürün aynı anda çekilir)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_product_details, product_urls))
        data.extend(filter(None, results))  # Hata alan sonuçları filtrele

# Tarayıcıyı kapat
driver.quit()

# Verileri Excel'e kaydet
df = pd.DataFrame(data)
df.to_excel("robotistan_tum_urunler.xlsx", index=False)
print("Veriler Excel dosyasına kaydedildi.")
