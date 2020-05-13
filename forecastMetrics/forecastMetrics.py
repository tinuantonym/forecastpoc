import os
import io
import json
import boto3
import random
import csv
import botocore
from datetime import date
from datetime import datetime
from datetime import timedelta
from urllib.parse import unquote_plus
import vars

S3BucketName=os.environ['S3BucketName']
s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')
s3_resource = boto3.resource('s3')

def tranformDateToString(date):
    return date.strftime("%Y-%m-%d")

def isSameDate(date1, date2):
    if(tranformDateToString(date1)==tranformDateToString(date2)):
        return True
    return False

def transformDatetimeStringFormat(datestring):
    return datestring[0:4]+"-"+datestring[4:6]+"-"+datestring[6:8]


def getDateFromString(dateString):
    return datetime.strptime(dateString, "%Y-%m-%d").date()


def getRowValueForTheDay(currentDay,item,cellName):
    currentDayString=tranformDateToString(currentDay)

    # if currentDayString has no data
    if (currentDayString not in vars.RawData):
        if (isSameDate(currentDay, vars.StartDate)):
            return 0
        else:
            return getRowValueForTheDay(currentDay-timedelta(days=1),item,cellName)

    # Only fill the target value ; but for related will backfill
    if (not (item in vars.RawData[currentDayString])):
      if(cellName=="targetValue"):
         return None
      if (isSameDate(currentDay, vars.StartDate)):
          return 0
      else:
          return getRowValueForTheDay(currentDay-timedelta(days=1),item,cellName)

    if ((not (cellName in vars.RawData[currentDayString][item])) or (vars.RawData[currentDayString][item][cellName] is None) or (vars.RawData[currentDayString][item][cellName]=="")):
            return getRowValueForTheDay(currentDay-timedelta(days=1),item,cellName)
    else:
            return vars.RawData[tranformDateToString(currentDay)][item][cellName]

def getCurrentDayRealData(currentDay):
    targetfile='target_'+tranformDateToString(currentDay)+".csv"
    download_path='/tmp/'+targetfile
    try:
        s3_client.download_file('racliu-forecast-demo-ap-southeast-2','covid-19-daily/'+targetfile,download_path)
        inputFile=open(download_path,'r')
        readerObj=csv.reader(inputFile)
        next(readerObj)
        currentDayRealData={}
        for row in readerObj:
           currentDayRealData[row[1]]=row[2]
        return currentDayRealData
    except:
        return None
def getTimestampByDate(currentDay):
    return datetime(currentDay.year, currentDay.month, currentDay.day)

def getMetricData(metricTimeStamp, stateName, abs, p):
    MetricData={
                'MetricName': 'ForecastPerformance',
                'Dimensions': [
                    {
                        'Name': 'ModelName',
                        'Value': 'COVID19_BackFillTarget_TotalTest'
                    },
                    {
                        'Name': 'StateName',
                        'Value': stateName
                    },
                    {
                        'Name': 'P',
                        'Value': p
                    },
                ],
                'Timestamp': metricTimeStamp,
                'Value': abs,
                'Unit': 'None'
            }
    return MetricData

def publishMetrics(currentDay,currentDayRealData):
    total_dif=0
    metricDataList=[]
    metricTimeStamp=getTimestampByDate(currentDay)
    forcastPlist=["p10","p50","p90"]
    for p in forcastPlist:
      metricDataList=[]
      for item in vars.ItemList:
          if (item.upper() in currentDayRealData):
              realValue=float(currentDayRealData[item.upper()])
              forcastValue=float(vars.ForcastData[tranformDateToString(currentDay)][item.lower()][p])
              if (realValue is None or realValue==0):
                  state_abs=0
              else:
                  state_abs=(abs((forcastValue-realValue)/realValue))*100
              #print("realvalue is " + str(realValue) + "forecastvalue is " + str(forcastValue) + "; state abs is " + str(state_abs))
              total_dif=total_dif+state_abs
              # currently not need by state data for model monitor
              #metricDataList.append(getMetricData(metricTimeStamp, item, state_abs, p))
      avarage_abs=total_dif/len(vars.ItemList)
      print("averageABS is "+str(avarage_abs) +  "============for :"+tranformDateToString(currentDay) +"====for p=" +p)
      metricDataList.append(getMetricData(metricTimeStamp, "allstatesAverage", avarage_abs, p))
      putForecastMetricsData(metricDataList)

def putForecastMetricsData(metricDataList):
    response = cloudwatch_client.put_metric_data(
       Namespace="COVID19_Forecast_test",
       MetricData=metricDataList
   )
    #print("metric put response: "+ str (response))


def processForecastCSV(csvPath):
    inputFile=open(csvPath,'r')
    readerObj=csv.reader(inputFile)
    next(readerObj)

    cur_itemList=[]
    # get start and end date, get Rawdata Map
    cur_startDate=date.today()
    cur_endDate=None
    colC_name="p"
    colD_name="p"
    colE_name="p"
    for row in readerObj:
       #skip header
       if (row[0]=="item_id"):
           break
       tmp_date_string=row[1][:10]
       tmp_date=getDateFromString(tmp_date_string)
       tmp_item_string=row[0]
       if (not tmp_item_string in cur_itemList):
           cur_itemList.append(tmp_item_string)
       if (not tmp_date_string in vars.ForcastData):
           vars.ForcastData[tmp_date_string]={}
       if (not tmp_item_string in vars.ForcastData[tmp_date_string]):
           vars.ForcastData[tmp_date_string][tmp_item_string]={}
       tmp_object={}
       tmp_object["p10"]=row[2]
       tmp_object["p50"]=row[3]
       tmp_object["p90"]=row[4]
       vars.ForcastData[tmp_date_string][tmp_item_string]=tmp_object
       #process start and end date
       if(tmp_date<cur_startDate):
           cur_startDate=tmp_date
       if (cur_endDate is None):
           cur_endDate=tmp_date
       if(tmp_date>cur_endDate):
           cur_endDate=tmp_date
    inputFile.close()
    vars.StartDate=cur_startDate
    vars.EndDate=cur_endDate
    vars.ItemList=cur_itemList


# trigger by scheduler and loop through all the forecast
def onEventHandler(event, context):
    response = s3_client.list_objects_v2(
    Bucket=S3BucketName,
    Prefix='covid-19-ml-forecast'
    )
    for content in response["Contents"]:
        key=content["Key"]
        print("========checking " + key)
        if ((not ".csv" in key) or (not "forecast" in key)):
            continue
        fileName=key.split("/")[-1]
        download_path="/tmp/"+fileName
        s3_client.download_file(S3BucketName, key, download_path)
        processForecastCSV(download_path)
        currentDay=vars.StartDate
        hasNonePublishedMetrics=False
        while (currentDay<=vars.EndDate):
              currentDayRealData=getCurrentDayRealData(currentDay)
              if (currentDayRealData is None):
                  print("no real data for "+ tranformDateToString(currentDay))
                  hasNonePublishedMetrics=True
              else:
                  print (tranformDateToString(currentDay) + " has forcast data and real data ")
                  publishMetrics(currentDay,currentDayRealData)
                  currentDayMetricsPublished=True
              currentDay=currentDay+timedelta(days=1)
        # move file
        if(not hasNonePublishedMetrics):
            source=S3BucketName+"/"+key
            print("all published, going to archive :" + source + "; with file name " + fileName)
            s3_resource.Object(S3BucketName,'archived/'+fileName).copy_from(CopySource=source)
            s3_resource.Object(S3BucketName,key).delete()
