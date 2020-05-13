'''
{'PredictorArn': 'arn:aws:forecast:ap-southeast-2:438736422320:predictor/asdfasddfa',
'PredictorName': 'asdfasddfa',
'ForecastHorizon': 2,
'PerformAutoML': True,
'EvaluationParameters': {'NumberOfBacktestWindows': 1, 'BackTestWindowOffset': 2},
'InputDataConfig':
{'DatasetGroupArn': 'arn:aws:forecast:ap-southeast-2:438736422320:dataset-group/COVID19_20200122_20200424',
'SupplementaryFeatures': [{'Name': 'holiday', 'Value': 'US'}]
},
 'FeaturizationConfig':
 {'ForecastFrequency': 'D',
 'Featurizations':
 [{'AttributeName': 'target_value',
 'FeaturizationPipeline':
 [{'FeaturizationMethodName': 'filling', 'FeaturizationMethodParameters': {'aggregation': 'sum', 'backfill': 'zero', 'frontfill': 'none', 'middlefill': 'zero'}}]},
 {'AttributeName': 'totalTestResults',
 'FeaturizationPipeline': [{'FeaturizationMethodName': 'filling',
 'FeaturizationMethodParameters': {'aggregation': 'first', 'backfill': 'none', 'frontfill': 'none', 'middlefill': 'none'}}]}]}

 , 'PredictorExecutionDetails': {'PredictorExecutions': [{'AlgorithmArn': 'arn:aws:forecast:::algorithm/ETS', 'TestWindows': [{'TestWindowStart': datetime.datetime(2020, 4, 23, 0, 0, tzinfo=tzlocal()), 'TestWindowEnd': datetime.datetime(2020, 4, 25, 0, 0, tzinfo=tzlocal()), 'Status': 'ACTIVE'}]},
{'AlgorithmArn': 'arn:aws:forecast:::algorithm/NPTS', 'TestWindows': [{'TestWindowStart': datetime.datetime(2020, 4, 23, 0, 0, tzinfo=tzlocal()), 'TestWindowEnd': datetime.datetime(2020, 4, 25, 0, 0, tzinfo=tzlocal()), 'Status': 'ACTIVE'}]}, {'AlgorithmArn': 'arn:aws:forecast:::algorithm/Prophet', 'TestWindows': [{'TestWindowStart': datetime.datetime(2020, 4, 23, 0, 0, tzinfo=tzlocal()), 'TestWindowEnd': datetime.datetime(2020, 4, 25, 0, 0, tzinfo=tzlocal()), 'Status': 'ACTIVE'}]}, {'AlgorithmArn': 'arn:aws:forecast:::algorithm/ARIMA', 'TestWindows': [{'TestWindowStart': datetime.datetime(2020, 4, 23, 0, 0, tzinfo=tzlocal()), 'TestWindowEnd': datetime.datetime(2020, 4, 25, 0, 0, tzinfo=tzlocal()), 'Status': 'ACTIVE'}]}, {'AlgorithmArn': 'arn:aws:forecast:::algorithm/Deep_AR_Plus', 'TestWindows': [{'TestWindowStart': datetime.datetime(2020, 4, 23, 0, 0, tzinfo=tzlocal()), 'TestWindowEnd': datetime.datetime(2020, 4, 25, 0, 0, tzinfo=tzlocal()), 'Status': 'ACTIVE'}]}]}, 'DatasetImportJobArns': ['arn:aws:forecast:ap-southeast-2:438736422320:dataset-import-job/COVID19_20200122_20200424_target/history_target_20200122_20200424_csv', 'arn:aws:forecast:ap-southeast-2:438736422320:dataset-import-job/COVID19_20200122_20200424_related/history_related_20200122_20200424_csv'], 'AutoMLAlgorithmArns': ['arn:aws:forecast:::algorithm/ARIMA'], 'Status': 'ACTIVE', 'CreationTime': datetime.datetime(2020, 4, 25, 14, 34, 4, 26000, tzinfo=tzlocal()), 'LastModificationTime': datetime.datetime(2020, 4, 25, 15, 41, 7, 887000, tzinfo=tzlocal()),
'ResponseMetadata':
{'RequestId': '4f92cd68-4acb-4910-a953-931a89481055', 'HTTPStatusCode': 200, 'HTTPHeaders':
{'content-type': 'application/x-amz-json-1.1', 'date': 'Sun, 26 Apr 2020 03:50:47 GMT', 'x-amzn-requestid': '4f92cd68-4acb-4910-a953-931a89481055', 'content-length': '2139', 'connection': 'keep-alive'},
'RetryAttempts': 0}
}
'''
'''
       'FeaturizationMethodParameters':
       {'aggregation': 'max', 'backfill': 'nan', 'frontfill': 'none', 'middlefill': 'nan'}}]},
       {'AttributeName': 'totalTestResults',
       'FeaturizationPipeline': [
       {'FeaturizationMethodName': 'filling',
       'FeaturizationMethodParameters': {'aggregation': 'max', 'backfill': 'nan', 'frontfill': 'none', 'middlefill': 'nan'}}]}
'''
