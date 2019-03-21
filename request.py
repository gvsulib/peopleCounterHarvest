#!/usr/bin/env python3

import requests
import json
import datetime
import credentials

#start generating date data for current reporting period ( previous 7 days)
today = datetime.datetime.now()

#This is run every monday and gets the data for the last week
lastWeek = today + datetime.timedelta(-7)


startDate = lastWeek.strftime("%Y-%m-%d")
endDate = today.strftime("%Y-%m-%d")

#get all data for all times, 60-minute increments
startTime = "00:00"
endTime = "23:00"
interval = "60"

r = requests.get('https://api.axper.com/api/TrafficReport/GetTrafficData', params = {'Apikey':f'{credentials.apiKey}','DateFrom':f'{startDate}','DateTo':f'{endDate}','HourMinuteFrom':f'{startTime}','HourMinuteTo':f'{endTime}', 'IntervalInMinutes':f'{interval}'})
# start changing the string into an array for writing

#print(r.url)

lines = r.text.split("\n")
# get ris of the first line, which is field identifiers
lines.pop(0)

finalArray = []
innerArray = []

totalCount = 0

#first extract and format all usable data
for row in lines:
    data = {}
    #remove carriage returns
    row = row.replace("\r","")
    #split the csv row into individual elements for processing
    row = row.split(",")
    if row[0] != '':
        row.pop(0)
        #replacename with the numberic code for that location in libinsight
        if row[0] == "Mary Idema Pew Library":
            
            data["gate_id"] = "10" 
            totalCount += 1
        elif row[0] == "Steelcase Library":
            data["gate_id"] = "9"
            totalCount += 1
        elif row[0] == "Exhibition Room":
            data["gate_id"] = "12"
        elif row[0] == "Seidman House Library":
            data["gate_id"] = "11"
            #skip any data with a name we don't recognize
        else:
            continue

        #format the rest of the data
        data["date"] = row[1]
        data["gate_start"] = row[2]
        data["gate_end"] = row[3]
        innerArray.append(data)
            

count = 0
totalCount = 0
tempArray = []
length = len(innerArray)

#libinsight will only upload data in batches of 500 records.  So I need a json array in blocks of 500 or less.
#roll through the formated data, breaking it into separate arrays of 500 records (or less if there's less than 500 remaining), 
# and transforming it to json
for row in innerArray:
    tempArray.append(row)
    count += 1
    totalCount +=1
    if len(tempArray) == 500 or totalCount == length:
        count = 0
        finalArray.append(json.dumps(tempArray))
        tempArray=[]
        

print(str(totalCount) + " records processed.")

#now iterate through the final array of records, uploading each batch of 500
#check the http status code and the response from the libinsight API to make sure 
#the ingest was successful.  If it wasn't, shut down.
for payload in finalArray:

    r = requests.post('https://gvsu.libinsight.com/add.php', params = {'wid':'27','type':'5','token':f'{credentials.token}','data':'json'}, data=payload)
    if r.status_code != 200:
        print(f"problem contacting libinsight server, terminating. Status Code {r.status_code} \n")
        exit

    json_data = json.loads(r.text)

    if json_data["response"] != 1:
        print("Libinsight reports error ingesting data, terminating.")
        exit

print("Data migration complete!")