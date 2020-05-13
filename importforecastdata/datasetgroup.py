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

dataPrefix = "PMFORECAST"
S3BucketName = os.environ['S3BucketName']
roleArn = os.environ['ForecastExecutionRole']

s3_client = boto3.client('s3')
forecast_client = boto3.client("forecast")

target_schema = {
	"Attributes": [
		{
			"AttributeName": "item_id",
			"AttributeType": "string"
		},
		{
			"AttributeName": "timestamp",
			"AttributeType": "timestamp"
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
			"AttributeName": "item_id",
			"AttributeType": "string"
		},
		{
			"AttributeName": "timestamp",
			"AttributeType": "timestamp"
		},
		{
			"AttributeName": "WindGust",
			"AttributeType": "float"
		},
		{
			"AttributeName": "WindDir_avg",
			"AttributeType": "float"
		},
		{
			"AttributeName": "RH",
			"AttributeType": "float"
		},
		{
			"AttributeName": "Rain_mm_Tot",
			"AttributeType": "float"
		},
		{
			"AttributeName": "BP_mb",
			"AttributeType": "float"
		},
		{
			"AttributeName": "AirTC_Min",
			"AttributeType": "float"
		},
		{
			"AttributeName": "AirTC_Max",
			"AttributeType": "float"
		},
		{
			"AttributeName": "AirTC_Avg",
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
                'RoleArn': roleArn
          }
        },
        TimestampFormat='yyyy-MM-dd hh:mm:ss'
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
        DataFrequency='10min',
        Schema=schema
    )
    return response["DatasetArn"]


def onEventHandler(event, context):
    if event is None:
        return
    print(event)
    sourceBucketName = event["Records"][0]["s3"]["bucket"]["name"]
    sourceObjectKey = event["Records"][0]["s3"]["object"]["key"]
    if (not "History" in sourceObjectKey):
        return
    # print(sourceObjectKey+ " is not historical data, no forecast dataset group will be created !" )
    datasetGroupName = dataPrefix
    
    s3ObjectUrl = "s3://" + sourceBucketName + "/" + sourceObjectKey
    
    # if the new job is not to upload history data , then quit the loading
    if (not "History" in s3ObjectUrl):
        print("===not History data, return" + s3ObjectUrl)
        return

    response = forecast_client.list_datasets()
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
    if ("Target" in s3ObjectUrl):
        upsertDataImportJob(forecast_client, targetDataSetArn, s3ObjectUrl)
    if ("Related" in s3ObjectUrl):
        upsertDataImportJob(forecast_client, relatedDataSetArn, s3ObjectUrl)
