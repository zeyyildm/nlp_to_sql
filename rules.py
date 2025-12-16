import re #regex için

def normalize(text: str) -> str: #test kullanıcıdan gelen str temizlenmiş hali
    text = text.strip().lower() #metnin başındaki ve sonundaki boşlukları siler
    text = re.sub(r"[^a-z0-9çğıöşü\s]", " ", text) #harf rakam ya da boşluk olmayan her şeyi bul ve bunları boşlukla değiştir
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
    if any(k in text for k in INTENT_KEYWORDS["top"]):
        return "list"
    return "unknown"

#iflerin yapısı gereği bir önem sırası oldu sonradan bunu düzenleyebiliriz
    
    