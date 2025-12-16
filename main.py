# from db import run_query #run queryi içeri alıyoruz

# sql = "SELECT * FROM customers LIMIT 5;"
# result = run_query(sql)

# print(result)

from rules import normalize, find_intent

while True: #program sürekli devam etsin

    text = input("\nSoru gir (çıkmak için q): ")

    if text.lower() == "q": #q yazınca program durur
        break

    normalized = normalize(text)
    intent = find_intent(normalized)

    print("Normalize edilmiş:", normalized)
    print("Tespit edilen intent:", intent)