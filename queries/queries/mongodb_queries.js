use sensor_db

// Count all hourly aggregate records
db.hourly_aggregates.countDocuments()

// Display hourly averages
db.hourly_aggregates.find(
    {},
    {
        hourLabel: 1,
        avg_mw: 1,
        _id: 0
    }
).sort({hour: 1})

// Find peak consumption hour
db.hourly_aggregates.find()
    .sort({avg_mw: -1})
    .limit(1)

// Display hourly averages between 08:00 and 18:00
db.hourly_aggregates.find(
    {
        hour: {
            $gte: 8,
            $lte: 18
        }
    },
    {
        hourLabel: 1,
        avg_mw: 1,
        _id: 0
    }
).sort({hour: 1})
