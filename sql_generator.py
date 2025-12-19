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
    
    # !!!! EN BAŞA BURAYA ALDIM KOD TEKRARI VE HATASI OLMASIN DİYE
    where_clauses = build_time_where_clauses(
        year=year,
        specific_date=specific_date,
        interval_months=interval_months,
        relative_time=relative_time
    )

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

        if where_clauses: #join bir listenin elemanları arasına bir şey koyar
            sql += " WHERE " + " AND ".join(where_clauses)
        #ÖR:
        #["A", "B", "C"]
        #" AND ".join(["A", "B", "C"])
        #"A AND B AND C"

        return sql + ";"
        

    if intent == "list":
        sql = f"SELECT * FROM {table}"
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " LIMIT 10;"
        return sql

    
    if intent == "sum":
        column = ""

        #sipariş tutarı (ciro)
        if table == "orders":
            sql = "SELECT COALESCE(SUM(total_amount), 0) AS total_sum FROM orders"

        #satılan ürün adedi
        elif table == "order_items":
            #tarih bilgisini 'orders' tablosundan almak için JOIN yapıyoruz
            sql = "SELECT COALESCE(SUM(order_items.quantity), 0) AS total_sum FROM order_items"
            sql += " JOIN orders ON order_items.order_id = orders.id"
            
        #ürün fiyatları (Örn: Depo değeri)
        elif table == "products":
            sql = "SELECT COALESCE(SUM(price), 0) AS total_sum FROM products"
            
        # Eğer yukarıdaki tablolardan biri değilse (Örn: Müşteriler) toplama yapılamaz
        else:
            return None

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        return sql + ";"

    return None

