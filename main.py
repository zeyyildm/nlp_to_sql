from rules import extract_year, extract_month_year, extract_interval, detect_time_filter, detect_distinct #zaman bilgileri için
from rules import normalize, find_intent, find_entity, detect_order_context, extract_customer_name
from sql_generator import generate_sql
from db import run_query

while True: #program sürekli devam etsin

    text = input("\nSoru gir (çıkmak için q): ")

    if text.lower() == "q": #q yazınca program durur
        break

    normalized = normalize(text)
    distinct_flag = detect_distinct(normalized)
    intent = find_intent(normalized)
    entity = find_entity(normalized)
    if intent == "unknown" and entity is not None:
        intent = "list"

    distinct_flag = detect_distinct(normalized)
    is_order_context = detect_order_context(normalized) # Sipariş bağlamı var mı?
    # Eğer konu "müşteri" ise AMA "sipariş"ten bahsediliyorsa,
    # Aslında biz 'orders' tablosuna bakmalıyız ve 'distinct' saymalıyız.
    if entity == "customers" and is_order_context:
        entity = "orders"   # Tabloyu değiştir
        distinct_flag = True # Farklı müşterileri sayması için bayrağı kaldır
    
    year_info = extract_year(normalized) #cümledeki yıl bulunur
    date_info = extract_month_year(normalized) #ay+yıl ikilisi bulunur
    interval_num = extract_interval(normalized) #cümledeki zaman aralığı, son 3 ay gibi bulur
    rel_time = detect_time_filter(normalized) #bu ay, geçen ay
    cust_name = extract_customer_name(normalized)

    print("Normalize edilmiş:", normalized)
    print("Tespit edilen intent:", intent)
    print("Tespit edilen tablo:", entity)
    print(f"Zaman Bilgileri -> Yıl: {year_info} | Özel Tarih: {date_info} | Aralık: {interval_num} | Göreceli: {rel_time}")
    print(f"Tespit Edilen İsim: {cust_name}")  

    sql = generate_sql(
        intent, 
        entity, 
        year=year_info,
        specific_date=date_info, 
        interval_months=interval_num,
        relative_time=rel_time,
        distinct=distinct_flag
        )

    if sql:
        print("Oluşturulan SQL:", sql)
        result = run_query(sql)
        print(result)
    else:
        print("Bu sorgu şu an desteklenmiyor.")


