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
import subtasks
import vars

forecast_client = boto3.client("forecast")
sqs_client=boto3.client("sqs")
queueurl=os.environ['S3BucketName']

def getAllDataGroupsNeedMaintain(forecast_client):
    response = forecast_client.list_dataset_groups()
    dsGroupList=[]
    for dsGroup in response["DatasetGroups"]:
        if ("COVID19_2020" in datasetGroup["DatasetGroupName"]):
            dsGroupList.append(dsGroup)
    return dsGroupList

def hasLongRunTask_checkDSStatus(client, dsArn):

def hasLongRunTask_maintainDS(client, dsArn):
    hasLongRunTask=subtasks.hasLongRunTask_deleteFailedDataImport(client, dsArn)
    if(hasLongRunTask):
        return True
    # the ds has data import and data import status is "ready"




def maintainDsGroup(forecast_client,dsgroup):
    # maintain data set
    response = forecast_client.describe_dataset_group(
        DatasetGroupArn= dsgroup["DatasetGroupArn"]
    )
    for dsArn in response["DatasetArns"]:
        ds_maintain_result=maintainDatasetsInDG(forecast_client, dsArn)
        # ds all good to go, no long period task triggerred
        if(ds_maintain_result):
            predictor_maintain_result=maintainPredictor()
            if(predictor_maintain_result):
                forcast_maintain_result=maintainForcast()
            else:
                break
        else:
            break

def getNamesByConvention(dsgName):
    names={}
    #COVID19_20200122_20200426 -->history_related_20200122_20200426_csv
    #COVID19_20200122_20200426 -->history_target_20200122_20200426_csv
    names["targetImportJob"]=dsgName.replace("COVID19","history_target")+"_csv"
    names["relatedImportJob"]=dsgName.replace("COVID19","history_related")+"_csv"

def getAllDSNeedMaintain():
    dsList=[]
    response = forecast_client.list_datasets()
    for ds in response["Datasets"]
       if ("COVID19_2020" in ds["DatasetName"]):
           dsList.append(ds)

    return dsList

def getDsStatus(dsArn):
    response = forecast_client.describe_dataset(
    DatasetArn='string'
   )



##
def onEventHandler1(event, context):
    if event is None:
        return
    dsGroupList=getAllDSNeedMaintain()
    for ds in dsGroupList:

    for dsgroup in dsGroupList:
        dsg=dsgroup["DatasetGroupName"]
        names=getNamesByConvention(dsg)

        setNamingConvention(dsg)
        maintainDsGroup(dsgroup)
        print("Dataset Group :" + dsgroup["DatasetGroupName"] + " maintainaince check done..")


# test trigger the message and start the loading
def onEventHandler(event, context):
    cmd={
      "datasetArn": "testtestarn",
      "S3Url": "urlurlurl"
          }
    response = client.send_message(
    QueueUrl='string',
    MessageBody='string',
    DelaySeconds=123,
    MessageAttributes={
        'string': {
            'StringValue': 'string',
            'BinaryValue': b'bytes',
            'StringListValues': [
                'string',
            ],
            'BinaryListValues': [
                b'bytes',
            ],
            'DataType': 'string'
        }
    },
    MessageSystemAttributes={
        'string': {
            'StringValue': 'string',
            'BinaryValue': b'bytes',
            'StringListValues': [
                'string',
            ],
            'BinaryListValues': [
                b'bytes',
            ],
            'DataType': 'string'
        }
    }
)
