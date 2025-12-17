import psycopg2 #python ile postgresql bağlantısı
import pandas as pd #sqlden gelen sonuçları dataframe olarak tutmak için

def get_connection(): #postgre bağlantısını oluşturmak için
    return psycopg2.connect( #bağlantı nesnesini döndürür
        host="localhost", #eğer uzak sunucu olsaydı burda IP olurdu
        database="nlp_sql_db",
        user="beyzahiz",
        password=""
    )

def run_query(sql): #dışarıdan sql sorgusunu alır ve çalıştırır
    conn = get_connection() #postgresql bağlantısı açılır
    df = pd.read_sql(sql, conn) #sonuç dataframe e dönüşür
    conn.close()
    return df
