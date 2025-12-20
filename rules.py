import re #regex için

def normalize(text: str) -> str: #test kullanıcıdan gelen str temizlenmiş hali
    text = text.strip().lower() #metnin başındaki ve sonundaki boşlukları siler
    tr_map = str.maketrans("çğıöşü", "cgiosu") #pcnin eşleşme yapabilmesi için içsel bir çevirme
    text = text.translate(tr_map)  # türkçe -> ingilizce dönüşümü yapar
    text = re.sub(r"[^a-z0-9\s]", " ", text) #harf rakam ve boşluk dışındakileri temizle
    text = re.sub(r"\s+", " ", text).strip() #bir veya daha fazla boşluk varsa bunları tek boşluğa indir
    return text #artık temizlenmiş text döner

#SÖZLÜKLER

ENTITY_KEYWORDS = { #TEXT HANGI TABLOYU SORUYOR
    "customers": {"müşteri", "kullanıcı", "üye", "kayıt", "insan", "musteri", "kullanici", "uye", "kayit"},
    "orders": {"sipariş", "satış", "işlem", "siparis", "satis", "islem", "harcama", "ciro", "tutar", "gelir"},
    "products": {"ürün", "item", "mal", "esya", "eşya", "fiyat"},
    "order_items": {"adet", "miktar", "kalem", "ürün adeti", "ürünadeti", "urun adeti", "urun adetı", "urun adetı",
                    "satılan", "satilan", "satış adedi", "satis adedi"},
}

INTENT_KEYWORDS = { #sözlükle beraber niyet eşleştirmesi yapacağız
    "count": {"kaç", "kaçtane", "sayısı", "adet", "kaç adet", "kac", "kactane", "kacadet", "sayisi", "kac adet"},
    "sum": {"toplam", "ciro", "ne kadar"},
    "list": {"listele", "göster", "getir", "hangi", "goster"},
    "top": {"en çok", "en fazla", "ilk", "en cok", "encok", "ençok", "enfazla"},
    "max": {"en yüksek", "enyuksek", "enyüksek", "en yuksek", "en çok", "encok", "ençok", "en cok", "en fazla", "enfazla", "max", "max.", "maximum"},
    "min": {"en az", "en düşük", "minimum", "min.", "min", "enaz", "endusuk", "endüşük"},
    "avg": {"ortalama", "ort", "ort."},
    
}

TIME_KEYWORDS = {
    "today": {"bugün"},
    "this_month": {"bu ay"},
    "last_month": {"geçen ay", "gecen ay"},
    "this_year": {"bu yıl", "bu yil"},
}

MONTH_MAP = { 
    "ocak": 1, "subat": 2, "mart": 3, "nisan": 4, "mayis": 5, "haziran": 6,
    "temmuz": 7, "agustos": 8, "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12
}

DISTINCT_KEYWORDS = {"farkli", "benzersiz", "farklı", "benzersız"}

COLUMN_MAPPING = { #kullanıcının dediği kelime -> veritabanındaki sütun adı
    "ad": "name",
    "isim": "name",
    "soyad": "name", 
    "adsoyad": "name",
    "mail": "email",
    "eposta": "email",
    "fiyat": "price",
    "tutar": "total_amount",
    "miktar": "quantity",
    "adet": "quantity",
    "tarih": "created_at",
    "zaman": "created_at"
}

def extract_columns(text: str):
    selected_cols = []
    words = text.split()
    for word in words:
        for key, col_name in COLUMN_MAPPING.items(): #kelimenin kökü sözlükte var mı kontrol eder
            if key in word:
                if col_name not in selected_cols: #aynı kolonu iki kere ekleme
                    selected_cols.append(col_name)
    return selected_cols if selected_cols else None

def detect_distinct(text: str) -> bool:
    return any(k in text for k in DISTINCT_KEYWORDS)

def find_intent(text: str) -> str:
    if any(k in text for k in INTENT_KEYWORDS["top"]):
        return "top"
    if any(k in text for k in INTENT_KEYWORDS["sum"]):
        return "sum"
    if any(k in text for k in INTENT_KEYWORDS["count"]):
        return "count"
    if any(k in text for k in INTENT_KEYWORDS["list"]):
        return "list"
    return "unknown"

#iflerin yapısı gereği bir önem sırası oldu sonradan bunu düzenleyebiliriz
    
def find_entity(text: str) -> str | None:  #girdi normalize edilmiş cümle, çıktı tablo adı veya none
    for table, keywords in ENTITY_KEYWORDS.items(): #sözlükteki her tabloya bakar
        if any(k in text for k in keywords): #o tabloya ait her kelimeyi cümlede arar
            return table #en az biri geçiyorsa okey
    return None 

#zamanla ilgili her şey bu modül sayfasında yer almalıdır
def extract_year(text: str):  #yıl yakalama regexi, metin içindeki 4 haneli yılı bulur
    match = re.search(r'\b(19|20)\d{2}\b', text) #\b sayı başka bir şeyin parçası olmasın
    if match:
        return int(match.group(0)) #REGEXIN TAMAMEN YAKALADIĞI ŞEY
    return None


def extract_month_year(text: str): #2022 Mart gibi ifadeleri yakalar. 
    year = extract_year(text) #yılı bulur
    found_month = None #ayı bulur
    for month_name, month_num in MONTH_MAP.items():
        if month_name in text: 
            found_month = month_num
            break
    
    if found_month and year:  # Eğer hem ay hem yıl bulunduysa döndür
        return found_month, year
    
    return None

def extract_interval(text: str): #son 3 ay gibi ifadeleri yakalar sadece sayıyıy döndürür
    match = re.search(r'son (\d+) ay', text)
    if match:
        return int(match.group(1)) #SADECE 3 Ü ALMAK İSTEDİĞİMİZ İÇİN 1
    return None

def detect_time_filter(text: str): #bu ay ve geçen ay ifadelerini yakalar
    for time_key, keywords in TIME_KEYWORDS.items():
        if any(k in text for k in keywords):
            return time_key
    return None

#cümlede sipariş vermekle ilgili bir bağlam var mı bakar -> Örn: 'sipariş veren', 'sipariş verdi', 'alışveriş yapan'
def detect_order_context(text: str) -> bool:
    keywords = {"sipariş", "siparis", "alısveris", "alisveris", "satin", "satın", "verdi", "alan"}
    return any(word in text for word in keywords)

#isimlerdeki nın nin siler ismi çeker
def extract_customer_name(text: str):
    words = text.split()
    for word in words:
        # 3 harfli ekler (nin, nın, nun, nün)
        if len(word) > 3 and (word.endswith("nin") or word.endswith("nin") or word.endswith("nun") or word.endswith("nun")):
             return word[:-3] 
        
        # 2 harfli ekler (in, in, un, un)
        if len(word) > 2 and (word.endswith("in") or word.endswith("in") or word.endswith("un") or word.endswith("un")):
             return word[:-2]
             
    return None


def extract_limit_and_order(text: str): #limit sayısını ve sıralama yönünü bulur
    limit = 10 # Varsayılan limitimiz
    order = None

    # limit sayısını bulma, Regex: "ilk 5", "son 10", "5 tane", "5 adet"
    match = re.search(r'\b(\d+)\s*(?:tane|adet|sipariş|kayıt|müşteri|ürün)?\b', text)
    
    #eğer sayı bulduysak ve bu sayı yıl değilse 
    if match:
        num = int(match.group(1))
        if num < 1000: 
            limit = num

    if "son" in text or "yeni" in text: #sıralama yönünü bulma: azalan yani en yeniden eskiye
        order = "DESC"

    elif "ilk" in text or "eski" in text: #ilk beş derken genelde en üstteki 5 kastedilir
        if "eski" in text: #ama eski ASCdir
            order = "ASC"
    return limit, order

