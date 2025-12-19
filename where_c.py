def build_time_where_clauses(
    year=None,
    specific_date=None,
    interval_months=None,
    relative_time=None
):
    where_clauses = []

    if specific_date:  # örn: (3, 2022)
        month, sp_year = specific_date
        where_clauses.append(f"EXTRACT(MONTH FROM created_at) = {month}")
        where_clauses.append(f"EXTRACT(YEAR FROM created_at) = {sp_year}")

    elif interval_months:  # örn: 3
        where_clauses.append(f"created_at >= CURRENT_DATE - INTERVAL '{interval_months} months'")

    elif relative_time == "this_month":
        where_clauses.append("DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)")

    elif relative_time == "last_month":
        where_clauses.append("DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')")

    elif relative_time == "this_year":
        where_clauses.append("EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE)")

    elif year:
        where_clauses.append(f"EXTRACT(YEAR FROM created_at) = {year}")

    return where_clauses


