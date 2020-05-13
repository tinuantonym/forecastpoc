


def hasLongRunTask_deleteFailedDataImport(client, datasetArn)
   hasLongRunTask=False
   response = client.list_dataset_import_jobs(
    Filters=[
            {
                'Key': 'DatasetArn',
                'Value': datasetArn,
                'Condition': 'IS'
            },
            {
                'Key': 'Status',
                'Value': 'CREATE_FAILED',
                'Condition': 'IS'
            }
            ]
        )
   failedJobs=response["DatasetImportJobs"]
   for failedjob in failedJobs:
       jobArn=failedjob["DatasetImportJobArn"]
       response = client.delete_dataset_import_job(
           DatasetImportJobArn=jobArn
        )
       print("failed job " + jobArn + " delete request got the response " + str (response))
       hasLongRunTask=False
       # delete one at a time
       break
   return hasLongRunTask
