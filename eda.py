"""
Food Wastage Management System
EDA
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------
# 1. DATABASE CONNECTION
# ---------------------------------------------------------------------
connection_string = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="Postgresql@0322",
    host="localhost",
    port=5432,
    database="foodwastagedb"
)
engine = create_engine(connection_string)

# ---------------------------------------------------------------------
# 2. LOAD DATA FROM DATABASE
# ---------------------------------------------------------------------
providers    = pd.read_sql("SELECT * FROM providers", engine)
receivers    = pd.read_sql("SELECT * FROM receivers", engine)
food         = pd.read_sql("SELECT * FROM food_listings", engine)
claims       = pd.read_sql("SELECT * FROM claims", engine)

# Merge for combined analysis
food_claims  = food.merge(claims, on="food_id", how="left")
full_data    = food_claims.merge(providers, on="provider_id", how="left", suffixes=("", "_provider"))
full_data    = full_data.merge(receivers, on="receiver_id", how="left", suffixes=("", "_receiver"))

print("Data loaded successfully!")
print(f"Providers: {len(providers)} | Receivers: {len(receivers)} | Food Listings: {len(food)} | Claims: {len(claims)}")

# Style settings
sns.set_theme(style="whitegrid")
COLORS = sns.color_palette("Set2")

# =====================================================================
# UNIVARIATE ANALYSIS
# =====================================================================

# --- Chart 1: Food Type Distribution ---
plt.figure(figsize=(8, 5))
food["food_type"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Distribution of Food Types", fontsize=14, fontweight="bold")
plt.xlabel("Food Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart1_food_type_distribution.png", dpi=150)
plt.show()
print("Chart 1 saved: Food Type Distribution")


# --- Chart 2: Meal Type Distribution (Pie Chart) ---
plt.figure(figsize=(7, 7))
meal_counts = food["meal_type"].value_counts()
plt.pie(meal_counts, labels=meal_counts.index, autopct="%1.1f%%",
        colors=COLORS, startangle=140)
plt.title("Meal Type Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("chart2_meal_type_distribution.png", dpi=150)
plt.show()
print("Chart 2 saved: Meal Type Distribution")


# --- Chart 3: Claim Status Distribution ---
plt.figure(figsize=(7, 5))
claims["status"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Claim Status Breakdown", fontsize=14, fontweight="bold")
plt.xlabel("Status")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("chart3_claim_status.png", dpi=150)
plt.show()
print("Chart 3 saved: Claim Status Breakdown")


# --- Chart 4: Quantity Distribution (Histogram) ---
plt.figure(figsize=(8, 5))
food["quantity"].dropna().plot(kind="hist", bins=20, color=COLORS[0], edgecolor="black")
plt.title("Distribution of Food Quantity", fontsize=14, fontweight="bold")
plt.xlabel("Quantity")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("chart4_quantity_distribution.png", dpi=150)
plt.show()
print("Chart 4 saved: Quantity Distribution")


# --- Chart 5: Provider Type Distribution ---
plt.figure(figsize=(8, 5))
providers["type"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Provider Type Distribution", fontsize=14, fontweight="bold")
plt.xlabel("Provider Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart5_provider_type.png", dpi=150)
plt.show()
print("Chart 5 saved: Provider Type Distribution")


# =====================================================================
# BIVARIATE ANALYSIS
# =====================================================================

# --- Chart 6: Total Quantity Donated by Provider Type ---
plt.figure(figsize=(9, 5))
qty_by_type = food.groupby("provider_type")["quantity"].sum().sort_values(ascending=False)
qty_by_type.plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Total Quantity Donated by Provider Type", fontsize=14, fontweight="bold")
plt.xlabel("Provider Type")
plt.ylabel("Total Quantity")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart6_quantity_by_provider_type.png", dpi=150)
plt.show()
print("Chart 6 saved: Quantity by Provider Type")


# --- Chart 7: Claims by Food Type ---
plt.figure(figsize=(9, 5))
claims_by_food_type = full_data.groupby("food_type")["claim_id"].count().sort_values(ascending=False)
claims_by_food_type.plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Number of Claims by Food Type", fontsize=14, fontweight="bold")
plt.xlabel("Food Type")
plt.ylabel("Total Claims")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart7_claims_by_food_type.png", dpi=150)
plt.show()
print("Chart 7 saved: Claims by Food Type")


# --- Chart 8: Monthly Claim Trends (Line Chart) ---
plt.figure(figsize=(10, 5))
claims["timestamp"] = pd.to_datetime(claims["timestamp"])
monthly = claims.dropna(subset=["timestamp"])
monthly = monthly.groupby(monthly["timestamp"].dt.to_period("M"))["claim_id"].count()
monthly.index = monthly.index.astype(str)
monthly.plot(kind="line", marker="o", color=COLORS[1])
plt.title("Monthly Claim Trends", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Total Claims")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart8_monthly_claims.png", dpi=150)
plt.show()
print("Chart 8 saved: Monthly Claim Trends")


# --- Chart 9: Top 10 Cities by Food Availability ---
plt.figure(figsize=(10, 5))
city_food = food.groupby("location")["quantity"].sum().sort_values(ascending=False).head(10)
city_food.plot(kind="barh", color=COLORS[2], edgecolor="black")
plt.title("Top 10 Cities by Total Food Quantity Available", fontsize=14, fontweight="bold")
plt.xlabel("Total Quantity")
plt.ylabel("City")
plt.tight_layout()
plt.savefig("chart9_city_food_availability.png", dpi=150)
plt.show()
print("Chart 9 saved: Top 10 Cities by Food Availability")


# --- Chart 10: Expiry Status Breakdown ---
plt.figure(figsize=(7, 5))
food["expiry_date"] = pd.to_datetime(food["expiry_date"])
today = pd.Timestamp.today()
food["expiry_status"] = food["expiry_date"].apply(
    lambda x: "Expired" if pd.notna(x) and x < today
    else ("Expiring Soon" if pd.notna(x) and x <= today + pd.Timedelta(days=7)
    else "Fresh")
)
food["expiry_status"].value_counts().plot(kind="bar", color=COLORS, edgecolor="black")
plt.title("Food Expiry Status Breakdown", fontsize=14, fontweight="bold")
plt.xlabel("Expiry Status")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("chart10_expiry_status.png", dpi=150)
plt.show()
print("Chart 10 saved: Expiry Status Breakdown")


# =====================================================================
# MULTIVARIATE ANALYSIS
# =====================================================================

# --- Chart 11: Heatmap — Claims by Food Type and Meal Type ---
plt.figure(figsize=(10, 6))
pivot = full_data.groupby(["food_type", "meal_type"])["claim_id"].count().unstack(fill_value=0)
sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd", linewidths=0.5)
plt.title("Heatmap: Claims by Food Type and Meal Type", fontsize=14, fontweight="bold")
plt.xlabel("Meal Type")
plt.ylabel("Food Type")
plt.tight_layout()
plt.savefig("chart11_heatmap_foodtype_mealtype.png", dpi=150)
plt.show()
print("Chart 11 saved: Heatmap Food Type vs Meal Type")


# --- Chart 12: Grouped Bar — Claim Status by Food Type ---
plt.figure(figsize=(12, 6))
status_food = full_data.groupby(["food_type", "status"])["claim_id"].count().unstack(fill_value=0)
status_food.plot(kind="bar", figsize=(12, 6), color=COLORS, edgecolor="black")
plt.title("Claim Status by Food Type", fontsize=14, fontweight="bold")
plt.xlabel("Food Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.legend(title="Status")
plt.tight_layout()
plt.savefig("chart12_claim_status_by_food_type.png", dpi=150)
plt.show()
print("Chart 12 saved: Claim Status by Food Type")


# --- Chart 13: Scatter Plot — Quantity vs Claims per Provider ---
plt.figure(figsize=(9, 6))
provider_summary = full_data.groupby("provider_id").agg(
    total_quantity=("quantity", "sum"),
    total_claims=("claim_id", "count")
).reset_index()
plt.scatter(provider_summary["total_quantity"], provider_summary["total_claims"],
            alpha=0.6, color=COLORS[3], edgecolors="black")
plt.title("Quantity Donated vs Claims Received (per Provider)", fontsize=14, fontweight="bold")
plt.xlabel("Total Quantity Donated")
plt.ylabel("Total Claims Received")
plt.tight_layout()
plt.savefig("chart13_scatter_quantity_vs_claims.png", dpi=150)
plt.show()
print("Chart 13 saved: Scatter Quantity vs Claims")

