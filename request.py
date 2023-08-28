#!/usr/bin/env python3

import requests
import json
import datetime
import credentials
import sys
import os
import time


#set a filename for local data
#file = open("last_upload.csv", "w")

if len(sys.argv) > 1:

	if len(sys.argv) < 3:
		print("You must enter a valid start date and end date.")
		quit(1)

	#verify that the two dates provided are in the correct format
	try:
        	
		datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
	except ValueError:
		print("First date is invalid, should be YYYY-MM-DD, try again.")
		quit(1)
	try:
                
                datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
	except ValueError:
		print("Second date is invalid, should be YYYY-MM-DD, try again.")
		quit(1)

	startTime = time.mktime(datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").timetuple())
	endTime = time.mktime(datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").timetuple())

	if startTime > endTime:
		print("Start date must be before end date.")
		quit(1)

	if len(sys.argv) == 4:

		acceptableValues = [5,6,7,14,15,16]
		if int(sys.argv[3]) in acceptableValues:
			
			location = ""
			locIDNum = sys.argv[3]
			if locIDNum  == "5":
				location  = "Mary Idema Pew Library"
			elif locIDNum  == "6":
				location = "Steelcase Library"
			elif locIDNum  == "14":
               			location = "Seidman House Library"
			elif locIDNum == "7":
				location = "Frey Library"
			elif locIDNum == "15":
				location = "Exhibition Room"
			elif locIDNum == "16":
				location = "Tech Showcase"
			else:
				print("Third argument must be an 5,6,7,14,15, or 16")
				quit(1)
		else:
			print("Third argument must be an 5,6,7, 14, 15, or 16")
			quit(1)
	

	else :

		location = False
	#if we make it here, set start and end dates
	startDate = sys.argv[1]
	endDate = sys.argv[2]
else: 
	#if no arguments are supplied, get data for the last week
	#start generating date data for current reporting period ( previous 7 days)
	today = datetime.datetime.now()

	#This is run every monday and gets the data for the last week
	lastWeek = today + datetime.timedelta(-7)


	startDate = lastWeek.strftime("%Y-%m-%d")
	endDate = today.strftime("%Y-%m-%d")
	location = False
#get all data for all times, 60-minute increments
startTime = "00:00"
endTime = "23:00"
interval = "60"

data = {'Apikey':credentials.apiKey,'DateFrom':startDate,'DateTo':endDate,'HourMinuteFrom':startTime,'HourMinuteTo':endTime, 'IntervalInMinutes':interval}


print('Attempting to get data from {startDate} to {endDate}'.format(startDate=startDate, endDate=endDate))

r = requests.get('https://api.axper.com/api/TrafficReport/GetTrafficData', params = data)



if r.status_code != 200:
	print('Cannot contact peoplecounter API, error code {}'.format(r.status_code))
	quit(1)



# start changing the string into an array for writing

print(r.url)


file = open("raw_data.csv", "w+")
file.write(r.text)
file.close()
lines = r.text.split("\n")
# get rid of the first line, which is field identifiers
lines.pop(0)

finalArray = []
innerArray = []


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

	if location == False:
		
		if row[0] == "Mary Idema Pew Library":
			data["gate_id"] = "5"
		elif row[0] == "Steelcase Library":
			data["gate_id"] = "6"
		elif row[0] == "Seidman House Library":
			data["gate_id"] = "14"
            		#skip any data with a name we don't recognize
		elif row[0] == "Frey Library":
			data["gate_id"] = "7"
		
		elif row[0] == "Exhibition Room":
			data["gate_id"] = "15"
		elif row[0] == "Tech Showcase":
			data["gate_id"] = "16"
		else:
			continue
	else:
		if row[0] == location:
			
			data["gate_id"] = locIDNum
		else:
			continue
	#format the rest of the data
	data["date"] = row[1]
	data["gate_start"] = row[2]
	data["gate_end"] = row[3]


	
	innerArray.append(data)
            
#file.close()
count = 0
totalCount = 0
tempArray = []
length = len(innerArray)
#print(*innerArray, sep = ", ")  
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
	stuff = {'wid':'29','type':'5','token':credentials.token,'data':'json'}
	r = requests.post('https://gvsu.libinsight.com/add.php', params = stuff, data=payload)
	if r.status_code != 200:
        	print('problem contacting libinsight server, terminating. Status Code {} \n'.format(r.status_code))
        	quit()
	json_data = json.loads(r.text)

	if json_data["response"] != 1:
		print("Libinsight reports error ingesting data, terminating.")
		for i in json_data:
    			print("{} {}".format(i, json_data[i]))
		quit()

print("Data migration complete!")
