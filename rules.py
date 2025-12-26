import re #regex için

def normalize(text: str) -> str: #test kullanıcıdan gelen str temizlenmiş hali
    text = text.strip().lower() #metnin başındaki ve sonundaki boşlukları siler
    tr_map = str.maketrans("çğıöşü", "cgiosu") #pcnin eşleşme yapabilmesi için içsel bir çevirme
    text = text.translate(tr_map)  # türkçe -> ingilizce dönüşümü yapar
    text = re.sub(r"[^a-z0-9\s]", " ", text) #harf rakam ve boşluk dışındakileri temizle
    text = re.sub(r"\s+", " ", text).strip() #bir veya daha fazla boşluk varsa bunları tek boşluğa indir
    return text #artık temizlenmiş text döner

#SÖZLÜKLER

GROUP_KEYWORDS = {"göre", "gore", "bazında", "bazinda", "dağılımı", "dagilimi"}

ENTITY_KEYWORDS = { #TEXT HANGI TABLOYU SORUYOR
    "customers": {"müşteri", "kullanıcı", "üye", "kayıt", "insan", "musteri", "kullanici", "uye", "kayit"},
    "orders": {"sipariş", "satış", "işlem", "siparis", "satis", "islem", "harcama", "ciro", "tutar", "gelir"},
    "products": {"ürün", "urun", "item", "mal", "esya", "eşya", "esya", "fiyat", "eklendi"},
    "order_items": {"adet", "miktar", "kalem", "ürün adeti", "ürünadeti", "urun adeti", "urun adetı", "urun adetı",
                    "satılan", "satilan", "satildi", "satıldı", "satış adedi", "satis adedi", "urun satildi", "ürün satıldı"},
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
    "email":"email",
    "fiyat": "price",
    "tutar": "total_amount",
    "miktar": "quantity",
    "adet": "quantity",
    "tarih": "created_at",
    "zaman": "created_at",
    "ürün": "products.name", "urun": "products.name"
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
    # SIRALAMA ÇOK ÖNEMLİ: Önce spesifik olanlar (Max/Min), sonra genel olanlar (Sum/List)
    if any(k in text for k in INTENT_KEYWORDS["max"]): return "max"
    if any(k in text for k in INTENT_KEYWORDS["min"]): return "min"
    if any(k in text for k in INTENT_KEYWORDS["top"]): return "list" # İlk 5 gibi sorgular listelemedir
    
    if any(k in text for k in INTENT_KEYWORDS["sum"]): return "sum"
    if any(k in text for k in INTENT_KEYWORDS["count"]): return "count"
    if any(k in text for k in INTENT_KEYWORDS["list"]): return "list"
    
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
#cümlede müşteri geçiyor ama bu cümle sipariş ile mi ilgili
def detect_order_context(text: str) -> bool:
    # müşteri sorusunu orders'a kaydıracak güçlü ifadeler
    strong_phrases = [
        "siparis verdi", "siparis veren", "siparis yapan",
        "en az 1 siparis", "en az bir siparis",
        "alisveris yapan", "alisveris etti", "satin aldi", "satin alan"
    ]
    return any(p in text for p in strong_phrases)

#isimlerdeki nın nin siler ismi çeker
def extract_customer_name(text: str):
    words = text.split()
    for word in words:
        # 3 harfli ekler (nin, nın, nun, nün)
        if len(word) > 3 and (word.endswith("nin") or word.endswith("nın") or word.endswith("nun") or word.endswith("nün")):
             return word[:-3] 
        
        # 2 harfli ekler (in, in, un, un)
        if len(word) > 2 and (word.endswith("in") or word.endswith("ın") or word.endswith("un") or word.endswith("ün")):
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

    # Sıralama yönü
    # ASC (Küçükten Büyüğe / Eskiden Yeniye)
    if any(k in text for k in ["ilk", "eski", "en az", "en dusuk", "en düşük", "ucuz", "en ucuz"]):
        order = "ASC"
    # DESC (Büyükten Küçüğe / Yeniden Eskiye)
    elif any(k in text for k in ["son", "yeni", "en cok", "en çok", "en fazla", "yuksek", "yüksek", "pahalı", "pahali"]):
        order = "DESC"
        
    return limit, order

def extract_numeric_condition(text: str):
    operator = None
    value = None

    # 1. BÜYÜKTÜR DURUMU 
    match_gt = re.search(r'(\d+)\s*(?:tl|lira|dolar|euro|birim|adet)?\s*(?:üzeri|uzeri|fazla|yuksek|büyük|buyuk|den cok|den çok|den fazla)', text)
    # (\d+) -> bir veya daha fazla rakam yakalar. parantez olduğundan group(1) ile yakalayıyoruz
    # \s* -> sayıdan sonra boşluk olabilir veya olmayabilir
    # (?:tl|...) -> opsiyonel olaral tl adet gibi birim. burası bir grup ama yaklama yok
    if match_gt:
        value = int(match_gt.group(1))
        operator = ">"
        return operator, value

    # 2. KÜÇÜKTÜR DURUMU 
    match_lt = re.search(r'(\d+)\s*(?:tl|lira|dolar|euro|birim|adet)?\s*(?:altı|alti|az|düşük|dusuk|den az|den kucuk|den küçük)', text)
    if match_lt:
        value = int(match_lt.group(1))
        operator = "<"
        return operator, value
        
    # 3. EŞİTTİR DURUMU (=)
    match_eq = re.search(r'(\d+)\s*(?:tl|lira|dolar|euro|birim|adet)?\s*(?:olan|esit|eşit)', text)
    if match_eq:
        value = int(match_eq.group(1))
        operator = "="
        return operator, value

    return None, None


#GROUP BY
def extract_grouping_request(text: str): #Kullanıcının gruplama isteyip istemediğini anlar.
    if not any(k in text for k in GROUP_KEYWORDS):
        return None, None

    if "aylara" in text or "aylik" in text or "ay bazinda" in text:
        return None, "month"
    if "yillara" in text or "yillik" in text or "yil bazinda" in text:
        return None, "year"

    if "musteri" in text or "kullanici" in text or "kisi" in text:
        return "name", None 
    if "urun" in text:
        return "name", None
            
    return None, None