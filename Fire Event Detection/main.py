# # Import necessary libraries
# import cv2
# import numpy as np
# from ultralytics import YOLO
# import pymongo
# from PIL import Image
# import io
# from datetime import datetime

# # Connect to MongoDB
# client = pymongo.MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
# db = client["object_detection_database"]
# collection = db["Smoke Data"]

# # Load YOLO model
# model = YOLO('Model/best.pt')

# # Initialize frame number
# frame_number = 1

# # Path to input video
# s = r"InputVideo/fire2.mp4"

# # Open video capture object
# cap = cv2.VideoCapture(s)

# # Loop through video frames
# while True:
#     # Read frame from the video
#     success, frame = cap.read()
#     # Check if frame was successfully read
#     if not success:
#         break

#     # Resize frame
#     resized_frame = cv2.resize(frame, (480, 480), interpolation=cv2.INTER_LINEAR)

#     # Perform object detection using YOLO
#     results = model(resized_frame)
    
#      # Get current timestamp
#     dt=datetime.now()

#     # If objects are detected
#     if len(results[0]) > 0:
#         # Convert frame to bytes
#         image_bytes = io.BytesIO()
#         Image.fromarray(resized_frame).save(image_bytes, format='JPEG')

#         dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")

#         # Create document to store frame data in MongoDB
#         frame_data_document = {
#             'frame_number': frame_number,
#             'Event_Occur': 'Fire Detection',
#             'Time_stamp': dt_string,
#             'frame': image_bytes.getvalue(),
#             'image_name': f'frame{frame_number}.png' ,
#             'Day' : dt.day ,
#             'Month' : dt.month ,
#             'Year' : dt.year
#         }


#         # Insert frame data into MongoDB
#         collection.insert_one(frame_data_document)

#         # Increment frame number
#         frame_number += 1

#         # Plot annotated frame with detected objects
#         annotated_frame = results[0].plot()
#         cv2.imshow("YOLOv8 Inference", annotated_frame)

#     # Increment month and year
#     dt = dt.replace(month=dt.month % 12 + 1)
#     if dt.month == 1:
#         dt = dt.replace(year=dt.year + 1)

#     # Break the loop if 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release video capture object and close windows
# cap.release()
# cv2.destroyAllWindows()




# Import necessary libraries
import cv2
import numpy as np
from ultralytics import YOLO
import pymongo
from PIL import Image
import io
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
db = client["object_detection_database"]
collection = db["Smoke Data"]

# Load YOLO model
model = YOLO('Model/best.pt')

# Initialize frame number
frame_number = 1

# Path to input video
s = r"InputVideo/fire2.mp4"

# Open video capture object
cap = cv2.VideoCapture(s)

# Loop through video frames
while True:
    # Read frame from the video
    success, frame = cap.read()
    # Check if frame was successfully read
    if not success:
        break

    # Resize frame
    resized_frame = cv2.resize(frame, (480, 480), interpolation=cv2.INTER_LINEAR)

    # Perform object detection using YOLO
    results = model(resized_frame)
    
    # Set a custom date and time (e.g., 7 July 2023 at 12:30 PM)
    custom_datetime = datetime(year=2024, month=3, day=1, hour=12, minute=30, second=0)

    # If objects are detected
    if len(results[0]) > 0:
        # Convert frame to bytes
        image_bytes = io.BytesIO()
        Image.fromarray(resized_frame).save(image_bytes, format='JPEG')

        # Format the custom date and time as '7 July 2023'
        dt_string = custom_datetime.strftime("%d %B %Y").lstrip('0')

        # Create document to store frame data in MongoDB
        frame_data_document = {
            'frame_number': frame_number,
            'Event_Occur': 'Fire Detection',
            'Time_stamp': dt_string,
            'frame': image_bytes.getvalue(),
            'image_name': f'frame{frame_number}.png',
            'Day': custom_datetime.day,
            'Month': custom_datetime.month,
            'Year': custom_datetime.year
        }

        # Insert frame data into MongoDB
        collection.insert_one(frame_data_document)

        # Increment frame number
        frame_number += 1

        # Plot annotated frame with detected objects
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Inference", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture object and close windows
cap.release()
cv2.destroyAllWindows()
