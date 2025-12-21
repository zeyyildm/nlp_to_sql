from where_c import build_time_where_clauses

# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
#neden bazı parametreler none?
#çünkü kullanıcı örneğin her zaman bir parametre belirtmez kaç müşteri var der zaman belli değildir
def generate_sql(intent: str, table: str, year=None, specific_date=None, interval_months=None, relative_time=None, distinct: bool=False, customer_name=None, limit=10, order_dir=None, selected_columns=None, condition=None) -> str | None:
    """
    Parametreler:
    - intent: count, list vb.
    - table: orders, customers vb.
    - year: Sadece yıl bilgisi (Örn: 2022)
    - specific_date: (Ay, Yıl) formatında tuple (Örn: (3, 2022))
    - interval_months: Son kaç ay olduğu (Örn: 3)
    - relative_time: 'this_month' veya 'last_month'
    """
    if not table: #tablo yoksa sonuç dönme. güvenli şekilde sql üretmiyorum demek
        return None
    
    # TARİH KOLONUNU BELİRLEMEK
    # Hem sıralama (ORDER BY) için hem de Filtreleme (WHERE) için gerekli.
    # Eğer bunu yapmazsak "created_at" hangi tabloda diye hata verir.
    target_date_col = "created_at"
    has_date_column = True  # Tabloda created_at var mı?
    
    if table == "orders":
        target_date_col = "orders.created_at"
    elif table == "order_items":
        target_date_col = "orders.created_at"  # order_items'da tarih yok, orders'dan alınacak
    elif table == "customers":
        target_date_col = "customers.created_at"
    elif table == "products":
        target_date_col = "products.created_at"

    # !!!! EN BAŞA BURAYA ALDIM KOD TEKRARI VE HATASI OLMASIN DİYE
    # Eğer tarih kolonu yoksa ve zaman filtresi varsa, hata döndür
    if not has_date_column and (year or specific_date or interval_months or relative_time):
        return None  # Products tablosunda tarih filtresi kullanılamaz
    
    where_clauses = build_time_where_clauses(
        year=year,
        specific_date=specific_date,
        interval_months=interval_months,
        relative_time=relative_time,
        customer_name=customer_name,
        date_column=target_date_col
    )

    # KOŞUL -> 1000 tl ve üzeri gibi ifadeler için (">", 1000) gelir
    # operator = ">"
    #value = 1000
    if condition and condition[0] and condition[1]:
        operator, value = condition
        filter_col = ""  #bu value hangi sütunla karşılaştırılacak
        if table == "orders":
            filter_col = "orders.total_amount"
        elif table == "products":
            filter_col = "price"
        elif table == "order_items":
            filter_col = "quantity"
            
        if filter_col: #gerçekten bir kolon seçilmiş mi diye bakar
            where_clauses.append(f"{filter_col} {operator} {value}") #bunu da gider where clause olarak ekler

    #COUNT

    distinct_col_map = {
    "orders": "customer_id",
    "order_items": "product_id",
    "customers": "id",
    "products": "id"
    }
    if intent == "count":
        # JOIN gerekip gerekmediğini belirle
        # order_items için zaman filtresi varsa veya distinct kullanılıyorsa JOIN gerekir
        need_join = False
        
        if table == "order_items":
            # Zaman filtresi varsa veya distinct kullanılıyorsa JOIN gerekir
            if where_clauses or distinct:
                need_join = True
        
        # COUNT sorgusu oluştur
        if distinct:
            col = distinct_col_map.get(table)
            if not col:
                return None
            # JOIN varsa kolon adını tablo prefix'i ile belirt
            if need_join and table == "order_items":
                sql = f"SELECT COUNT(DISTINCT order_items.{col}) AS count FROM {table}"
            else:
                sql = f"SELECT COUNT(DISTINCT {col}) AS count FROM {table}"
        else:
            sql = f"SELECT COUNT(*) AS count FROM {table}"

        # JOIN ekle (WHERE'den önce)
        if need_join and table == "order_items":
            sql += " JOIN orders ON order_items.order_id = orders.id"

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
        need_join = False
        
            # A) Eğer isim filtresi varsa (Örn: Beyzanın siparişleri) -> JOIN lazım
        if customer_name:
            need_join = True
            
            # B) Eğer seçilen kolonlar 'müşteri bilgisi' içeriyorsa -> JOIN lazım
        if selected_columns:
            if "name" in selected_columns or "email" in selected_columns:
                need_join = True
        
            # Karar verildiyse JOIN ekle
        if table == "orders" and need_join:
            sql += " JOIN customers ON orders.customer_id = customers.id"

        #WHERE
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

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

