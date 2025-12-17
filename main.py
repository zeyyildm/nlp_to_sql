# from db import run_query #run queryi içeri alıyoruz

# sql = "SELECT * FROM customers LIMIT 5;"
# result = run_query(sql)

# print(result)

from rules import extract_year, extract_month_year, extract_interval, detect_month_filter #zaman bilgileri için
from rules import normalize, find_intent, find_entity
from sql_generator import generate_sql
from db import run_query

while True: #program sürekli devam etsin

    text = input("\nSoru gir (çıkmak için q): ")

    if text.lower() == "q": #q yazınca program durur
        break

    normalized = normalize(text)
    intent = find_intent(normalized)
    entity = find_entity(normalized)
    year_info = extract_year(normalized) #cümledeki yıl bulunur
    date_info = extract_month_year(normalized) #ay+yıl ikilisi bulunur
    interval_num = extract_interval(normalized) #cümledeki zaman aralığı, son 3 ay gibi bulur
    rel_time = detect_month_filter(normalized) #bu ay, geçen ay

    print("Normalize edilmiş:", normalized)
    print("Tespit edilen intent:", intent)
    print("Tespit edilen tablo:", entity)
    print(f"Zaman Bilgileri -> Yıl: {year_info} | Özel Tarih: {date_info} | Aralık: {interval_num} | Göreceli: {rel_time}")

    sql = generate_sql(
        intent, 
        entity, 
        year=year_info,
        specific_date=date_info, 
        interval_months=interval_num,
        relative_time=rel_time
        )

    if sql:
        print("Oluşturulan SQL:", sql)
        result = run_query(sql)
        print(result)
    else:
        print("Bu sorgu şu an desteklenmiyor.")


