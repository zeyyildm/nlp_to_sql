# intent + tablo bilgisini alır ve SQL cümlesine dönüştürür
def generate_sql(intent: str, table: str) -> str | None:
    if not table:
        return None

    if intent == "count":
        return f"SELECT COUNT(*) FROM {table};"

    if intent == "list":
        return f"SELECT * FROM {table} LIMIT 10;"

    return None
