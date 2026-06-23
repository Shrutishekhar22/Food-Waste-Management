"""
Food Wastage Management System 
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

connection_string = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="Postgresql@0322",
    host="localhost",
    port=5432,
    database="foodwastagedb"
)
engine = create_engine(connection_string)

PROVIDERS_CSV = "providers_data.csv"
RECEIVERS_CSV = "receivers_data.csv"
FOOD_LISTINGS_CSV = "food_listings_data.csv"
CLAIMS_CSV = "claims_data.csv"


def load_providers():
    df = pd.read_csv(PROVIDERS_CSV)
    df.columns = [c.strip().lower() for c in df.columns]
    df["address"] = df["address"].fillna("Not Provided")
    df["contact"] = df["contact"].fillna("Not Provided")
    df.to_sql("providers", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into providers")


def load_receivers():
    df = pd.read_csv(RECEIVERS_CSV)
    df.columns = [c.strip().lower() for c in df.columns]
    df["contact"] = df["contact"].fillna("Not Provided")
    df.to_sql("receivers", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into receivers")


def load_food_listings():
    df = pd.read_csv(FOOD_LISTINGS_CSV)
    df.columns = [c.strip().lower() for c in df.columns]
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    valid_providers = pd.read_sql("SELECT provider_id FROM providers", engine)["provider_id"]
    before = len(df)
    df = df[df["provider_id"].isin(valid_providers)]
    after = len(df)
    if before != after:
        print(f"Dropped {before - after} food_listings rows with unknown provider_id")

    df.to_sql("food_listings", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into food_listings")


def load_claims():
    df = pd.read_csv(CLAIMS_CSV)
    df.columns = [c.strip().lower() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["status"] = df["status"].fillna("Unknown")

    valid_food_ids = pd.read_sql("SELECT food_id FROM food_listings", engine)["food_id"]
    valid_receiver_ids = pd.read_sql("SELECT receiver_id FROM receivers", engine)["receiver_id"]

    before = len(df)
    df = df[df["food_id"].isin(valid_food_ids) & df["receiver_id"].isin(valid_receiver_ids)]
    after = len(df)
    if before != after:
        print(f"Dropped {before - after} claims rows with unknown food_id/receiver_id")

    df.to_sql("claims", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into claims")


def verify_counts():
    print("\n--- Row counts in database ---")
    with engine.connect() as conn:
        for table in ["providers", "receivers", "food_listings", "claims"]:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table}: {count} rows")


if __name__ == "__main__":
    load_providers()
    load_receivers()
    load_food_listings()
    load_claims()
    verify_counts()