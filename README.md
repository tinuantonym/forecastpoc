# forecast-demo


## adding new data

Current data range
Forecast 28/Feb - 8/Apr
Related 28/Feb - 10/Apr

Forecast : 9/Apr and 10/Apr

## Problem Try to solve

- Data processing, (no missing data point, data range, )
- With related Data,(related data model )
- Model monitoring



# data processing
## Raw data
0 date, -- Transform
1 state, -- Item
2 positive, ----to forcast
3 negative, --del
4 pending, --del
5 hospitalizedCurrently,  --del
6 hospitalizedCumulative, --del
7 inIcuCurrently, --del
8 inIcuCumulative, --del
9 onVentilatorCurrently, --del
10 onVentilatorCumulative, --del
11 recovered, --del
12 hash, --delete
13 dateChecked, --delete
14 death, --del
15 hospitalized, --del
16 total, --del
17 totalTestResults -- related
18 posNeg, --del
19 fips, --del
20 deathIncrease, --del
21 hospitalizedIncrease, --del
22 negativeIncrease,--del
23 positiveIncrease, --del
24 totalTestResultsIncrease --del


forecast column 0, 1, 2
related column 0, 1, 17

s3://racliu-forecast-demo-ap-southeast-2/covid-19-ml/forecast.csv

{
	"Attributes": [
		{
			"AttributeName": "timestamp",
			"AttributeType": "timestamp"
		},
		{
			"AttributeName": "item_id",
			"AttributeType": "string"
		},
		{
			"AttributeName": "target_value",
			"AttributeType": "float"
		}
	]
}




s3://racliu-forecast-demo-ap-southeast-2/covid-19-ml/related.csv


{
	"Attributes": [
		{
			"AttributeName": "timestamp",
			"AttributeType": "timestamp"
		},
		{
			"AttributeName": "item_id",
			"AttributeType": "string"
		},
		{
			"AttributeName": "totalTestResults",
			"AttributeType": "float"
		}
	]
}
https://covid19-lake.s3.us-east-2.amazonaws.com/rearc-covid-19-testing-data/csv/states_daily/states_daily.csv
