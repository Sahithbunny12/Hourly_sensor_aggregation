# Hourly Sensor Aggregation

A Big Data Analytics project that processes hourly electricity consumption data, calculates average power consumption for each hour of the day, and stores the aggregated results in **Apache HBase** and **MongoDB**.

## Project Overview

This project performs time-windowed aggregation on historical hourly electricity consumption data from the PJM Interconnection dataset.

The dataset contains electricity demand measurements recorded at hourly intervals, with consumption measured in Megawatts (MW).

The main objective is to calculate the average electricity consumption for each hour of the day and store the resulting 24 hourly aggregates in distributed databases for querying and analysis.

## Technologies Used

* Python
* Pandas
* Docker
* Apache HBase
* MongoDB
* HappyBase
* PyMongo
* Kaggle Dataset

## Dataset

**Dataset:** Hourly Energy Consumption

**Source:** PJM Interconnection via Kaggle

**Domain:** Energy Analytics / Power Systems

**Data Type:** Time Series

**Time Granularity:** Hourly

**Measurement Unit:** Megawatts (MW)

The dataset contains historical electricity consumption data from multiple PJM regions.

Dataset source:

https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption

## Project Workflow

```text
Hourly Energy Dataset
        |
        v
    Python + Pandas
        |
        v
Data preprocessing
        |
        v
Extract hour from timestamp
        |
        v
GROUP BY hour
        |
        v
Calculate average MW
        |
        +-------------------+
        |                   |
        v                   v
     HBase              MongoDB
        |                   |
        v                   v
   Query results       Query results
```

## Data Processing

The Python program performs the following operations:

1. Loads the AEP hourly energy consumption CSV file.
2. Renames the columns to `datetime` and `consumption`.
3. Converts the datetime column into a Pandas datetime object.
4. Extracts the hour from each timestamp.
5. Groups the records by hour.
6. Calculates the average electricity consumption for every hour.
7. Rounds the average consumption to two decimal places.
8. Stores the 24 hourly aggregate records in HBase.
9. Stores the hourly aggregates in MongoDB.
10. Stores a sample of raw sensor readings for demonstration.

## HBase Storage

The HBase table used by the project is:

```text
sensor_data
```

Column family:

```text
CF
```

Example row key:

```text
AEP_Hour_08
```

Example stored fields:

```text
CF:hour
CF:avg_mw
CF:source
CF:unit
```

## MongoDB Storage

MongoDB database:

```text
sensor_db
```

Collection:

```text
hourly_aggregates
```

Example document:

```json
{
  "rowKey": "AEP_Hour_08",
  "hour": 8,
  "hourLabel": "Hour_08",
  "avg_mw": 12345.67,
  "source": "AEP",
  "unit": "MW"
}
```

## Docker Setup

The project uses Docker to run HBase.

Start the HBase container:

```bash
docker run -d --name hbase-sensor \
-p 2182:2181 \
-p 9091:9090 \
-p 16002:16000 \
-p 16011:16010 \
dajobe/hbase
```

Verify the container:

```bash
docker ps
```

## HBase Table Setup

Open the HBase shell:

```bash
docker exec -it hbase-sensor hbase shell
```

Create the table:

```text
create 'sensor_data', 'CF'
```

Verify:

```text
list
```

## Python Setup

Check Python:

```bash
python --version
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Dataset Setup

Download the dataset from Kaggle and place the required CSV file inside:

```text
data/
```

Expected file:

```text
data/AEP_hourly.csv
```

The CSV file is intentionally excluded from this repository using `.gitignore`.

## Run the Project

From the project root:

```bash
python sensor_ingest.py
```

The program will:

* Load the energy dataset
* Calculate hourly averages
* Connect to HBase
* Connect to MongoDB
* Insert hourly aggregates
* Insert sample raw readings
* Display the hourly aggregation results

## Example HBase Queries

```text
count 'sensor_data'
```

Scan the hourly aggregates:

```text
scan 'sensor_data', {
  STARTROW => 'AEP_Hour_',
  STOPROW => 'AEP_Hour_~',
  LIMIT => 24
}
```

Retrieve a specific hour:

```text
get 'sensor_data', 'AEP_Hour_08'
```

## Example MongoDB Queries

```javascript
use sensor_db

db.hourly_aggregates.countDocuments()
```

Display hourly averages:

```javascript
db.hourly_aggregates
  .find({}, {hourLabel: 1, avg_mw: 1, _id: 0})
  .sort({hour: 1})
```

Find the peak consumption hour:

```javascript
db.hourly_aggregates
  .find()
  .sort({avg_mw: -1})
  .limit(1)
```

## Key Outcome

The project produces **24 hourly aggregate records**, representing the average electricity consumption for each hour of the day.

The aggregated data is stored in both HBase and MongoDB, allowing the results to be queried using database-specific commands.

## Applications

This type of hourly energy aggregation can be useful for:

* Electricity load forecasting
* Energy management
* Smart grid analytics
* Demand prediction
* Power generation planning
* Energy distribution
* Grid optimization


## Author

**B. Sahith**

B.Tech – Computer Science and Engineering (Data Science)

Mahatma Gandhi Institute of Technology

## Academic Project

Big Data Analytics Laboratory Project
Academic Year: 2025–2026
