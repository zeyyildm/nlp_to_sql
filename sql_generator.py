
# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
def generate_sql(intent: str, table: str,  year=None, specific_date=None, interval_months=None, relative_time=None) -> str | None:
    """
    Parametreler:
    - intent: count, list vb.
    - table: orders, customers vb.
    - year: Sadece yıl bilgisi (Örn: 2022)
    - specific_date: (Ay, Yıl) formatında tuple (Örn: (3, 2022))
    - interval_months: Son kaç ay olduğu (Örn: 3)
    - relative_time: 'this_month' veya 'last_month'
    """
    if not table:
        return None

    if intent == "count":
        sql =  f"SELECT COUNT(*) FROM {table}"

        where_clauses = [] #WHERE koşullarının toplanacağı boş bir liste oluşturuldu

        if specific_date: #spesifik tarih 2022 Mart gibi
            month, sp_year = specific_date
            where_clauses.append(f"EXTRACT(MONTH FROM created_at) = {month}")
            where_clauses.append(f"EXTRACT(YEAR FROM created_at) = {sp_year}")

        elif interval_months: #son 3 ay gibi, şimdiki zamandan X ay geriye git
            where_clauses.append(f"created_at >= CURRENT_DATE - INTERVAL '{interval_months} months'")

        elif relative_time == "this_month": #geçen ay, bu ay 
            where_clauses.append("DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)")
        
        elif relative_time == "last_month":
            where_clauses.append("DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')")

        elif year: #sadece yıl 
            where_clauses.append(f"EXTRACT(YEAR FROM created_at) = {year}")

        if where_clauses: #hepsini birleştirmek için
            sql += " WHERE " + " AND ".join(where_clauses)

        return sql + ";"
        

    if intent == "list":
        return f"SELECT * FROM {table} LIMIT 10;"

    return None

