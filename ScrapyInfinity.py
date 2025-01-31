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
    "https://www.motorobit.com/motorlar",
    "https://www.motorobit.com/motor-surucu-kartlari",
    "https://www.motorobit.com/komponentler",
    "https://www.motorobit.com/arduino",
    "https://www.motorobit.com/raspberry-pi-6471",
    "https://www.motorobit.com/drone-ve-multikopter",
    "https://www.motorobit.com/voltaj-regulator-kartlari",
    "https://www.motorobit.com/role-kartlari",
    "https://www.motorobit.com/sensorler",
    "https://www.motorobit.com/kablosuz-haberlesme",
    "https://www.motorobit.com/elektronik-kartlar",
    "https://www.motorobit.com/ekranlar",
    "http://motorobit.com/butonlar-ve-switchler",
    "https://www.motorobit.com/kablolar-ve-donusturuculer",
    "https://www.motorobit.com/otomasyon-malzemeleri",
    "https://www.motorobit.com/guc-kaynaklari",
    "https://www.motorobit.com/li-po-piller",
    "https://www.motorobit.com/pil-aku-gunes-panelleri",
    "https://www.motorobit.com/olcu-ve-test-aletleri",
    "https://www.motorobit.com/hoparlor-ve-buzzer",
    "https://www.motorobit.com/havya-ve-ekipmanlar",
    "https://www.motorobit.com/robot-kitleri",
    "https://www.motorobit.com/egitim-kitleri",
    "https://www.motorobit.com/3d-yazici-ve-filament",
    "https://www.motorobit.com/plaket-ve-breadboard",
    "https://www.motorobit.com/el-aletleri-ve-hirdavat",
    "https://www.motorobit.com/mekanik-parcalar",
    "https://www.motorobit.com/tekerlekler",
    "https://www.motorobit.com/outlet"
]

# Çekilen verileri saklamak için liste
data = []

# 📌 Sayfa kaydırmayı optimize eden fonksiyon
def scroll_page(driver):
    scroll_pause_time = 1
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
    time.sleep(2)  # Sayfanın yüklenmesini bekle

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
        
        # Ürün URL'si
        product_url = product.select_one("a")["href"]
        product_url = "https://www.motorobit.com" + product_url
        product_urls.append((name, product_url, category_url))

    # 🚀 Çoklu işlem ile ürün detaylarını çek
    def fetch_product_details(product_info):
        name, product_url, category_url = product_info
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(product_url, headers=headers)
        product_soup = BeautifulSoup(response.text, "html.parser")

        # 📌 Stok bilgisi
        stock = product_soup.select_one(".stock-general").get_text(strip=True) if product_soup.select_one(".stock-general") else "Stok bilgisi yok"

        # 📌 Fiyat bilgisi (ÜRÜN SAYFASINDAN ALINIYOR)
        price = product_soup.select_one(".product-price").get_text(strip=True) if product_soup.select_one(".product-price") else "Fiyat bilgisi yok"
        
       
        # 📌 Kategori ismi
        category_name = category_url.split("/")[-1]
        
        return {
            "Kategori": category_name,
            "Ürün Adı": name,
            "Fiyat": price,
            "URL": product_url,
            "Stok": stock
            
        }
    
    # 🚀 Paralel işlem (5 ürün aynı anda çekilir)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_product_details, product_urls))
        data.extend(results)

# Tarayıcıyı kapat
driver.quit()

# Verileri Excel'e kaydet
df = pd.DataFrame(data)
df.to_excel("motorobit_tum_urunler.xlsx", index=False)
print("Veriler Excel dosyasına kaydedildi.")
