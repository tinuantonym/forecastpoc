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

def getPredictorArnByName(client, datasetGroupArn, preditorName):
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
            return preditor["PredictorArn"]
    return None

def isForcastExitInDataSetGroup(client, datasetGroupArn, forecastName):
    response = client.list_forecasts( Filters=[
         {
            'Key': 'DatasetGroupArn',
            'Value': datasetGroupArn,
            'Condition': 'IS'
         },
     ])
    Forecasts = response["Forecasts"]
    for forcast in Forecasts:
        if (forcast["ForecastName"]==forecastName):
            if(forcast["Status"]=="CREATE_FAILED"):
                response = client.delete_forecast(ForecastArn=forcast["ForecastArn"])
            return True
    return False

def createForecast(client,forecastName,predictorArn):
    response = client.create_forecast(
    ForecastName= forecastName,
    PredictorArn= predictorArn,
    ForecastTypes=["0.1", "0.5", "0.9"]
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
            defaultForecastName=datasetGroup["DatasetGroupName"]+"_Forecast"
            defaultPredictorArn=getPredictorArnByName(forecast_client, datasetGroup["DatasetGroupArn"], defaultPredictorName)
            if (defaultPredictorArn is None ):
                return
            if(isForcastExitInDataSetGroup(forecast_client,datasetGroup["DatasetGroupArn"],defaultForecastName)):
               print("default predictor :" + defaultForecastName + " already exist")
               return
            createForecast(forecast_client,defaultForecastName,defaultPredictorArn)
