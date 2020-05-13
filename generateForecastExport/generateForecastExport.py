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

S3BucketName = os.environ['S3BucketName']
roleArn = os.environ['ForecastExecutionRole']

forecast_client = boto3.client("forecast")


def isExportJobExistforForcast(client, forecastExportJobName, forecastArn):
    response = client.list_forecast_export_jobs( Filters=[
         {
            'Key': 'ForecastArn',
            'Value': forecastArn,
            'Condition': 'IS'
         },
     ])
    jobs = response["ForecastExportJobs"]
    for job in jobs:
        if (job["ForecastExportJobName"]==forecastExportJobName):
            if(job["Status"]=="CREATE_FAILED"):
                response = client.delete_forecast_export_job(ForecastExportJobArn=job["ForecastExportJobArn"])
            return True
    return False

def createExportJob(client,jobName, forcastArn):
    response = client.create_forecast_export_job(
    ForecastExportJobName=jobName,
    ForecastArn=forcastArn,
    Destination={
        'S3Config': {
            'Path': "s3://"+S3BucketName+"/covid-19-ml-forecast",
            'RoleArn': roleArn,
        }})

def onEventHandler(event, context):
    if event is None:
        return
    # list all the dataset Group that don't have predictor
    response = forecast_client.list_forecasts( Filters=
       [ { "Condition": "IS", "Key": "Status", "Value": "ACTIVE" }
       ])
    for forecast in response["Forecasts"]:
        if ("COVID19_2020" in forecast["ForecastName"]):
            defaultExportJob=forecast["ForecastName"]+"_export"
            if(isExportJobExistforForcast(forecast_client, defaultExportJob, forecast["ForecastArn"])):
               print("default export job :" + defaultExportJob + " already exist")
               return
            createExportJob(forecast_client,defaultExportJob,forecast["ForecastArn"])
