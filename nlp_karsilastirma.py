import stanza
import re

# 1. Stanza Türkçe Modelini İndir ve Yükle
print("Stanza Türkçe modeli yükleniyor... (İlk seferde indirme yapabilir)")
# processors='tokenize,lemma' -> Sadece kök bulma ve kelime ayırma modüllerini indirir (Hızlı olsun diye)
stanza.download('tr', processors='tokenize,lemma') 
nlp = stanza.Pipeline('tr', processors='tokenize,lemma', use_gpu=False)

# 2. Senin Mevcut Regex Fonksiyonun (Rules.py'daki mantık)
def my_custom_stemmer(word):
    word = word.lower()
    # Senin projedeki örnek kurallar (Basitleştirilmiş)
    word = re.sub(r'(l[ae]r)$', '', word) # -ler/-lar
    word = re.sub(r'(n?in|n?un)$', '', word) # -nin/-nun
    word = re.sub(r'([uü]n)$', '', word) # Senin meşhur "Ürün -> Ur" hatanı simüle ediyoruz
    return word

# 3. Karşılaştırma Fonksiyonu
def compare_methods(text):
    # Stanza ile analiz
    doc = nlp(text)
    
    print(f"\nAnaliz Edilen Cümle: '{text}'")
    print("-" * 75)
    print(f"{'Kelime':<20} | {'Senin Yöntem (Regex)':<25} | {'Stanza (Library)':<25}")
    print("-" * 75)
    
    # Stanza cümleleri ve kelimeleri döner
    for sentence in doc.sentences:
        for word in sentence.words:
            text_word = word.text
            
            # 1. Yöntem: Senin Regex sonucun
            regex_root = my_custom_stemmer(text_word)
            
            # 2. Yöntem: Stanza Kök Bulma (Lemma)
            stanza_root = word.lemma
            
            print(f"{text_word:<20} | {regex_root:<25} | {stanza_root:<25}")

# --- TEST SENARYOLARI ---
test_cumleleri = [
    "Müşterilerin siparişlerini listele",
    "Ürünleri fiyata göre sırala",  # Burada "Ürün" farkını göreceğiz
    "2025 yılında en çok satanlar",
    "Kitaplığımızdaki kitapları getir"
]

for cumle in test_cumleleri:
    compare_methods(cumle)