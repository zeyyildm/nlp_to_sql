# NLP to SQL Converter

A rule-based Natural Language Processing (NLP) system that converts Turkish natural language questions into SQL queries. This project enables users to query a PostgreSQL database using plain Turkish language instead of writing SQL directly.

**OVERALL ACCURACY: 96.6%**

## 🎯 Features

- **Natural Language Understanding**: Processes Turkish questions and extracts intent, entities, and conditions
- **SQL Generation**: Automatically generates PostgreSQL-compatible SQL queries
- **Multiple Query Types**: Supports COUNT, SUM, LIST, MAX, and MIN operations
- **Time Filtering**: Handles various time expressions (this month, last month, this year, specific dates, intervals)
- **Advanced Filtering**: Supports customer names, numeric conditions, grouping, and sorting
- **Evaluation System**: Includes comprehensive test cases and performance metrics

## 📋 Table of Contents

- [Installation](#installation)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [Supported Query Types](#supported-query-types)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Evaluation](#evaluation)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.7+
- PostgreSQL database
- pip package manager

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nlp_to_sql
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt 
   ```

4. **Configure database connection**
   
   Edit `db.py` and update the database connection parameters:
   ```python
   host="localhost"
   database="nlp_sql_db"
   user="your_username"
   password="your_password"
   ```

## 🗄️ Database Setup

1. **Create the database**
   ```bash
   createdb nlp_sql_db
   ```

2. **Run the schema script**
   ```bash
   psql -d nlp_sql_db -f schema.sql
   ```

3. **Insert sample data**
   ```bash
   psql -d nlp_sql_db -f tablolar.sql
   ```

The database includes the following tables:
- `customers`: Customer information (id, name, email, created_at)
- `products`: Product catalog (id, name, price, created_at)
- `orders`: Order records (id, customer_id, total_amount, created_at)
- `order_items`: Order line items (id, order_id, product_id, quantity)

## 💻 Usage

### Interactive Mode

Run the main script to start an interactive session:

```bash
python main.py
```

Example interaction:
```
Soru gir (çıkmak için q): kaç müşteri var
Normalize edilmiş: kac musteri var
Tespit edilen intent: count
Tespit edilen tablo: customers
Oluşturulan SQL: SELECT COUNT(*) AS count FROM customers;
```

### Evaluation Mode

Run the evaluation script to test the system with predefined test cases:

```bash
python evaluate.py
```

This will:
- Test the system against 48+ test cases
- Generate accuracy metrics
- Create performance visualizations
- Export results to CSV

## 📊 Supported Query Types

### COUNT Queries
Count records with optional filtering:
- "kaç müşteri var" (how many customers are there)
- "bu ay kaç sipariş var" (how many orders this month)
- "bu yıl kaç farklı müşteri sipariş verdi" (how many distinct customers ordered this year)

### SUM Queries
Calculate totals:
- "bu yıl toplam sipariş tutarı ne kadar" (total order amount this year)
- "aylara göre toplam ciro nedir" (total revenue by month)
- "müşterilere göre toplam harcama ne kadar" (total spending by customer)

### LIST Queries
Retrieve records with sorting and filtering:
- "ilk 5 siparişi göster" (show first 5 orders)
- "10000 tl üzeri harcama yapan müşterileri listele" (list customers spending over 10000 TL)
- "aylara göre siparişleri listele" (list orders by month)

### MAX/MIN Queries
Find extreme values:
- "en pahalı ürün ne kadar" (what is the most expensive product)
- "en ucuz ürün ne kadar" (what is the cheapest product)
- "en yüksek sipariş tutarı ne kadar" (what is the highest order amount)

## 📝 Examples

### Time-based Queries

```
Soru: bu ay kaç sipariş var
SQL: SELECT COUNT(*) AS count FROM orders 
     WHERE DATE_TRUNC('month', orders.created_at) = DATE_TRUNC('month', CURRENT_DATE);
```

```
Soru: son 3 ay kaç sipariş var
SQL: SELECT COUNT(*) AS count FROM orders 
     WHERE orders.created_at >= CURRENT_DATE - INTERVAL '3 months';
```

```
Soru: 2025 martta toplam sipariş tutarı ne kadar
SQL: SELECT COALESCE(SUM(orders.total_amount), 0) AS total_sum FROM orders 
     WHERE EXTRACT(MONTH FROM orders.created_at) = 3 
     AND EXTRACT(YEAR FROM orders.created_at) = 2025;
```

### Filtering and Grouping

```
Soru: 10000 tl üzeri harcama yapan müşterileri listele
SQL: SELECT customers.name, SUM(orders.total_amount) as toplam 
     FROM orders JOIN customers ON orders.customer_id = customers.id 
     GROUP BY customers.name 
     HAVING SUM(orders.total_amount) > 10000 
     ORDER BY toplam DESC LIMIT 10;
```

```
Soru: aylara göre toplam ciro nedir
SQL: SELECT TO_CHAR(orders.created_at, 'YYYY-MM') as donem, 
            COALESCE(SUM(orders.total_amount), 0) AS total_sum 
     FROM orders 
     GROUP BY donem 
     ORDER BY donem;
```

### Sorting and Limiting

```
Soru: en pahalı 5 ürün göster
SQL: SELECT products.name FROM products 
     ORDER BY price DESC LIMIT 5;
```

```
Soru: ilk eklenen 5 müşteriyi listele
SQL: SELECT * FROM customers 
     ORDER BY customers.created_at ASC LIMIT 5;
```

## 📁 Project Structure

```
nlp_to_sql/
├── main.py              # Main interactive application
├── rules.py             # NLP rule extraction functions
├── sql_generator.py     # SQL query generation logic
├── db.py                # Database connection and query execution
├── where_c.py           # Time-based WHERE clause builder
├── evaluate.py          # Evaluation script with test cases
├── schema.sql           # Database schema definition
├── tablolar.sql         # Sample data insertion script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Key Modules

- **`rules.py`**: Contains all NLP extraction functions:
  - Text normalization
  - Intent detection (count, sum, list, max, min)
  - Entity recognition (customers, orders, products, order_items)
  - Time extraction (year, month, intervals, relative time)
  - Condition extraction (numeric operators, customer names)
  - Grouping and sorting context detection

- **`sql_generator.py`**: Generates SQL queries based on extracted parameters:
  - Handles different query types (COUNT, SUM, LIST, MAX, MIN)
  - Manages JOINs for related tables
  - Applies WHERE clauses for filtering
  - Handles GROUP BY and HAVING clauses
  - Applies ORDER BY and LIMIT clauses

- **`where_c.py`**: Builds time-based WHERE clauses:
  - Supports multiple time filters simultaneously
  - Handles specific dates, intervals, and relative time expressions

## 🧪 Evaluation

The evaluation system tests the model against 48+ test cases across different categories:

- **COUNT**: 9 test cases
- **SUM**: 5 test cases
- **LIST**: 8 test cases
- **MAX/MIN**: 8 test cases

Run the evaluation:
```bash
python evaluate.py
```

Output includes:
- Overall accuracy percentage
- Category-wise performance metrics
- Detailed error reports
- CSV export of results
- Performance visualization graphs

Results are saved to:
- `degerlendirme_sonuclari.csv`: Detailed test results
- `degerlendirme_grafigi.png`: Performance visualization

***


<img width="730" height="313" alt="Ekran Resmi 2026-12-30 21 21 39" src="https://github.com/user-attachments/assets/1226d1d3-5d2a-4e5b-9e26-69ebccd5dd2c" />


***





## 🔧 Technical Details

### Text Normalization
- Converts Turkish characters to ASCII equivalents (ç→c, ğ→g, etc.)
- Removes special characters
- Normalizes whitespace
- Converts to lowercase

### Intent Detection Priority
1. LIST (highest priority)
2. COUNT
3. MAX/MIN
4. TOP (converted to LIST)
5. SUM

### Supported Time Expressions
- **Specific dates**: "2025 mart" (March 2025)
- **Relative time**: "bu ay" (this month), "geçen ay" (last month), "bu yıl" (this year)
- **Intervals**: "son 3 ay" (last 3 months)
- **Year only**: "2025" (year 2025)

### Supported Conditions
- **Greater than**: "1000 tl üzeri" (> 1000)
- **Less than**: "500 tl altı" (< 500)
- **Equal**: "1000 tl olan" (= 1000)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Improvement
- Support for more complex queries (subqueries, unions)
- Better handling of ambiguous queries
- Support for additional entities and relationships
- Machine learning-based intent detection
- Multi-language support


## 👥 Authors

- Project contributors

## 🙏 Acknowledgments

- Built for educational purposes to demonstrate rule-based NLP to SQL conversion
- Uses PostgreSQL as the database backend
- Implements comprehensive Turkish language processing rules
