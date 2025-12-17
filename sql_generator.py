from rules import extract_year

# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
def generate_sql(intent: str, table: str, text: str) -> str | None:
    if not table:
        return None
    
    year = extract_year(text)

    if intent == "count":
        sql =  f"SELECT COUNT(*) FROM {table}"

        if year and table == "orders":
            sql += f" WHERE EXTRACT(YEAR FROM created_at) = {year}"
        return sql + ";"
        

    if intent == "list":
        return f"SELECT * FROM {table} LIMIT 10;"

    return None

