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

def writeDataAndUpload(currentDay, dataListForCurrentTimePoint):

    # only re-write recent 5 day's data (ignore redundant historical data)
    numOfDays=abs((vars.EndDate - currentDay).days)
    if(numOfDays>3):
        return
    targetFileName="target_"+tranformDateToString(currentDay)+".csv"
    relatedFileName="related_"+tranformDateToString(currentDay)+".csv"

    targetFile = open("/tmp/"+targetFileName,'w',newline='')
    csvWriterTarget = csv.writer(targetFile)
    relatedFile = open("/tmp/"+relatedFileName,'w',newline='')
    csvWriterRelated = csv.writer(relatedFile)

    for item in dataListForCurrentTimePoint:
        targetRow=[item[0],item[1],item[2]]
        relatedRow=[item[0],item[1],item[3]]
        csvWriterTarget.writerow(targetRow)
        csvWriterRelated.writerow(relatedRow)
    targetFile.close()
    relatedFile.close()
    s3_client.upload_file("/tmp/"+targetFileName, S3BucketName, "covid-19-daily/"+targetFileName)
    s3_client.upload_file("/tmp/"+relatedFileName, S3BucketName, "covid-19-daily/"+relatedFileName)

# this will also fill empty data for rawdata
def generateDataForCurrentDay(currentDay):
    dataListForCurrentTimePoint=[]
    for item in vars.ItemList:
        rowItemForTheDay=[]
        rowItemForTheDay.append(tranformDateToString(currentDay))
        rowItemForTheDay.append(item)
        rowItemForTheDay.append(getRowValueForTheDay(currentDay,item,"targetValue"))
        rowItemForTheDay.append(getRowValueForTheDay(currentDay,item,"relatedValue1"))
        dataListForCurrentTimePoint.append(rowItemForTheDay)
    return dataListForCurrentTimePoint


def processRawCSV(rawDataLocalPath):
    inputFile=open(rawDataLocalPath,'r')
    readerObj=csv.reader(inputFile)
    next(readerObj)

    cur_itemList=[]
    # get start and end date, get Rawdata Map
    cur_startDate=date.today()
    cur_endDate=None
    for row in readerObj:
       tmp_date_string=transformDateStringFormat(row[0])
       tmp_date=getDateFromString(tmp_date_string)
       tmp_item_string=row[1]
       if (not tmp_item_string in cur_itemList):
           cur_itemList.append(tmp_item_string)
       if (not tmp_date_string in vars.RawData):
           vars.RawData[tmp_date_string]={}
       if (not tmp_item_string in vars.RawData[tmp_date_string]):
           vars.RawData[tmp_date_string][tmp_item_string]={}
       tmp_object={}
       tmp_object["targetValue"]=row[2]
       tmp_object["relatedValue1"]=row[17]
       vars.RawData[tmp_date_string][tmp_item_string]=tmp_object
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

def updateFullHistryItem(currentDayItems):
    for item in currentDayItems:
        vars.FullHistoryList.append(item)

def writeFullHistoryAndUpload():
    FullHistoryTargetFileName="history.target."+tranformDateToString(vars.StartDate)+"."+ tranformDateToString(vars.EndDate)+".csv"
    FullHistoryRelatedFileName="history.related."+tranformDateToString(vars.StartDate)+"."+ tranformDateToString(vars.EndDate)+".csv"

    targetFile = open("/tmp/"+FullHistoryTargetFileName,'w',newline='')
    csvWritertarget = csv.writer(targetFile)
    relatedFile = open("/tmp/"+FullHistoryRelatedFileName,'w',newline='')
    csvWriterRelated = csv.writer(relatedFile)
    for item in vars.FullHistoryList:
        targetRow=[item[0],item[1],item[2]]
        relatedRow=[item[0],item[1],item[3]]
        csvWritertarget.writerow(targetRow)
        csvWriterRelated.writerow(relatedRow)

    simulateStartDate=vars.EndDate+timedelta(days=1)
    simulateEndDate=vars.EndDate+timedelta(days=vars.ForcastDays)
    currentDay=simulateStartDate
    while(currentDay<=simulateEndDate):
       for item in vars.ItemList:
          rowItemForTheDay=[]
          rowItemForTheDay.append(tranformDateToString(currentDay))
          rowItemForTheDay.append(item)
          rowItemForTheDay.append(getRowValueForTheDay(vars.EndDate,item,"relatedValue1"))
          csvWriterRelated.writerow(rowItemForTheDay)
       currentDay=currentDay+timedelta(days=1)

    targetFile.close()
    relatedFile.close()
    s3_client.upload_file("/tmp/"+FullHistoryTargetFileName, S3BucketName, "covid-19-ml-history/"+FullHistoryTargetFileName)
    s3_client.upload_file("/tmp/"+FullHistoryRelatedFileName, S3BucketName, "covid-19-ml-history/"+FullHistoryRelatedFileName)



def onEventHandler(event, context):
  if event is None:
      return
  print("entry!!!=== event: " + str(event))
  tmpkey=tranformDateToString(date.today())+".csv"

  #download raw data and process
  download_path = '/tmp/'+tmpkey
  s3_client.download_file('covid19-lake', 'rearc-covid-19-testing-data/csv/states_daily/states_daily.csv', download_path)
  s3_client.upload_file(download_path, S3BucketName, "covid-19-raw/states_daily_raw"+tmpkey)

  processRawCSV(download_path)

  currentDay=vars.StartDate
  print ("start from " + str(vars.StartDate))
  print ("ending at " + str(vars.EndDate))
  totalDays=abs((vars.EndDate - vars.StartDate).days)+1
  totalItemNum=len(vars.ItemList)
  totalFiles=totalDays*2
  print("Total Days "+str(totalDays)+ " ; Total Item Number " + str(totalItemNum)+ "; total Files " + str(totalFiles))
  print (str(currentDay<=vars.EndDate))
  while (currentDay<=vars.EndDate):
      currentDayItems=generateDataForCurrentDay(currentDay)
      updateFullHistryItem(currentDayItems)
      #everyday item will only used for metrics
      writeDataAndUpload(currentDay,currentDayItems)
      currentDay=currentDay+timedelta(days=1)

  writeFullHistoryAndUpload()
