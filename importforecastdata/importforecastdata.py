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

S3BucketName=os.environ['S3BucketName']

s3_client = boto3.client('s3')

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

def onObjectCreate(event, context):
   if event is None:
       return
   for record in event['Records']:
       payload=record["body"]
       print(str(payload))
    #upsertDataImportJob(client, DataSetArn, S3Url)
