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
import vars

S3BucketName = os.environ['S3BucketName']
roleArn = os.environ['ForecastExecutionRole']
dataPrefix = "COVID19"

s3_client = boto3.client('s3')
forecast_client = boto3.client("forecast")

target_schema = {
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
related_schema = {
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

def tranformDateToString(date):
    return date.strftime("%Y-%m-%d")

def isSameDate(date1, date2):
    if(tranformDateToString(date1)==tranformDateToString(date2)):
        return True
    return False

def transformDateStringFormat(datestring):
    return datestring[0:4]+"-"+datestring[4:6]+"-"+datestring[6:]


def getDateFromString(dateString):
    return datetime.strptime(dateString, "%Y-%m-%d").date()


def upsertDataImportJob(client, DataSetArn, S3Url):
    # rules to use S3Url generating data import JobName
    JobName=S3Url.split("/")[-1].replace("-","").replace(".","_")
    #check if the data import job already exsit
    response = client.list_dataset_import_jobs(
    Filters=[{
            'Key': 'DatasetArn',
            'Value': DataSetArn,
            'Condition': 'IS'
            },])
    existingJobList=response["DatasetImportJobs"]
    for job in existingJobList:
        if (JobName==job["DatasetImportJobName"]):
            print("=== DatasetImportJob already exist: "+JobName)
            return
    # if the job not exist
    print ("start the data import job for " + JobName + "; for dataset "+DataSetArn+ "; with datasource " + S3Url )
    response = client.create_dataset_import_job(
        DatasetImportJobName=JobName,
        DatasetArn=DataSetArn,
        DataSource={
            'S3Config': {
                'Path': S3Url,
                'RoleArn': roleArn,
            }
        },
        TimestampFormat='yyyy-MM-dd'
    )


def isExistingDataSetGroup(client, datasetGroupName):
    response = client.list_dataset_groups(
    )
    for dsgroup in response["DatasetGroups"]:
        if (datasetGroupName == dsgroup["DatasetGroupName"]):
            return True
    return False


def upsertDataSet(existingDataSets, client, schema, datasetName, datasetType):
    for ds in existingDataSets:
        if (ds["DatasetName"] == datasetName):
            isExistingDS = True
            print("=== dataset already exist: "+datasetName)
            return ds["DatasetArn"]
    response = client.create_dataset(
        DatasetName=datasetName,
        Domain='CUSTOM',
        # DatasetType='TARGET_TIME_SERIES'|'RELATED_TIME_SERIES'|'ITEM_METADATA',
        DatasetType=datasetType,
        DataFrequency='D',
        Schema=schema
    )
    return response["DatasetArn"]


def onEventHandler(event, context):
    if event is None:
        return
    print("entry of loadforecastdata!!! ")
    body = json.loads(event['Records'][0]['body'])
    message = json.loads(body['Message'])
    # print("From SQS: " + json.dumps(message))
    sourceBucketName = message["Records"][0]["s3"]["bucket"]["name"]
    sourceObjectKey = message["Records"][0]["s3"]["object"]["key"]
    if (not "history" in sourceObjectKey):
        return
    # print(sourceObjectKey+ " is not historical data, no forecast dataset group will be created !" )

    s3ObjectUrl = "s3://" + sourceBucketName + "/" + sourceObjectKey
    startDate=getDateFromString(sourceObjectKey.split("/")[-1].split(".")[-3])
    endDate=getDateFromString(sourceObjectKey.split("/")[-1].split(".")[-2])

    datasetGroupName = dataPrefix + "_" + tranformDateToString(startDate).replace("-", "") + "_" + tranformDateToString(endDate).replace("-", "")
    # if the new job is not to upload history data , then quit the loading
    if (not "history" in s3ObjectUrl):
        print("===not history data, return" + s3ObjectUrl)
        return

    response = forecast_client.list_datasets(
    )
    existingDataSets = response["Datasets"]
    # upsert data set
    targetDataSetArn = upsertDataSet(existingDataSets, forecast_client, target_schema, datasetGroupName + "_target",
                                     "TARGET_TIME_SERIES")
    relatedDataSetArn = upsertDataSet(existingDataSets, forecast_client, related_schema, datasetGroupName + "_related",
                                      "RELATED_TIME_SERIES")

    # if dataGroup not exist, create
    if (not isExistingDataSetGroup(forecast_client, datasetGroupName)):
        response = forecast_client.create_dataset_group(
            DatasetGroupName=datasetGroupName,
            Domain='CUSTOM',
            DatasetArns=[
                targetDataSetArn, relatedDataSetArn
            ]
        )

    # load history data
    if ("target" in s3ObjectUrl):
        upsertDataImportJob(forecast_client, targetDataSetArn, s3ObjectUrl)
    if ("related" in s3ObjectUrl):
        upsertDataImportJob(forecast_client, relatedDataSetArn, s3ObjectUrl)
