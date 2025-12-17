# from db import run_query #run queryi içeri alıyoruz

# sql = "SELECT * FROM customers LIMIT 5;"
# result = run_query(sql)

# print(result)

from rules import normalize, find_intent, find_entity, extract_year
from sql_generator import generate_sql
from db import run_query

while True: #program sürekli devam etsin

    text = input("\nSoru gir (çıkmak için q): ")

    if text.lower() == "q": #q yazınca program durur
        break

    normalized = normalize(text)
    intent = find_intent(normalized)
    entity = find_entity(normalized)

    print("Normalize edilmiş:", normalized)
    print("Tespit edilen intent:", intent)
    print("Tespit edilen tablo:", entity)

    sql = generate_sql(intent, entity, normalized)

    if sql:
        print("Oluşturulan SQL:", sql)
        result = run_query(sql)
        print(result)
    else:
        print("Bu sorgu şu an desteklenmiyor.")


