import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import Tracker
import cvzone
import numpy as np
from pymongo import MongoClient
from datetime import datetime, timedelta
import time

client = MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
db = client["object_detection_database"]
collection = db['Person Counting and Tracking']

model = YOLO('Model/yolov8s.pt')

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)
cap = cv2.VideoCapture('video/p.mp4')

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

tracker = Tracker()
people_status = {}
counter_enter = []
counter_exit = []
list = []


# Define the years to loop through
years = range(2020, 2023)

# Initialize a datetime object starting from January 1, 2020
dt = datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0)

# enter
area_enter = [(494, 289), (505, 599), (578, 496), (530, 292)]
# exit
area_exit = [(548, 290), (600, 496), (637, 493), (574, 288)]

last_record = None
last_insert_time = datetime.now()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 500))

    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    list = []  
    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])

        c = class_list[d]
        if 'person' in c:
            list.append([x1, y1, x2, y2])

    bbox_id = tracker.update(list)
    for bbox in bbox_id:
        x3, y3, x4, y4, id = bbox
        results_enter = cv2.pointPolygonTest(np.array(area_enter, np.int32), ((x4, y4)), False)
        results_exit = cv2.pointPolygonTest(np.array(area_exit, np.int32), ((x4, y4)), False)

        if id not in people_status:
            people_status[id] = 'none'  

        if results_enter >= 0 and people_status[id] != 'exit':
            people_status[id] = 'enter'
            if id not in counter_enter:
                cv2.circle(frame, (x4, y4), 7, (0, 255, 0), -1)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 2)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 1)
                counter_enter.append(id)

        elif results_exit >= 0 and people_status[id] != 'enter':
            people_status[id] = 'exit'
            if id not in counter_exit:
                cv2.circle(frame, (x4, y4), 7, (0, 0, 255), -1)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 2)
                cvzone.putTextRect(frame, f'{id}', (x3, y3), 1, 1)
                counter_exit.append(id)

    cv2.polylines(frame, [np.array(area_enter, np.int32)], True, (0, 255, 0), 1)  # Green Enter
    cv2.polylines(frame, [np.array(area_exit, np.int32)], True, (0, 0, 255), 1)  # Red Exit

    ent = len(counter_enter)
    ext = len(counter_exit)
    total = ent + ext

    # Generate timestamp for the current year
    # dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")
    current_time = datetime.now()
    

    # Check if 10 seconds have passed since the last insertion
    if (current_time - last_insert_time).total_seconds() >= 10:
        current_record = {'person_in': ent, 'person_out': ext, 'Total Person' : total,  'Timestamp': current_time  , 'Day' : current_time.day , 'Month' : current_time.month , 'Year' : current_time.year}

        # Check if the current record is different from the last recorded data
        if current_record != last_record:
            collection.insert_one(current_record)
            last_record = current_record
            last_insert_time = current_time  # Update the last insert time

    cvzone.putTextRect(frame, f'Enter: {ent}', (50, 50), 1, 2)
    cvzone.putTextRect(frame, f'Exit: {ext}', (50, 100), 1, 2)

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
