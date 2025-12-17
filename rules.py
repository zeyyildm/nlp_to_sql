import re #regex için

def normalize(text: str) -> str: #test kullanıcıdan gelen str temizlenmiş hali
    text = text.strip().lower() #metnin başındaki ve sonundaki boşlukları siler
    tr_map = str.maketrans("çğıöşü", "cgiosu") #pcnin eşleşme yapabilmesi için içsel bir çevirme
    text = text.translate(tr_map)  # türkçe -> ingilizce dönüşümü yapar
    text = re.sub(r"[^a-z0-9\s]", " ", text) #harf rakam ve boşluk dışındakileri temizle
    text = re.sub(r"\s+", " ", text).strip() #bir veya daha fazla boşluk varsa bunları tek boşluğa indir
    return text #artık temizlenmiş text döner

#SÖZLÜKLER

ENTITY_KEYWORDS = {
    "customers": {"müşteri", "kullanıcı", "üye", "kayıt", "insan", "musteri", "kullanici", "uye", "kayit"},
    "orders": {"sipariş", "satış", "işlem", "siparis", "satis", "islem", "harcama"},
    "products": {"ürün", "item", "mal", "esya", "eşya"},
    "order_items": {"adet", "miktar", "kalem", "ürün adeti", "ürünadeti", "urun adeti", "urun adetı", "urun adetı"},
}

INTENT_KEYWORDS = { #sözlükle beraber niyet eşleştirmesi yapacağız
    "count": {"kaç", "kaçtane", "sayısı", "adet", "kaç adet", "kac", "kactane", "kacadet", "sayisi", "kac adet"},
    "sum": {"toplam", "ciro", "tutar", "ne kadar"},
    "list": {"listele", "göster", "getir", "hangi", "goster"},
    "top": {"en çok", "en fazla", "ilk", "top", "en cok", "encok", "ençok", "enfazla"},
    "max": {"en yüksek", "enyuksek", "enyüksek", "en yuksek", "en çok", "encok", "ençok", "en cok", "en fazla", "enfazla", "max", "max.", "maximum"},
    "min": {"en az", "en düşük", "minimum", "min.", "min", "enaz", "endusuk", "endüşük"},
    "avf": {"ortalama", "ort", "ort."},
    
}

TIME_KEYWORDS = {
    "today": {"bugün"},
    "this_month": {"bu ay"},
    "last_month": {"geçen ay", "gecen ay"},
    "this_year": {"bu yıl", "bu yil"},
}

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


def extract_year(text: str):  #yıl yakalama regexi
    match = re.search(r"(19|20)\d{2}", text)
    if match:
        return int(match.group())
    return None

