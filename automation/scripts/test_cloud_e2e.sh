export KINESIS_STREAM_INPUT="stg_ride_events-risk-score-mlops"
export KINESIS_STREAM_OUTPUT="stg_ride_predictions-risk-score-mlops"

aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
            "cust": {
                "riskperformance": 0,
                "externalriskestimate": 57,
                "msinceoldesttradeopen": 176,
                "msincemostrecenttradeopen": 4,
                "averageminfile": 87,
                "numsatisfactorytrades": 18,
                "numtrades60ever2derogpubrec": 0,
                "numtrades90ever2derogpubrec": 0,
                "percenttradesneverdelq": 89,
                "msincemostrecentdelq": 2,
                "maxdelq2publicreclast12m": 4,
                "maxdelqever": 6,
                "numtotaltrades": 18,
                "numtradesopeninlast12m": 1,
                "percentinstalltrades": 56,
                "msincemostrecentinqexcl7days": 4,
                "numinqlast6m": 1,
                "numinqlast6mexcl7days": 1,
                "netfractionrevolvingburden": 93,
                "netfractioninstallburden": 72,
                "numrevolvingtradeswbalance": 5,
                "numinstalltradeswbalance": 3,
                "numbank2natltradeswhighutilization": 1,
                "percenttradeswbalance": 100
            },
            "cust_id": 19
        }'
```
#SHARD_ITERATOR=$(aws kinesis get-shard-iterator --shard-id ${SHARD_ID} --shard-iterator-type TRIM_HORIZON --stream-name ${KINESIS_STREAM_OUTPUT} --query 'ShardIterator')

#aws kinesis get-records --shard-iterator $SHARD_ITERATOR
