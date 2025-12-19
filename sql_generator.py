from where_c import build_time_where_clauses

# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
#neden bazı parametreler none?
#çünkü kullanıcı örneğin her zaman bir parametre belirtmez kaç müşteri var der zaman belli değildir
def generate_sql(intent: str, table: str, year=None, specific_date=None, interval_months=None, relative_time=None, distinct: bool=False) -> str | None:
    """
    Parametreler:
    - intent: count, list vb.
    - table: orders, customers vb.
    - year: Sadece yıl bilgisi (Örn: 2022)
    - specific_date: (Ay, Yıl) formatında tuple (Örn: (3, 2022))
    - interval_months: Son kaç ay olduğu (Örn: 3)
    - relative_time: 'this_month' veya 'last_month'
    """
    if not table: #tablo yoksa sonuç dönme
        return None
    

    if intent == "count":
        if distinct and table == "orders":
             # "Bu yıl kaç müşteri sipariş verdi?" -> Buraya düşecek
            sql = "SELECT COUNT(DISTINCT customer_id) AS count FROM orders"
            
        elif distinct and table == "order_items":
             # "Kaç farklı ürün satıldı?"
            sql = "SELECT COUNT(DISTINCT product_id) AS count FROM order_items"
            
        else:
            # "Bu yıl kaç müşteri kayıt oldu?" -> Buraya düşecek (Table=customers kalacak)
            # "Bu yıl kaç sipariş var?" -> Buraya düşecek
            sql = f"SELECT COUNT(*) AS count FROM {table}"

        where_clauses = build_time_where_clauses(
            year=year,
            specific_date=specific_date,
            interval_months=interval_months,
            relative_time=relative_time
)

        if where_clauses: #join bir listenin elemanları arasına bir şey koyar
            sql += " WHERE " + " AND ".join(where_clauses)
        #ÖR:
        #["A", "B", "C"]
        #" AND ".join(["A", "B", "C"])
        #"A AND B AND C"

        return sql + ";"
        

    if intent == "list":
        sql = f"SELECT * FROM {table}"

        where_clauses = build_time_where_clauses(
            year=year,
            specific_date=specific_date,
            interval_months=interval_months,
            relative_time=relative_time
    )

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

        sql += " LIMIT 10;"
        return sql

    
    if intent == "sum":
        if table != "orders":
            return None
        
        #SUM(total_count) -> o kolondaki tüm değerleri toplar
        #!!!!!!!!!COALESCE -> EĞER SAYI NULL İSE YERİNE ŞUNU KOY
        #DİYELIM KI 2030 YILINDAN HİÇ SİPARİŞ YOK SONUÇ 0 VEYA NONE DÖNMEZ NULL DÖNER NULL KÖTÜ ÇIKTI
        sql = "SELECT COALESCE(SUM(total_amount), 0) AS total_amount FROM orders" #eğer null ise git onun yerine 0 koy

        where_clauses = build_time_where_clauses(
            year=year,
            specific_date=specific_date,
            interval_months=interval_months,
            relative_time=relative_time
    )

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        return sql + ";"

    return None

