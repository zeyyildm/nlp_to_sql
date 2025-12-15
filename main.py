from db import run_query

sql = "SELECT * FROM customers LIMIT 5;"
result = run_query(sql)

print(result)
