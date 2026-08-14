import pandas as pd
import pymongo


print("=== MongoDB Sensor Insert Starting ===")


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

print("Loading AEP hourly energy dataset...")

df = pd.read_csv("data/AEP_hourly.csv")

print(f"Loaded {len(df)} rows")


# ---------------------------------------------------------
# PREPROCESS DATA
# ---------------------------------------------------------

df.columns = ["datetime", "consumption"]

df["datetime"] = pd.to_datetime(df["datetime"])

# Extract hour from datetime
df["hour"] = df["datetime"].dt.hour


# ---------------------------------------------------------
# GROUP BY HOUR → AVERAGE CONSUMPTION
# ---------------------------------------------------------

print("\nCalculating hourly averages...")

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
# CONNECT TO MONGODB
# ---------------------------------------------------------

print("\nConnecting to MongoDB...")

client = pymongo.MongoClient(
    "mongodb://localhost:27017/"
)

db = client["sensor_db"]

col = db["hourly_aggregates"]

# Remove previously inserted data
col.delete_many({})

print("MongoDB connected!")


# ---------------------------------------------------------
# INSERT HOURLY AGGREGATES
# ---------------------------------------------------------

print("\nInserting hourly aggregates into MongoDB...")

for _, row in hourly_avg.iterrows():

    hour_str = f"Hour_{int(row['hour']):02d}"

    document = {
        "rowKey": f"AEP_{hour_str}",
        "hour": int(row["hour"]),
        "hourLabel": hour_str,
        "avg_mw": float(row["avg_mw"]),
        "source": "AEP",
        "unit": "MW"
    }

    col.insert_one(document)

    print(
        f"  Inserted: {hour_str} → "
        f"{row['avg_mw']} MW"
    )


# ---------------------------------------------------------
# DISPLAY RESULT
# ---------------------------------------------------------

print(
    f"\n=== Done! "
    f"{hourly_avg.shape[0]} records inserted into MongoDB ==="
)


print("\n--- MongoDB Hourly Aggregation Results ---")

results = col.find(
    {},
    {
        "_id": 0,
        "hourLabel": 1,
        "avg_mw": 1
    }
).sort("hour", 1)


for document in results:

    print(
        f"{document['hourLabel']}: "
        f"{document['avg_mw']} MW"
    )


# ---------------------------------------------------------
# CLOSE CONNECTION
# ---------------------------------------------------------

client.close()

print("\n=== MongoDB Sensor Insert Completed ===")
