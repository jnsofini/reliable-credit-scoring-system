import requests
import json


customers = {
   "records":[
      {
         "cust":{
            "ExternalRiskEstimate":79,
            "AverageMInFile":68,
            "NumSatisfactoryTrades":27,
            "PercentTradesNeverDelq":100,
            "PercentInstallTrades":36,
            "MSinceMostRecentInqexcl7days":0,
            "NetFractionRevolvingBurden":1
         },
         "cust_id":2
      },
      {
         "cust":{
            "ExternalRiskEstimate":80,
            "AverageMInFile":66,
            "NumSatisfactoryTrades":5,
            "PercentTradesNeverDelq":90,
            "PercentInstallTrades":46,
            "MSinceMostRecentInqexcl7days":0,
            "NetFractionRevolvingBurden":1
         },
         "cust_id":3
      }
   ]
}

url = "http://localhost:8002/predict"  # fast_api_url
# url = "http://localhost:9696/predict"
# url = "https://credit-scoring.fly.dev/predict"  # fast_api_url_fly
response = requests.post(url, json=customers)
print(json.dumps(response.json(), indent=6))
# print(response.json())
