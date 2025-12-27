from where_c import build_time_where_clauses

# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
#neden bazı parametreler none?
#çünkü kullanıcı örneğin her zaman bir parametre belirtmez kaç müşteri var der zaman belli değildir
def generate_sql(intent: str, table: str, year=None, specific_date=None, interval_months=None, relative_time=None, distinct: bool=False, customer_name=None, limit=10, order_dir=None, selected_columns=None, condition=None, group_by_col=None, time_group=None, sort_context=None) -> str | None:
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
        # Ürünlerde 'created_at' olmayabilir, 'id' üzerinden işlem yapması daha güvenli.
        # Eğer veritabanında products tablosunda tarih yoksa has_date_column=False yapıyoruz.
        target_date_col = "id" # Varsayılan sıralama kolonu
        has_date_column = False # Tarih filtresi (bu yıl, geçen ay) uygulanmasın

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

    # KOŞUL -> 1000 tl ve üzeri gibi ifadeler için (">", 1000) gelir , operator = "> , value = 1000
    if condition and condition[0] and condition[1]:
        operator, value = condition
        filter_col = ""  #bu value hangi sütunla karşılaştırılacak
        if table == "orders":
            filter_col = "orders.total_amount"
        elif table == "products":
            filter_col = "price"
        elif table == "order_items":
            filter_col = "quantity"
            
        if filter_col:
             # ÖZEL DURUM: Eğer aggregate (sum) yapmıyorsak normal where ekle.
             # Eğer aggregate yapacaksak (1000 tl üzeri harcayanlar), bunu aşağıda HAVING'e sakla.
             if not (intent == "list" and table == "customers" and value > 50):
                where_clauses.append(f"{filter_col} {operator} {value}")

    # MAX & MIN 
    # Örnek: "En pahalı ürün", "En yüksek sipariş", "En düşük fiyat"
    # "En yüksek sipariş tutarı", "En ucuz ürün" sorguları buraya düşecek
    if intent == "max" or intent == "min":
        agg_func = "MAX" if intent == "max" else "MIN"
        target_col = ""
        
        if table == "products": target_col = "price"
        elif table == "orders": target_col = "total_amount"
        elif table == "order_items": target_col = "quantity"
        
        # Eğer uygun bir kolon yoksa (örn: müşteri max?) null dön
        if not target_col: return None

        sql = f"SELECT {agg_func}({target_col}) as sonuc FROM {table}"
        if where_clauses: sql += " WHERE " + " AND ".join(where_clauses)
        return sql + ";"


    #COUNT
    if intent == "count":
    
    # gruplama varsa buraya gir ve çık 
        if group_by_col or time_group:
            select_part = "COUNT(*)"
            group_clause = ""
            
            if time_group == "month":
                select_part = f"TO_CHAR({target_date_col}, 'YYYY-MM') as donem, COUNT(*)"
                group_clause = " GROUP BY donem ORDER BY donem"
            elif group_by_col == "name":
                select_part = "customers.name, COUNT(*)"
                group_clause = " GROUP BY customers.name ORDER BY 2 DESC"

            sql = f"SELECT {select_part} AS count FROM {table}"
            
            # Join Zorunlulukları
            need_join = False
            if "customers" in group_clause or customer_name: need_join = True
            if table == "order_items": need_join = True

            if need_join and table == "order_items": sql += " JOIN orders ON order_items.order_id = orders.id"
            if (table == "orders" or table == "customers") and "customers" in group_clause: 
                 if table == "orders": sql += " JOIN customers ON orders.customer_id = customers.id"
                 elif table == "customers": sql = sql.replace("FROM customers", "FROM orders JOIN customers ON orders.customer_id = customers.id")

            if where_clauses: sql += " WHERE " + " AND ".join(where_clauses)
            sql += group_clause
            return sql + ";"

        distinct_col_map = {
        "orders": "customer_id",
        "order_items": "product_id",
        "customers": "id",
        "products": "id"
        }
    
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
        


    #LIST 
    if intent == "list":
        # Aylara Göre Listeleme (Raporlama)
        if time_group == "month":
             # "Aylara göre siparişleri listele" denildiğinde aslında bir rapor (aggregation) istenir.
             sql = f"SELECT TO_CHAR({target_date_col}, 'YYYY-MM') as donem, COUNT(*) as siparis_sayisi FROM {table}"
             if where_clauses:
                 sql += " WHERE " + " AND ".join(where_clauses)
             sql += " GROUP BY donem ORDER BY donem"
             return sql + ";"
        
    # AGGREGATE FİLTRE (HAVING) VARSA ÖZEL İŞLEM] 
        # Örn: "1000 TL üzeri harcama yapan müşterileri listele"
        if table == "customers" and condition and condition[1] and condition[1] > 50:
             # Bu normal bir liste değil, HAVING sorgusudur.
             op, val = condition
             sql = f"SELECT customers.name, SUM(orders.total_amount) as toplam FROM orders JOIN customers ON orders.customer_id = customers.id"
             if where_clauses: sql += " WHERE " + " AND ".join(where_clauses)
             sql += f" GROUP BY customers.name HAVING SUM(orders.total_amount) {op} {val} ORDER BY toplam DESC LIMIT {limit}"
             return sql + ";"
    

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

        # SIRALAMA (TOP MANTIĞI BURADA)
        if order_dir:
            sort_col = target_date_col # Varsayılan: created_at (Zaman)
            
            # 1. Eğer bağlam "Para/Miktar" ise (Pahalı, Ucuz, Yüksek vb.)
            if sort_context == "amount":
                if table == "products": sort_col = "price"
                elif table == "orders": sort_col = "total_amount"
            
            # 2. Eğer bağlam "Zaman" ise (İlk, Son vb.)
            # sort_col zaten target_date_col (created_at) olarak kaldı. Değişmeye gerek yok.

            # 3. Bağlam yoksa ama Tablo Ürünler ise (Varsayılan olarak fiyata göre sırala)
            elif table == "products" and sort_context != "time":
                sort_col = "price"
                
            sql += f" ORDER BY {sort_col} {order_dir}"
            
        elif table == "orders": 
             sql += f" ORDER BY {target_date_col} DESC" # Varsayılan: Tarih (Yeniden eskiye)

        # LİMİT (TOP 5 vb.)
        sql += f" LIMIT {limit};"
        return sql



    #SUM
    if intent == "sum":
    # GRUPLAMA veya CUSTOMERS HATASI VARSA DÜZELT
        # Customers tablosunda sum yapılmaya çalışılırsa burası yakalar ve düzeltir.
        if group_by_col or time_group or table == "customers":
            agg_col = "orders.total_amount" # Varsayılan: Müşteri sorulsa bile sipariş topla
            main_tbl = "orders"
            
            if table == "products": 
                agg_col = "price"
                main_tbl = "products"
            elif table == "order_items": 
                agg_col = "order_items.quantity"
                main_tbl = "order_items"

            select_part = f"COALESCE(SUM({agg_col}), 0)"
            group_part = ""

            if time_group == "month":
                select_part = f"TO_CHAR({target_date_col}, 'YYYY-MM') as donem, {select_part}"
                group_part = " GROUP BY donem ORDER BY donem"
            elif group_by_col == "name":
                select_part = f"customers.name, {select_part}"
                group_part = " GROUP BY customers.name ORDER BY 2 DESC"

            sql = f"SELECT {select_part} AS total_sum FROM {main_tbl}"
            
            # Joinler
            if main_tbl == "orders" and (customer_name or group_by_col == "name" or table == "customers"):
                sql += " JOIN customers ON orders.customer_id = customers.id"
            elif main_tbl == "order_items":
                sql += " JOIN orders ON order_items.order_id = orders.id"

            if where_clauses: sql += " WHERE " + " AND ".join(where_clauses)
            sql += group_part
            return sql + ";"
    
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

