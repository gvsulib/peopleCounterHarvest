#!/usr/bin/env python3

import requests
import json
import datetime
import json



apiKey = "a475a0804c3c4f09B08ac7a339ba5383"


today = datetime.datetime.now()

#This is run every monday and gets the data for the last week
lastMonth = today + datetime.timedelta(-32)


startDate = twoWeeksAgo.strftime("%Y-%m-%d")
endDate = today.strftime("%Y-%m-%d")

startTime = "00:00"
endTime = "24:00"
interval = "60"

r = requests.get('https://api.axper.com/api/TrafficReport/GetTrafficData', params = {'Apikey':f'{apiKey}','DateFrom':f'{startDate}','DateTo':f'{endDate}','HourMinuteFrom':f'{startTime}','HourMinuteTo':f'{endTime}', 'IntervalInMinutes':f'{interval}'})
# start changing the string into an array for writing
lines = r.text.split("\n")
lines.pop(0)

finalArray = []
innerArray = []

totalCount = 0

#first extract and format all usable data
for row in lines:
    data = {}
    #remove carriage returns
    row = row.replace("\r","")
    row = row.split(",")
    if row[0] != '':
        row.pop(0)
        if row[0] == "Mary Idema Pew Library":
            
            data["gate_id"] = "10"
            data["date"] = row[1]
            data["gate_start"] = row[2]
            data["gate_end"] = row[3]
            innerArray.append(data)
            
            totalCount += 1
        elif row[0] == "Steelcase Library":
            data["gate_id"] = "9"
            data["date"] = row[1]
            data["gate_start"] = row[2]
            data["gate_end"] = row[3]
            innerArray.append(data)
            
            totalCount += 1
        else:
            continue

count = 0
totalCount = 0
tempArray = []
length = len(innerArray)


for row in innerArray:
    tempArray.append(row)
    count += 1
    totalCount +=1
    if len(tempArray) == 500 or totalCount == length:
        count = 0
        finalArray.append(json.dumps(tempArray))
        tempArray=[]
        




#print(str(finalArray))

for payload in finalArray:

   r = requests.post('https://gvsu.libinsight.com/add.php', params = {'wid':'27','type':'5','token':'6e4058071fb07daafd779096c5ce7f02','data':'json'}, data=payload)
  