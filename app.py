"""
Food Wastage Management System
Streamlit App
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------------------
@st.cache_resource
def get_engine():
    connection_string = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password="Postgresql@0322",
        host="localhost",
        port=5432,
        database="foodwastagedb"
    )
    return create_engine(connection_string)

engine = get_engine()

def run_query(query, params=None):
    with engine.connect() as conn:
        if params:
            return pd.read_sql(text(query), conn, params=params)
        return pd.read_sql(text(query), conn)

def execute_statement(statement, params=None):
    with engine.begin() as conn:
        if params:
            conn.execute(text(statement), params)
        else:
            conn.execute(text(statement))

# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Food Wastage Management System",
    page_icon="🍱",
    layout="wide"
)

# ---------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------
st.sidebar.title("🍱 Food Wastage MS")
page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📋 Data Explorer",
    "📊 SQL Analysis",
    "📈 Charts & EDA",
    "✏️ CRUD Operations"
])

# =====================================================================
# PAGE 1: HOME
# =====================================================================
if page == "🏠 Home":
    st.title("🍱 Local Food Wastage Management System")
    st.markdown("A data-driven system to track, analyze, and reduce local food wastage.")
    st.divider()

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        count = run_query("SELECT COUNT(*) AS c FROM providers")["c"][0]
        st.metric("Total Providers", count)
    with col2:
        count = run_query("SELECT COUNT(*) AS c FROM receivers")["c"][0]
        st.metric("Total Receivers", count)
    with col3:
        count = run_query("SELECT COUNT(*) AS c FROM food_listings")["c"][0]
        st.metric("Food Listings", count)
    with col4:
        count = run_query("SELECT COUNT(*) AS c FROM claims")["c"][0]
        st.metric("Total Claims", count)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Project Overview")
        st.markdown("""
        This system helps manage and reduce food wastage by:
        - Connecting **food providers** (restaurants, grocery stores, farms)
        - With **receivers** (NGOs, shelters, individuals)
        - Tracking **food listings** and **claims**
        - Providing **insights** to improve food distribution
        """)
    with col2:
        st.subheader("🛠️ Tech Stack")
        st.markdown("""
        | Component | Technology |
        |---|---|
        | Database | PostgreSQL |
        | Backend | Python |
        | Data Analysis | Pandas, Matplotlib, Seaborn |
        | Frontend | Streamlit |
        | ORM | SQLAlchemy |
        """)

    st.divider()
    st.subheader("📊 Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        rate = run_query("""
            SELECT ROUND(COUNT(c.claim_id) * 100.0 / NULLIF(COUNT(fl.food_id), 0), 2) AS rate
            FROM food_listings fl LEFT JOIN claims c ON fl.food_id = c.food_id
        """)["rate"][0]
        st.metric("Claim Rate", f"{rate}%")
    with col2:
        total_qty = run_query("SELECT SUM(quantity) AS q FROM food_listings")["q"][0]
        st.metric("Total Quantity Listed", f"{int(total_qty):,}")
    with col3:
        cities = run_query("SELECT COUNT(DISTINCT location) AS c FROM food_listings")["c"][0]
        st.metric("Cities Covered", cities)


# =====================================================================
# PAGE 2: DATA EXPLORER
# =====================================================================
elif page == "📋 Data Explorer":
    st.title("📋 Data Explorer")
    st.markdown("Browse and filter all tables in the database.")

    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])

    df = run_query(f"SELECT * FROM {table}")

    # Filters
    st.subheader("🔍 Filters")
    col1, col2 = st.columns(2)

    if table == "food_listings":
        with col1:
            food_types = ["All"] + sorted(df["food_type"].dropna().unique().tolist())
            selected_type = st.selectbox("Food Type", food_types)
        with col2:
            meal_types = ["All"] + sorted(df["meal_type"].dropna().unique().tolist())
            selected_meal = st.selectbox("Meal Type", meal_types)
        if selected_type != "All":
            df = df[df["food_type"] == selected_type]
        if selected_meal != "All":
            df = df[df["meal_type"] == selected_meal]

    elif table == "providers":
        with col1:
            types = ["All"] + sorted(df["type"].dropna().unique().tolist())
            selected = st.selectbox("Provider Type", types)
        with col2:
            cities = ["All"] + sorted(df["city"].dropna().unique().tolist())
            selected_city = st.selectbox("City", cities)
        if selected != "All":
            df = df[df["type"] == selected]
        if selected_city != "All":
            df = df[df["city"] == selected_city]

    elif table == "receivers":
        with col1:
            types = ["All"] + sorted(df["type"].dropna().unique().tolist())
            selected = st.selectbox("Receiver Type", types)
        with col2:
            cities = ["All"] + sorted(df["city"].dropna().unique().tolist())
            selected_city = st.selectbox("City", cities)
        if selected != "All":
            df = df[df["type"] == selected]
        if selected_city != "All":
            df = df[df["city"] == selected_city]

    elif table == "claims":
        with col1:
            statuses = ["All"] + sorted(df["status"].dropna().unique().tolist())
            selected = st.selectbox("Status", statuses)
        if selected != "All":
            df = df[df["status"] == selected]

    st.markdown(f"**Showing {len(df)} records**")
    st.dataframe(df, use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, f"{table}_filtered.csv", "text/csv")


# =====================================================================
# PAGE 3: SQL ANALYSIS
# =====================================================================
elif page == "📊 SQL Analysis":
    st.title("📊 SQL Analysis Queries")
    st.markdown("Results from all 17 analysis queries.")

    query_option = st.selectbox("Select Query", [
        "Q1: Total Listed vs Claimed",
        "Q2: Top 10 Providers by Quantity",
        "Q3: Most Claimed Food Types",
        "Q4: Claim Status Breakdown",
        "Q5: City-wise Food Availability",
        "Q6: Expiry Analysis",
        "Q7: Most Active Receivers",
        "Q8: Provider Type Breakdown",
        "Q9: Monthly Claim Trends",
        "Q10: Unclaimed Food Listings",
        "Q11: Meal Type Distribution",
        "Q12: Avg Quantity per Provider Type",
        "Q13: Receivers by City",
        "Q14: Top 10 Wastage Items",
        "Q15: Claim Success Rate by Food Type",
        "Q16: Inactive Providers",
        "Q17: Daily Average Claims"
    ])

    queries = {
        "Q1: Total Listed vs Claimed": """
            SELECT (SELECT COUNT(*) FROM food_listings) AS total_food_listed,
                   (SELECT COUNT(*) FROM claims) AS total_food_claimed,
                   ROUND((SELECT COUNT(*) FROM claims)::NUMERIC /
                   (SELECT COUNT(*) FROM food_listings) * 100, 2) AS claim_rate_percent
        """,
        "Q2: Top 10 Providers by Quantity": """
            SELECT p.provider_id, p.name AS provider_name, p.type, p.city,
                   SUM(fl.quantity) AS total_quantity_donated
            FROM providers p JOIN food_listings fl ON p.provider_id = fl.provider_id
            GROUP BY p.provider_id, p.name, p.type, p.city
            ORDER BY total_quantity_donated DESC LIMIT 10
        """,
        "Q3: Most Claimed Food Types": """
            SELECT fl.food_type, COUNT(c.claim_id) AS total_claims
            FROM food_listings fl LEFT JOIN claims c ON fl.food_id = c.food_id
            GROUP BY fl.food_type ORDER BY total_claims DESC
        """,
        "Q4: Claim Status Breakdown": """
            SELECT status, COUNT(*) AS total,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM claims GROUP BY status ORDER BY total DESC
        """,
        "Q5: City-wise Food Availability": """
            SELECT location AS city, COUNT(food_id) AS total_listings,
                   SUM(quantity) AS total_quantity_available
            FROM food_listings GROUP BY location ORDER BY total_quantity_available DESC
        """,
        "Q6: Expiry Analysis": """
            SELECT CASE
                WHEN expiry_date < CURRENT_DATE THEN 'Expired'
                WHEN expiry_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'Expiring Soon'
                ELSE 'Fresh' END AS expiry_status,
                COUNT(*) AS total_items, SUM(quantity) AS total_quantity
            FROM food_listings WHERE expiry_date IS NOT NULL GROUP BY expiry_status
        """,
        "Q7: Most Active Receivers": """
            SELECT r.receiver_id, r.name, r.type, r.city, COUNT(c.claim_id) AS total_claims
            FROM receivers r JOIN claims c ON r.receiver_id = c.receiver_id
            GROUP BY r.receiver_id, r.name, r.type, r.city
            ORDER BY total_claims DESC LIMIT 10
        """,
        "Q8: Provider Type Breakdown": """
            SELECT type AS provider_type, COUNT(DISTINCT provider_id) AS total_providers,
                   SUM(quantity) AS total_quantity_donated
            FROM food_listings GROUP BY type ORDER BY total_quantity_donated DESC
        """,
        "Q9: Monthly Claim Trends": """
            SELECT TO_CHAR("timestamp", 'YYYY-MM') AS month, COUNT(claim_id) AS total_claims
            FROM claims WHERE "timestamp" IS NOT NULL
            GROUP BY TO_CHAR("timestamp", 'YYYY-MM') ORDER BY month
        """,
        "Q10: Unclaimed Food Listings": """
            SELECT fl.food_id, fl.food_name, fl.quantity, fl.food_type, fl.location, fl.expiry_date
            FROM food_listings fl LEFT JOIN claims c ON fl.food_id = c.food_id
            WHERE c.claim_id IS NULL ORDER BY fl.expiry_date ASC
        """,
        "Q11: Meal Type Distribution": """
            SELECT meal_type, COUNT(*) AS total_listings, SUM(quantity) AS total_quantity,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM food_listings GROUP BY meal_type ORDER BY total_listings DESC
        """,
        "Q12: Avg Quantity per Provider Type": """
            SELECT p.type AS provider_type, ROUND(AVG(fl.quantity), 2) AS avg_quantity,
                   SUM(fl.quantity) AS total_quantity, COUNT(fl.food_id) AS total_listings
            FROM providers p JOIN food_listings fl ON p.provider_id = fl.provider_id
            GROUP BY p.type ORDER BY avg_quantity DESC
        """,
        "Q13: Receivers by City": """
            SELECT city, COUNT(receiver_id) AS total_receivers
            FROM receivers GROUP BY city ORDER BY total_receivers DESC
        """,
        "Q14: Top 10 Wastage Items": """
            SELECT fl.food_name, fl.food_type,
                   SUM(fl.quantity) AS total_listed,
                   COUNT(c.claim_id) AS times_claimed,
                   SUM(fl.quantity) - COUNT(c.claim_id) AS wasted_quantity
            FROM food_listings fl LEFT JOIN claims c ON fl.food_id = c.food_id
            GROUP BY fl.food_name, fl.food_type
            ORDER BY wasted_quantity DESC LIMIT 10
        """,
        "Q15: Claim Success Rate by Food Type": """
            SELECT fl.food_type, COUNT(fl.food_id) AS total_listed,
                   COUNT(c.claim_id) AS total_claimed,
                   ROUND(COUNT(c.claim_id) * 100.0 / NULLIF(COUNT(fl.food_id), 0), 2) AS claim_success_rate
            FROM food_listings fl LEFT JOIN claims c ON fl.food_id = c.food_id
            GROUP BY fl.food_type ORDER BY claim_success_rate DESC
        """,
        "Q16: Inactive Providers": """
            SELECT p.provider_id, p.name, p.type, p.city, COUNT(fl.food_id) AS total_listings
            FROM providers p
            LEFT JOIN food_listings fl ON p.provider_id = fl.provider_id
            LEFT JOIN claims c ON fl.food_id = c.food_id
            WHERE c.claim_id IS NULL
            GROUP BY p.provider_id, p.name, p.type, p.city
            ORDER BY total_listings DESC
        """,
        "Q17: Daily Average Claims": """
            SELECT ROUND(AVG(daily_claims), 2) AS avg_daily_claims
            FROM (SELECT DATE("timestamp") AS claim_date, COUNT(*) AS daily_claims
                  FROM claims WHERE "timestamp" IS NOT NULL
                  GROUP BY DATE("timestamp")) daily
        """
    }

    df = run_query(queries[query_option])
    st.subheader(query_option)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results", csv, "query_result.csv", "text/csv")


# =====================================================================
# PAGE 4: CHARTS & EDA
# =====================================================================
elif page == "📈 Charts & EDA":
    st.title("📈 Charts & EDA")

    chart = st.selectbox("Select Chart", [
        "Food Type Distribution",
        "Meal Type Distribution",
        "Claim Status Breakdown",
        "Quantity Distribution",
        "Provider Type Distribution",
        "Quantity by Provider Type",
        "Claims by Food Type",
        "Monthly Claim Trends",
        "Top 10 Cities by Food Availability",
        "Expiry Status Breakdown",
        "Heatmap: Food Type vs Meal Type",
        "Claim Status by Food Type",
        "Scatter: Quantity vs Claims"
    ])

    sns.set_theme(style="whitegrid")
    COLORS = sns.color_palette("Set2")

    food    = run_query("SELECT * FROM food_listings")
    claims  = run_query("SELECT * FROM claims")
    providers = run_query("SELECT * FROM providers")
    receivers = run_query("SELECT * FROM receivers")
    food_claims = food.merge(claims, on="food_id", how="left")
    full_data = food_claims.merge(providers, on="provider_id", how="left", suffixes=("", "_provider"))

    fig, ax = plt.subplots(figsize=(9, 5))

    if chart == "Food Type Distribution":
        food["food_type"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Distribution of Food Types", fontweight="bold")
        ax.set_xlabel("Food Type"); ax.set_ylabel("Count")
        plt.xticks(rotation=45)

    elif chart == "Meal Type Distribution":
        fig, ax = plt.subplots(figsize=(7, 7))
        meal_counts = food["meal_type"].value_counts()
        ax.pie(meal_counts, labels=meal_counts.index, autopct="%1.1f%%", colors=COLORS)
        ax.set_title("Meal Type Distribution", fontweight="bold")

    elif chart == "Claim Status Breakdown":
        claims["status"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Claim Status Breakdown", fontweight="bold")
        ax.set_xlabel("Status"); ax.set_ylabel("Count")
        plt.xticks(rotation=0)

    elif chart == "Quantity Distribution":
        food["quantity"].dropna().plot(kind="hist", bins=20, color=COLORS[0], edgecolor="black", ax=ax)
        ax.set_title("Distribution of Food Quantity", fontweight="bold")
        ax.set_xlabel("Quantity"); ax.set_ylabel("Frequency")

    elif chart == "Provider Type Distribution":
        providers["type"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Provider Type Distribution", fontweight="bold")
        ax.set_xlabel("Provider Type"); ax.set_ylabel("Count")
        plt.xticks(rotation=45)

    elif chart == "Quantity by Provider Type":
        food.groupby("provider_type")["quantity"].sum().sort_values(ascending=False).plot(
            kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Total Quantity by Provider Type", fontweight="bold")
        ax.set_xlabel("Provider Type"); ax.set_ylabel("Total Quantity")
        plt.xticks(rotation=45)

    elif chart == "Claims by Food Type":
        full_data.groupby("food_type")["claim_id"].count().sort_values(ascending=False).plot(
            kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Number of Claims by Food Type", fontweight="bold")
        ax.set_xlabel("Food Type"); ax.set_ylabel("Total Claims")
        plt.xticks(rotation=45)

    elif chart == "Monthly Claim Trends":
        claims["timestamp"] = pd.to_datetime(claims["timestamp"])
        monthly = claims.dropna(subset=["timestamp"])
        monthly = monthly.groupby(monthly["timestamp"].dt.to_period("M"))["claim_id"].count()
        monthly.index = monthly.index.astype(str)
        monthly.plot(kind="line", marker="o", color=COLORS[1], ax=ax)
        ax.set_title("Monthly Claim Trends", fontweight="bold")
        ax.set_xlabel("Month"); ax.set_ylabel("Total Claims")
        plt.xticks(rotation=45)

    elif chart == "Top 10 Cities by Food Availability":
        food.groupby("location")["quantity"].sum().sort_values(ascending=False).head(10).plot(
            kind="barh", color=COLORS[2], edgecolor="black", ax=ax)
        ax.set_title("Top 10 Cities by Food Availability", fontweight="bold")
        ax.set_xlabel("Total Quantity"); ax.set_ylabel("City")

    elif chart == "Expiry Status Breakdown":
        food["expiry_date"] = pd.to_datetime(food["expiry_date"])
        today = pd.Timestamp.today()
        food["expiry_status"] = food["expiry_date"].apply(
            lambda x: "Expired" if pd.notna(x) and x < today
            else ("Expiring Soon" if pd.notna(x) and x <= today + pd.Timedelta(days=7) else "Fresh"))
        food["expiry_status"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Food Expiry Status", fontweight="bold")
        ax.set_xlabel("Status"); ax.set_ylabel("Count")
        plt.xticks(rotation=0)

    elif chart == "Heatmap: Food Type vs Meal Type":
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot = full_data.groupby(["food_type", "meal_type"])["claim_id"].count().unstack(fill_value=0)
        sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd", ax=ax)
        ax.set_title("Heatmap: Claims by Food Type and Meal Type", fontweight="bold")

    elif chart == "Claim Status by Food Type":
        fig, ax = plt.subplots(figsize=(12, 6))
        status_food = full_data.groupby(["food_type", "status"])["claim_id"].count().unstack(fill_value=0)
        status_food.plot(kind="bar", color=COLORS, edgecolor="black", ax=ax)
        ax.set_title("Claim Status by Food Type", fontweight="bold")
        ax.set_xlabel("Food Type"); ax.set_ylabel("Count")
        plt.xticks(rotation=45)
        ax.legend(title="Status")

    elif chart == "Scatter: Quantity vs Claims":
        provider_summary = full_data.groupby("provider_id").agg(
            total_quantity=("quantity", "sum"),
            total_claims=("claim_id", "count")).reset_index()
        ax.scatter(provider_summary["total_quantity"], provider_summary["total_claims"],
                   alpha=0.6, color=COLORS[3], edgecolors="black")
        ax.set_title("Quantity Donated vs Claims Received", fontweight="bold")
        ax.set_xlabel("Total Quantity Donated"); ax.set_ylabel("Total Claims")

    plt.tight_layout()
    st.pyplot(fig)


# =====================================================================
# PAGE 5: CRUD OPERATIONS
# =====================================================================
elif page == "✏️ CRUD Operations":
    st.title("✏️ CRUD Operations")
    st.markdown("Add, update, or delete records in the database.")

    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])
    operation = st.radio("Operation", ["➕ Add Record", "✏️ Update Record", "🗑️ Delete Record"])

    # ---- ADD ----
    if operation == "➕ Add Record":
        st.subheader(f"Add New Record to {table}")

        if table == "providers":
            pid = st.number_input("Provider ID", min_value=1, step=1)
            name = st.text_input("Name")
            ptype = st.text_input("Type")
            address = st.text_input("Address")
            city = st.text_input("City")
            contact = st.text_input("Contact")
            if st.button("Add Provider"):
                execute_statement(
                    "INSERT INTO providers VALUES (:id, :name, :type, :address, :city, :contact)",
                    {"id": pid, "name": name, "type": ptype, "address": address, "city": city, "contact": contact}
                )
                st.success("Provider added successfully!")

        elif table == "receivers":
            rid = st.number_input("Receiver ID", min_value=1, step=1)
            name = st.text_input("Name")
            rtype = st.text_input("Type")
            city = st.text_input("City")
            contact = st.text_input("Contact")
            if st.button("Add Receiver"):
                execute_statement(
                    "INSERT INTO receivers VALUES (:id, :name, :type, :city, :contact)",
                    {"id": rid, "name": name, "type": rtype, "city": city, "contact": contact}
                )
                st.success("Receiver added successfully!")

        elif table == "food_listings":
            fid = st.number_input("Food ID", min_value=1, step=1)
            fname = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=0, step=1)
            expiry = st.date_input("Expiry Date")
            pid = st.number_input("Provider ID", min_value=1, step=1)
            ptype = st.text_input("Provider Type")
            location = st.text_input("Location")
            food_type = st.text_input("Food Type")
            meal_type = st.text_input("Meal Type")
            if st.button("Add Food Listing"):
                execute_statement(
                    """INSERT INTO food_listings VALUES
                    (:fid, :fname, :qty, :expiry, :pid, :ptype, :location, :food_type, :meal_type)""",
                    {"fid": fid, "fname": fname, "qty": qty, "expiry": expiry,
                     "pid": pid, "ptype": ptype, "location": location,
                     "food_type": food_type, "meal_type": meal_type}
                )
                st.success("Food listing added successfully!")

        elif table == "claims":
            cid = st.number_input("Claim ID", min_value=1, step=1)
            fid = st.number_input("Food ID", min_value=1, step=1)
            rid = st.number_input("Receiver ID", min_value=1, step=1)
            status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
            timestamp = st.date_input("Date")
            if st.button("Add Claim"):
                execute_statement(
                    'INSERT INTO claims VALUES (:cid, :fid, :rid, :status, :ts)',
                    {"cid": cid, "fid": fid, "rid": rid, "status": status, "ts": timestamp}
                )
                st.success("Claim added successfully!")

    # ---- UPDATE ----
    elif operation == "✏️ Update Record":
        st.subheader(f"Update Record in {table}")

        if table == "providers":
            pid = st.number_input("Provider ID to update", min_value=1, step=1)
            field = st.selectbox("Field to update", ["name", "type", "address", "city", "contact"])
            new_val = st.text_input("New Value")
            if st.button("Update"):
                execute_statement(
                    f"UPDATE providers SET {field} = :val WHERE provider_id = :id",
                    {"val": new_val, "id": pid}
                )
                st.success("Updated successfully!")

        elif table == "receivers":
            rid = st.number_input("Receiver ID to update", min_value=1, step=1)
            field = st.selectbox("Field to update", ["name", "type", "city", "contact"])
            new_val = st.text_input("New Value")
            if st.button("Update"):
                execute_statement(
                    f"UPDATE receivers SET {field} = :val WHERE receiver_id = :id",
                    {"val": new_val, "id": rid}
                )
                st.success("Updated successfully!")

        elif table == "food_listings":
            fid = st.number_input("Food ID to update", min_value=1, step=1)
            field = st.selectbox("Field to update", ["food_name", "quantity", "food_type", "meal_type", "location"])
            new_val = st.text_input("New Value")
            if st.button("Update"):
                execute_statement(
                    f"UPDATE food_listings SET {field} = :val WHERE food_id = :id",
                    {"val": new_val, "id": fid}
                )
                st.success("Updated successfully!")

        elif table == "claims":
            cid = st.number_input("Claim ID to update", min_value=1, step=1)
            new_status = st.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
            if st.button("Update Status"):
                execute_statement(
                    "UPDATE claims SET status = :val WHERE claim_id = :id",
                    {"val": new_status, "id": cid}
                )
                st.success("Status updated successfully!")

    # ---- DELETE ----
    elif operation == "🗑️ Delete Record":
        st.subheader(f"Delete Record from {table}")
        st.warning("⚠️ This action is permanent and cannot be undone.")

        id_col = {"providers": "provider_id", "receivers": "receiver_id",
                  "food_listings": "food_id", "claims": "claim_id"}[table]
        record_id = st.number_input(f"Enter {id_col} to delete", min_value=1, step=1)

        if st.button("🗑️ Delete", type="primary"):
            execute_statement(
                f"DELETE FROM {table} WHERE {id_col} = :id",
                {"id": record_id}
            )
            st.success(f"Record {record_id} deleted from {table}!")