import pandas as pd
import happybase
import pymongo

print("=== Hourly Sensor Aggregation Starting ===")


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

print("Loading AEP hourly energy dataset...")

df = pd.read_csv("data/AEP_hourly.csv")

print(f"Loaded {len(df)} rows")
print("Columns:", df.columns.tolist())

print("\nSample:")
print(df.head(3))


# ---------------------------------------------------------
# RENAME COLUMNS
# ---------------------------------------------------------

df.columns = ["datetime", "consumption"]

df["datetime"] = pd.to_datetime(df["datetime"])

# Extract hour from datetime
df["hour"] = df["datetime"].dt.hour

# Extract date
df["date"] = df["datetime"].dt.date.astype(str)


# ---------------------------------------------------------
# GROUP BY HOUR → AVERAGE CONSUMPTION
# ---------------------------------------------------------

print("\nCalculating hourly averages (GROUP BY hour)...")

hourly_avg = (
    df.groupby("hour")["consumption"]
    .mean()
    .reset_index()
)

hourly_avg.columns = ["hour", "avg_mw"]

hourly_avg["avg_mw"] = hourly_avg["avg_mw"].round(2)


print("\nHourly Averages:")
print(hourly_avg.to_string(index=False))


# ---------------------------------------------------------
# CONNECT TO HBASE
# ---------------------------------------------------------

print("\nConnecting to HBase...")

hb = happybase.Connection(
    "localhost",
    port=9091
)

table = hb.table("sensor_data")

print("HBase connected!")


# ---------------------------------------------------------
# CONNECT TO MONGODB
# ---------------------------------------------------------

print("Connecting to MongoDB...")

client = pymongo.MongoClient(
    "mongodb://localhost:27017/"
)

db = client["sensor_db"]

col = db["hourly_aggregates"]

# Clear old aggregated data
col.delete_many({})

print("MongoDB connected!")


# ---------------------------------------------------------
# INSERT HOURLY AGGREGATES INTO HBASE
# ---------------------------------------------------------

print("\nInserting hourly aggregates into HBase...")

for _, row in hourly_avg.iterrows():

    hour_str = f"Hour_{int(row['hour']):02d}"

    row_key = f"AEP_{hour_str}"

    table.put(
        row_key.encode(),
        {
            b"CF:hour": hour_str.encode(),
            b"CF:avg_mw": str(row["avg_mw"]).encode(),
            b"CF:source": b"AEP",
            b"CF:unit": b"MW"
        }
    )

    print(
        f"  HBase: {row_key} → "
        f"{row['avg_mw']} MW"
    )


# ---------------------------------------------------------
# INSERT HOURLY AGGREGATES INTO MONGODB
# ---------------------------------------------------------

print("\nInserting into MongoDB...")

for _, row in hourly_avg.iterrows():

    hour_str = f"Hour_{int(row['hour']):02d}"

    col.insert_one(
        {
            "rowKey": f"AEP_{hour_str}",
            "hour": int(row["hour"]),
            "hourLabel": hour_str,
            "avg_mw": float(row["avg_mw"]),
            "source": "AEP",
            "unit": "MW"
        }
    )


print(
    f"\nMongoDB: "
    f"{hourly_avg.shape[0]} hourly records inserted"
)


# ---------------------------------------------------------
# INSERT RAW DATA SAMPLE INTO HBASE AND MONGODB
# ---------------------------------------------------------

print("\nInserting 500 raw sensor readings...")

raw_col = db["raw_readings"]

# Clear old raw data
raw_col.delete_many({})

count = 0

for _, row in df.head(500).iterrows():

    row_key = (
        f"AEP_{row['date']}_"
        f"{int(row['hour']):02d}_"
        f"{count}"
    )

    # Insert into HBase
    table.put(
        row_key.encode(),
        {
            b"CF:datetime": str(row["datetime"]).encode(),
            b"CF:consumption": str(row["consumption"]).encode(),
            b"CF:hour": str(row["hour"]).encode(),
            b"CF:source": b"AEP"
        }
    )

    # Insert into MongoDB
    raw_col.insert_one(
        {
            "rowKey": row_key,
            "datetime": str(row["datetime"]),
            "hour": int(row["hour"]),
            "consumption": float(row["consumption"]),
            "source": "AEP"
        }
    )

    count += 1


# ---------------------------------------------------------
# FINAL OUTPUT
# ---------------------------------------------------------

print(
    f"\n=== Done! "
    f"{hourly_avg.shape[0]} hourly aggregates "
    f"+ {count} raw readings inserted ==="
)


print("\n--- HOURLY AGGREGATION RESULTS ---")

for _, row in hourly_avg.iterrows():

    label = f"Hour_{int(row['hour']):02d}"

    print(
        f"  {label}: "
        f"{row['avg_mw']} MW"
    )


# ---------------------------------------------------------
# CLOSE CONNECTIONS
# ---------------------------------------------------------

hb.close()
client.close()

print("\n=== Hourly Sensor Aggregation Completed ===")
