from where_c import build_time_where_clauses

# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
#neden bazı parametreler none?
#çünkü kullanıcı örneğin her zaman bir parametre belirtmez kaç müşteri var der zaman belli değildir
def generate_sql(intent: str, table: str, year=None, specific_date=None, interval_months=None, relative_time=None, distinct: bool=False, customer_name=None, limit=10, order_dir=None, selected_columns=None) -> str | None:
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
    
    # TARİH KOLONUNU BELİRLEMEK
    # Hem sıralama (ORDER BY) için hem de Filtreleme (WHERE) için gerekli.
    # Eğer bunu yapmazsak "created_at" hangi tabloda diye hata verir.
    target_date_col = "created_at"
    
    if table == "orders" or table == "order_items":
        target_date_col = "orders.created_at"
    elif table == "customers":
        target_date_col = "customers.created_at"


    # !!!! EN BAŞA BURAYA ALDIM KOD TEKRARI VE HATASI OLMASIN DİYE
    where_clauses = build_time_where_clauses(
        year=year,
        specific_date=specific_date,
        interval_months=interval_months,
        relative_time=relative_time,
        customer_name=customer_name
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
        
        #SELECT : Kolon seçimi 
        if selected_columns:
            cols = ", ".join(selected_columns) # ['name', 'email'] -> "name, email"
            sql = f"SELECT {cols} FROM {table}"
        else:
            sql = f"SELECT * FROM {table}" 

        # JOIN
        if customer_name and table == "orders":
            sql += " JOIN customers ON orders.customer_id = customers.id"

        # SIRALAMA (ORDER BY)
        if order_dir:
            sort_col = target_date_col  #Varsayılan olarak belirlenen tarih kolonuna göre sırala
            
            if table == "products": # İstisna: Ürünlerde tarih yoksa fiyata göre sırala
                sort_col = "price" 
            
            sql += f" ORDER BY {sort_col} {order_dir}"
            
        elif table == "orders": 
             sql += f" ORDER BY {target_date_col} DESC" # Kullanıcı bir şey demese bile siparişleri tarihe göre (YENİDEN ESKİYE) sırala

        # LİMİT
        sql += f" LIMIT {limit};"
        return sql
    
    if intent == "sum":
        sql = ""

        #sipariş tutarı (ciro)
        if table == "orders":
            sql = "SELECT COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders"

            # Eğer isim varsa CUSTOMERS tablosuna bağlan!
            if customer_name:
                sql += " JOIN customers ON orders.customer_id = customers.id"

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

