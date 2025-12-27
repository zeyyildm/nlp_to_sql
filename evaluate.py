import pandas as pd
import matplotlib.pyplot as plt
from rules import (
    normalize, find_intent, find_entity, detect_order_context, 
    extract_year, extract_month_year, extract_interval, detect_time_filter,
    extract_customer_name, extract_limit_and_order, extract_columns,
    extract_numeric_condition, extract_grouping_request, detect_sort_context, detect_distinct
)
from sql_generator import generate_sql

test_cases = [
    # --- KATEGORİ: COUNT ---
    {"cat": "COUNT", "q": "kaç müşteri var", "sql": "SELECT COUNT(*) AS count FROM customers;"},
    {"cat": "COUNT", "q": "bu ay kaç sipariş var", "sql": "SELECT COUNT(*) AS count FROM orders WHERE DATE_TRUNC('month', orders.created_at) = DATE_TRUNC('month', CURRENT_DATE);"},
    {"cat": "COUNT", "q": "son 3 ay kaç sipariş var", "sql": "SELECT COUNT(*) AS count FROM orders WHERE orders.created_at >= CURRENT_DATE - INTERVAL '3 months';"},
    {"cat": "COUNT", "q": "bu yıl kaç farklı müşteri sipariş verdi", "sql": "SELECT COUNT(DISTINCT customer_id) AS count FROM orders WHERE EXTRACT(YEAR FROM orders.created_at) = EXTRACT(YEAR FROM CURRENT_DATE);"},
    {"cat": "COUNT", "q": "bu yıl kaç müşteri en az 1 sipariş verdi", "sql": "SELECT COUNT(DISTINCT customer_id) AS count FROM orders WHERE EXTRACT(YEAR FROM orders.created_at) = EXTRACT(YEAR FROM CURRENT_DATE);"},
    {"cat": "COUNT", "q": "2025 te son 3 ayda kaç sipariş var", "sql": "SELECT COUNT(*) AS count FROM orders WHERE orders.created_at >= CURRENT_DATE - INTERVAL '3 months' AND EXTRACT(YEAR FROM orders.created_at) = 2025;"},
    {"cat": "COUNT", "q": "bu yıl kaç müşteri kayıt oldu", "sql": "SELECT COUNT(*) AS count FROM customers WHERE EXTRACT(YEAR FROM customers.created_at) = EXTRACT(YEAR FROM CURRENT_DATE);"},
    {"cat": "COUNT", "q": "bu ay kaç farklı ürün satıldı", "sql": "SELECT COUNT(DISTINCT order_items.product_id) AS count FROM order_items JOIN orders ON order_items.order_id = orders.id WHERE DATE_TRUNC('month', orders.created_at) = DATE_TRUNC('month', CURRENT_DATE);"},
    {"cat": "COUNT", "q": "bu ay toplam kaç ürün satıldı", "sql": "SELECT COUNT(*) AS count FROM order_items JOIN orders ON order_items.order_id = orders.id WHERE DATE_TRUNC('month', orders.created_at) = DATE_TRUNC('month', CURRENT_DATE);"},

    # --- KATEGORİ: SUM ---
    {"cat": "SUM", "q": "bu yıl toplam sipariş tutarı ne kadar", "sql": "SELECT COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders WHERE EXTRACT(YEAR FROM orders.created_at) = EXTRACT(YEAR FROM CURRENT_DATE);"},
    {"cat": "SUM", "q": "2025 martta toplam sipariş tutarı ne kadar", "sql": "SELECT COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders WHERE EXTRACT(MONTH FROM orders.created_at) = 3 AND EXTRACT(YEAR FROM orders.created_at) = 2025;"},
    {"cat": "SUM", "q": "bu ay toplam gelir ne kadar", "sql": "SELECT COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders WHERE DATE_TRUNC('month', orders.created_at) = DATE_TRUNC('month', CURRENT_DATE);"},
    {"cat": "SUM", "q": "aylara göre toplam ciro nedir", "sql": "SELECT TO_CHAR(orders.created_at, 'YYYY-MM') as donem, COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders GROUP BY donem ORDER BY donem;"},
    {"cat": "SUM", "q": "müşterilere göre toplam harcama ne kadar", "sql": "SELECT customers.name, COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders JOIN customers ON orders.customer_id = customers.id GROUP BY customers.name ORDER BY 2 DESC;"},
 
    # --- KATEGORİ: LIST ---
    {"cat": "LIST", "q": "ilk eklenen 5 müşteriyi listele", "sql": "SELECT * FROM customers ORDER BY customers.created_at ASC LIMIT 5;"},
    {"cat": "LIST", "q": "son eklenen 3 musteriyi listele", "sql": "SELECT * FROM customers ORDER BY customers.created_at DESC LIMIT 3;"},
    {"cat": "LIST", "q": "ilk 5 siparişi göster", "sql": "SELECT * FROM orders ORDER BY orders.created_at ASC LIMIT 5;"},
    {"cat": "LIST", "q": "müşterilerinin isimlerini göster", "sql": "SELECT name FROM customers LIMIT 10;"},
    {"cat": "LIST", "q": "10000 tl üzeri harcama yapan müşterileri listele", "sql": "SELECT customers.name, SUM(orders.total_amount) as toplam FROM orders JOIN customers ON orders.customer_id = customers.id GROUP BY customers.name HAVING SUM(orders.total_amount) > 10000 ORDER BY toplam DESC LIMIT 10;"},
    {"cat": "LIST", "q": "aylara göre siparişleri listele", "sql": "SELECT TO_CHAR(orders.created_at, 'YYYY-MM') as donem, COUNT(*) as siparis_sayisi FROM orders GROUP BY donem ORDER BY donem;"},
    {"cat": "LIST", "q": "siparişleri ve müşterileri birlikte listele", "sql": "SELECT orders.total_amount, customers.name, orders.created_at FROM orders JOIN customers ON orders.customer_id = customers.id LIMIT 10;"},

    # --- KATEGORİ: TOP/MAX/MIN ---
    {"cat": "MAX/MIN", "q": "en pahalı ürün ne kadar", "sql": "SELECT MAX(price) as sonuc FROM products;"},
    {"cat": "MAX/MIN", "q": "en ucuz ürün ne kadar", "sql": "SELECT MIN(price) as sonuc FROM products;"},
    {"cat": "MAX/MIN", "q": "en yüksek sipariş tutarı ne kadar", "sql": "SELECT MAX(total_amount) as sonuc FROM orders;"},
    {"cat": "MAX/MIN", "q": "en düşük sipariş tutarı ne kadar", "sql": "SELECT MIN(total_amount) as sonuc FROM orders;"},
    {"cat": "MAX/MIN", "q": "ilk 3 siparişi göster", "sql": "SELECT * FROM orders ORDER BY orders.created_at ASC LIMIT 3;"},
    {"cat": "MAX/MIN", "q": "son 5 siparişi göster", "sql": "SELECT * FROM orders ORDER BY orders.created_at DESC LIMIT 5;"},
    {"cat": "MAX/MIN", "q": "en pahalı 5 ürün göster", "sql": "SELECT products.name FROM products ORDER BY price DESC LIMIT 5;"},
    {"cat": "MAX/MIN", "q": "en ucuz 5 ürün göster", "sql": "SELECT products.name FROM products ORDER BY price ASC LIMIT 5;"}
]

def run_evaluation():
    results = []
    correct_count = 0
    total_count = len(test_cases)

    print(f"--- MODEL DEĞERLENDİRMESİ BAŞLIYOR ({total_count} TEST SENARYOSU) ---\n")

    for case in test_cases:
        text = case["q"]
        expected = case["sql"].strip().lower().replace(";", "")
        category = case["cat"]

        # --- MAIN.PY SİMÜLASYONU ---
        normalized = normalize(text)
        distinct_flag = detect_distinct(normalized)
        intent = find_intent(normalized)
        entity = find_entity(normalized)
        
        if intent == "top": intent = "list"
        if intent == "unknown" and entity is not None: intent = "list"
        
        is_order_context = detect_order_context(normalized)
        if "urun" in normalized or "ürün" in normalized:
            if "satildi" in normalized or "satilan" in normalized: entity = "order_items"
            elif "eklendi" in normalized: entity = "products"
        
        if entity == "customers" and is_order_context:
            entity = "orders"
            distinct_flag = True

        year_info = extract_year(normalized)
        date_info = extract_month_year(normalized)
        interval_num = extract_interval(normalized)
        rel_time = detect_time_filter(normalized)
        cust_name = extract_customer_name(normalized)
        limit_num, order_direction = extract_limit_and_order(normalized)
        cols = extract_columns(normalized)
        cond_op, cond_val = extract_numeric_condition(normalized)
        group_col, time_mode = extract_grouping_request(normalized)
        sort_ctx = detect_sort_context(normalized)

        generated_sql = generate_sql(
            intent, entity, year=year_info, specific_date=date_info,
            interval_months=interval_num, relative_time=rel_time,
            distinct=distinct_flag, customer_name=cust_name,
            limit=limit_num, order_dir=order_direction,
            selected_columns=cols, condition=(cond_op, cond_val),
            group_by_col=group_col, time_group=time_mode, sort_context=sort_ctx
        )

        is_correct = False
        clean_gen = ""
        if generated_sql:
            clean_gen = generated_sql.strip().lower().replace(";", "")
            # Basit eşleşme kontrolü
            if clean_gen == expected:
                is_correct = True
                correct_count += 1
        
        results.append({
            "Kategori": category,
            "Soru": text,
            "Durum": "BAŞARILI" if is_correct else "HATALI",
            "Beklenen": expected,
            "Üretilen": clean_gen
        })

    df = pd.DataFrame(results)
    accuracy = (correct_count / total_count) * 100
    
    print("-" * 60)
    print(f"GENEL BAŞARI ORANI (ACCURACY): %{accuracy:.2f}")
    print("-" * 60)
    
    print("\nKATEGORİ BAZLI PERFORMANS:")
    category_summary = df.groupby("Kategori")["Durum"].apply(lambda x: (x == "BAŞARILI").mean() * 100).reset_index()
    category_summary.rename(columns={"Durum": "Başarı (%)"}, inplace=True)
    print(category_summary)
    
    # Hata Raporu
    errors = df[df["Durum"] == "HATALI"]
    if not errors.empty:
        print("\n--- HATALI SORGULAR (BEKLENEN DURUM) ---")
        for index, row in errors.iterrows():
            print(f"\nSoru: {row['Soru']}")
            print(f"Beklenen: {row['Beklenen']}")
            print(f"Üretilen: {row['Üretilen']}")
    
    # CSV Kaydet
    df.to_csv("degerlendirme_sonuclari.csv", index=False)
    print("\nSonuçlar 'degerlendirme_sonuclari.csv' dosyasına kaydedildi.")

    # GRAFİK ÇİZİMİ 
    print("\nGrafik oluşturuluyor...")
    
    # Grafik Alanı (1 satır, 2 sütun)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Model Performans Analizi (Genel Doğruluk: %{accuracy:.1f})', fontsize=16)

    # 1. BAR GRAFİĞİ (Kategori Bazlı Başarı)
    bars = ax1.bar(category_summary["Kategori"], category_summary["Başarı (%)"], color=['#4CAF50' if x == 100 else '#FF9800' for x in category_summary["Başarı (%)"]])
    ax1.set_title("Kategori Bazlı Başarı Oranı", fontsize=12)
    ax1.set_ylabel("Başarı Yüzdesi (%)")
    ax1.set_ylim(0, 110)
    
    # Barların üzerine değer yazma
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'%{height:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 2. PASTA GRAFİĞİ (Genel Başarı/Hata Dağılımı)
    success_count = df[df["Durum"] == "BAŞARILI"].shape[0]
    fail_count = df[df["Durum"] == "HATALI"].shape[0]
    
    labels = [f'Başarılı ({success_count})', f'Hatalı ({fail_count})']
    sizes = [success_count, fail_count]
    colors = ['#4CAF50', '#F44336'] # Yeşil ve Kırmızı
    explode = (0.1, 0)  # Başarılı dilimini biraz ayır

    ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    ax2.set_title("Genel Model Başarısı", fontsize=12)

    # Grafiği Kaydet
    plt.tight_layout()
    plt.savefig('degerlendirme_grafigi.png')
    print("Grafik 'degerlendirme_grafigi.png' olarak kaydedildi.")
    # plt.show() # Eğer masaüstü uygulamasıysa açar, sunucuda gerek yok

if __name__ == "__main__":
    run_evaluation()