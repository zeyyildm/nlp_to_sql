def build_time_where_clauses(
    year=None,
    specific_date=None,
    interval_months=None,
    relative_time=None,
    customer_name=None,
    date_column="created_at"
):
    """
    Zaman filtrelerini WHERE clause'larına dönüştürür.
    Artık elif yerine if kullanarak çoklu zaman şartlarını destekler.
    
    Parametreler:
    - date_column: Tarih kolonunun adı (örn: "orders.created_at", "customers.created_at")
    """
    where_clauses = []

    # specific_date en spesifik olduğu için önce kontrol et
    if specific_date:  # örn: (3, 2022)
        month, sp_year = specific_date
        where_clauses.append(f"EXTRACT(MONTH FROM {date_column}) = {month}")
        where_clauses.append(f"EXTRACT(YEAR FROM {date_column}) = {sp_year}")

    # interval_months ve year birlikte kullanılabilir (örn: "2025 te son 3 ay")
    if interval_months:  # örn: 3
        where_clauses.append(f"{date_column} >= CURRENT_DATE - INTERVAL '{interval_months} months'")
        # Eğer year de varsa, interval'ı year ile sınırla
        if year:
            where_clauses.append(f"EXTRACT(YEAR FROM {date_column}) = {year}")

    # relative_time kontrolü (year ile birlikte kullanılabilir)
    if relative_time == "this_month":
        where_clauses.append(f"DATE_TRUNC('month', {date_column}) = DATE_TRUNC('month', CURRENT_DATE)")

    elif relative_time == "last_month":
        where_clauses.append(f"DATE_TRUNC('month', {date_column}) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')")

    elif relative_time == "this_year":
        where_clauses.append(f"EXTRACT(YEAR FROM {date_column}) = EXTRACT(YEAR FROM CURRENT_DATE)")

    # year sadece başka bir zaman filtresi yoksa kullanılır
    # (interval_months veya relative_time ile birlikte kullanılıyorsa zaten eklenmiş olur)
    if year and not interval_months and not relative_time and not specific_date:
        where_clauses.append(f"EXTRACT(YEAR FROM {date_column}) = {year}")

    if customer_name:
        # İsim eşleşmesi (Büyük/Küçük harf duyarsız)
        # customers tablosu için name kolonu kullanılır (first_name değil)
        where_clauses.append(f"customers.name ILIKE '%{customer_name}%'")

    return where_clauses


