import os
import io
import json
import boto3
import random
from urllib.parse import unquote_plus
import csv
from datetime import date
from datetime import datetime
from datetime import timedelta

forecast_client = boto3.client("forecast")

def isExistingDataSetGroup(client,  datasetGroupName):
    response = client.list_dataset_groups(
    )
    for dsgroup in response["DatasetGroups"]:
        if (datasetGroupName == dsgroup["DatasetGroupName"]):
            return True
    return False

def isPreditorExitInDataSetGroup(client, datasetGroupArn, preditorName):
    response = client.list_predictors( Filters=[
         {
            'Key': 'DatasetGroupArn',
            'Value': datasetGroupArn,
            'Condition': 'IS'
         },
     ])
    predictors = response["Predictors"]
    for preditor in predictors:
        if (preditor["PredictorName"]==preditorName):
            if(preditor["Status"]=="CREATE_FAILED"):
                response = client.delete_predictor(PredictorArn=preditor["PredictorArn"])
            return True
    return False

def createPredictor(client,datagroupArn,predictorName):
    response = client.create_predictor(
    PredictorName=predictorName,
    ForecastHorizon=2,
    PerformAutoML=True,
    EvaluationParameters={
        'NumberOfBacktestWindows': 1,
        'BackTestWindowOffset': 2
    },
    InputDataConfig={
        'DatasetGroupArn': datagroupArn,
        'SupplementaryFeatures': [{'Name': 'holiday', 'Value': 'US'}]
    },
    FeaturizationConfig={'ForecastFrequency': 'D',
    'Featurizations':
    [{'AttributeName': 'target_value',
    'FeaturizationPipeline':
    [{'FeaturizationMethodName': 'filling', 'FeaturizationMethodParameters': {'aggregation': 'max', 'backfill': 'nan', 'frontfill': 'none', 'middlefill': 'nan'}}]}
    ]}
)
    print(response)

def onEventHandler(event, context):
    if event is None:
        return
    # list all the dataset Group that don't have predictor
    response = forecast_client.list_dataset_groups()
    for datasetGroup in response["DatasetGroups"]:
        if ("COVID19_2020" in datasetGroup["DatasetGroupName"]):
            defaultPredictorName=datasetGroup["DatasetGroupName"]+"_Predictor"
            if(isPreditorExitInDataSetGroup(forecast_client,datasetGroup["DatasetGroupArn"],defaultPredictorName)):
               print("default predictor :" + defaultPredictorName + " already exist")
               continue
            createPredictor(forecast_client,datasetGroup["DatasetGroupArn"],defaultPredictorName)
