from os import error
from flask import Flask, render_template, request, redirect, url_for , Response , jsonify , session, send_from_directory
from pymongo import MongoClient
import ipaddress
import tabulate
import io
from PIL import Image
import datetime
from datetime import datetime
import os
import cv2
from collections import defaultdict
import base64
import uuid
import requests
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import re
import numpy as np
import calendar
import matplotlib.pyplot as plt
from collections import Counter



app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb+srv://mehernimra064:shahzadi123456789@cluster0.mgo1zg0.mongodb.net/")
# client = MongoClient("mongodb://localhost:27017")
db = client["object_detection_database"]  
collection_camera = db["camera_add"]  
collection_model = db["Add Model"]
collection_stream=db["View Stream"]
collection_smoke_fall=db['Smoke Data']
collection_Graphs=db['Graphs']
collection_Login=db['Login']
collection_SignUp=db['SignUp']
collection_PersonCountTracking=db['Person Counting and Tracking']



# Authentications

@app.route("/")
def form():
    return render_template("Form/form.html")


@app.route('/SubmitLogin', methods=["POST"])
def SubmitLogin():
    if request.method == "POST":
        login_data = {
            "Email": request.form["Email"],
            "Password": request.form["Password"],
        }

        try:
            email = login_data['Email']
            password = login_data['Password']

            if email and password:
                user = collection_SignUp.find_one({'Email': email, 'Password': password})
                if user:
                    user_name = user['Name']
                    
                    return redirect(url_for('Home_Page' , user_name=user_name))
                else:
                    return render_template('Form/form.html', error='Invalid Email or Password')
            else:
                return render_template('Form/form.html', error='Email or password cannot be empty')
        
        except Exception as e:
            return render_template('Form/form.html', error='An error occurred: {}'.format(str(e)))
        

@app.route('/SubmitSignUp' , methods=['Post'])
def SubmitSignUp():
    if request.method == "POST":
        data = {
            "Name": request.form["Name"],
            "Email": request.form["signupEmail"],
            "Password": request.form["signuppassword"],
            "ConfirmPassword": request.form["signupconfirmpassword"]
        }

        try:
            if data['Name'] != "" and data['Email'] != "":
                if data['Password'] != "" and data['ConfirmPassword'] != "":
                    if data['Password']  == data['ConfirmPassword'] :
                        collection_SignUp.insert_one(data)
                        return render_template('Form/form.html', success='Sign Up data saved successfully')
                    else:
                        return render_template('Form/form.html', success='Password and confirm password are not equal')
                else:
                    return render_template('Form/form.html', success='Confirm Password and Password Cannot Empty')
                    
            else:
                return render_template('Form/form.html', success='Email and Name Cannot Empty')
        except Exception as e:
            return render_template('Form/form.html', error='An error occurred: {}'.format(str(e)))


@app.route('/ForgetPasswordEmail.html')
def forget_Email():
    return render_template('Form/ForgetPasswordEmail.html')


@app.route('/SubmitResetEmail', methods=['POST'])
def submit_reset_email():
    if request.method == "POST":
        data ={
            "email" : request.form["Email"]
        }
        
        try:
            email = data["email"]
            if email:
                user = collection_SignUp.find_one({'Email': email})
                if user:
                    email=user["Email"]
                    return render_template('Form/ForgetPassword.html', email=email)
                else:
                    return render_template('Form/ForgetPasswordEmail.html', error='Email not found')
        except Exception as e:
            return render_template('Form/ForgetPasswordEmail.html', error='An error occurred: {}'.format(str(e)))


@app.route('/SubmitResetPassword', methods=['POST'])
def submit_reset_password():
    if request.method == "POST":
        # try:
            email = request.form["email"]
            PPassword = request.form["PPassword"]
            RNewPassword = request.form["RNewPassword"]
            
            if email is None:
                return redirect(url_for('submit_reset_email'))
            
            if PPassword == RNewPassword :
                user = collection_SignUp.find_one({'Email': email})
                if user:
                    collection_SignUp.update_one({'_id': user['_id']}, {'$set': {'Password': RNewPassword , 'ConfirmPassword': RNewPassword}})
                    return render_template('Form/form.html')
            else:
                return render_template('Form/ForgetPassword.html', email=email, error='Passwords do not match')

# Functions
def get_years_and_frames():

    camera_id = '1'
    fire_docs = collection_smoke_fall.find({})
    Time_stamp = 'Time_stamp'
    event = 'Event_Occur'

    timestamps = [document.get(Time_stamp) for document in collection_smoke_fall.find({})]
    events = [document.get(event) for document in collection_smoke_fall.find({})]

        # Extract unique years from the timestamps
    years = set()
    for timestamp in timestamps:
        year = timestamp.split()[0].split('/')[-1]  # Extract the year from the timestamp
        years.add(year)
        
        # Fetch frame_number from smoke_collection_table
    frame_numbers = [document.get('frame_number') for document in collection_smoke_fall.find({})]

    return fire_docs, years, camera_id


# Function to convert month number to month name
def convert_to_month_name(month_number):
    return calendar.month_abbr[int(month_number)]


def generate_event_graph(selected_year):

    # Filter records based on the selected year
    selected_year_records = [document for document in collection_smoke_fall.find({'year': selected_year})]

    # Fetch timestamps and events from filtered records
    timestamps = [document.get('Time_stamp') for document in selected_year_records]
    events = [document.get('Event_Occur') == 'Fire Detection' for document in selected_year_records]
    frame_numbers = [document.get('frame_number') for document in selected_year_records]

    # Calculate percentage events for the selected year
    percentage_events = calculate_percentage_events_fire(timestamps, events)

    # Extract months and percentage values
    months = list(percentage_events.keys())
    percentage_values = list(percentage_events.values())
    months = [convert_to_month_name(int(month.split('/')[1])) for month in months]

    plt.figure(figsize=(8, 6))
    bars = plt.bar(months, percentage_values, color='#4e73df')

    for bar, percentage in zip(bars, percentage_values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{percentage}', 
            ha='center', va='bottom', color='black', fontsize=10)
        
    # # Calculate the center points of the bars
    # bar_centers = [bar.get_x() + bar.get_width() / 2 for bar in bars]

    # # Plot a line connecting the center points of the bars
    # line_plot = plt.plot(bar_centers, percentage_values, marker='o', color='#004AAD')

    # Customize the appearance of the line
    # plt.setp(line_plot, linestyle='-', linewidth=2)


    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.title(f'Count of Real-time Fire Detection for {selected_year}')
    plt.grid(False)
    plt.tight_layout()

    plt.yticks(np.arange(0, max(percentage_values) + 1, 1), fontsize=10)

    # static filename
    graph_filename = f'years_barchart.png'
    graph_filepath = f'static/img/images/fire_detection/{graph_filename}'
    plt.savefig(graph_filepath)

    # Close the figure to avoid memory leaks
    # plt.close()

    # Save plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Encode the BytesIO object to base64
    graph_filename = base64.b64encode(img.getvalue()).decode()

    return graph_filename


def calculate_percentage_events_fire(timestamps, events):
    # Create a defaultdict to store events for each month
    monthly_events = defaultdict(int)

    # Iterate through timestamps and events
    for timestamp, event in zip(timestamps, events):
        # Convert the timestamp to a datetime object
        dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
        # Extract the year and month
        year_month = dt.strftime('%Y/%m')

        # Increment the count of events for the corresponding month
        monthly_events[year_month] += 1 if event else 0

    return monthly_events

# Home_Page

@app.route("/Home_Page")
def Home_Page():

        user_name = request.args.get('user_name', '')
        
        return render_template("Home_Page.html")

def calculate_counts_events_dashboard(timestamps, events):
    event_counts = {}
    for i in range(len(timestamps)):
        timestamp = timestamps[i]
        if timestamp not in event_counts:
            event_counts[timestamp] = 0
        event_counts[timestamp] += 1 if events[i] else 0

    return event_counts

# Dashboard

def generate_dashboard_graph(Time_stamp, event):
    counts_events = calculate_counts_events_dashboard(Time_stamp, event)
    timestamps = list(counts_events.keys())
    counts_events = list(counts_events.values())
    
    plt.figure(figsize=(6, 5))
    bars = plt.bar(range(len(timestamps)), counts_events, color='#4e73df')

    # Annotate each bar with its count value
    for i, count in enumerate(counts_events):
        plt.text(i, count, str(count), ha='center', va='bottom')

    plt.xticks(range(len(timestamps)), timestamps)  # Rotate x-axis labels for better readability
    plt.xlabel('Year')
    plt.ylabel('Count of Events')
    plt.title('Real-time Fall Detection Event Count')

    plt.grid(False)
    plt.tight_layout()

    Graph_save = uuid.uuid4().hex + '.png'
    plt.savefig(f'static/' + Graph_save)
    plt.close()  

    return Graph_save


@app.route("/detection_dashboard")
def detection_dashboard():
    try:
        user_name = request.args.get('user_name', '')

        fire_docs, years, camera_id = get_years_and_frames()

        Camera_IP=[document.get("Camera_IP") for document in collection_camera.find({})]
        Camera_ID=[document.get("Camera_ID") for document in collection_camera.find({})]
        Model_Name = [document.get("Model_Name") for document in collection_model.find({})]

        return render_template("detection_dashboard.html", camera_id=camera_id, user_name=user_name,
                                                fire_entities=fire_docs, years=years , Camera_IP=Camera_IP, Camera_ID=Camera_ID, Model_Name=Model_Name  )

    except Exception as e:
        return render_template("detection_dashboard.html")


@app.route('/process_selected_value', methods=['GET', 'POST'])
def process_selected_value():

    graph_filename = None

    try:
        if request.method == "POST":

            fire_docs, years, camera_id = get_years_and_frames()

            user_name = request.args.get('user_name', '')

            selected_year = int(request.form['year'])

            graph_filename = generate_event_graph(selected_year)

            Camera_ID=[document.get("Camera_ID") for document in collection_camera.find({})]
            Model_Name = [document.get("Model_Name") for document in collection_model.find({})]

            return render_template("detection_dashboard.html",
            user_name=user_name,
            fire_entities=fire_docs,
            years=years,
            Camera_ID=Camera_ID,
            Model_Name=Model_Name,
            graph_filename=graph_filename)

        else:
            return jsonify({'error': 'Invalid request method'}), 400

    except Exception as e:
        error_message = f"Error processing selected value: {str(e)}"
        return jsonify({'error': error_message}), 500

@app.route('/<camera_id>/<model>')
def get_model_camera_page(camera_id, model):

    user_name = request.args.get('user_name', '')
    fire_docs, years, camera_id = get_years_and_frames()

    Camera_ID = [document.get("Camera_ID") for document in collection_camera.find({})]
    Model_Name = [document.get("Model_Name") for document in collection_model.find({})]
    Model_Type = [document.get("Model_Type") for document in collection_model.find({})]

    # Find the model type for the requested model
    model_document = collection_model.find_one({"Model_Name": model})

    if model_document is None:
        return "Model not found", 404

    model_type = model_document.get("Model_Type")

    if model_type == "Detection":
        return render_template("detection_dashboard.html",
            model=model,
            camera_id=camera_id,
            user_name=user_name,
            fire_entities=fire_docs,
            years=years,
            Camera_ID=Camera_ID,
            Model_Name=Model_Name)

    else:
        return render_template("counting_dashboard.html",
            model=model,
            camera_id=camera_id,
            user_name=user_name,
            fire_entities=fire_docs,
            years=years,
            Camera_ID=Camera_ID,
            Model_Name=Model_Name)

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = 5
        start_index = (page - 1) * per_page

        selected_records = collection_smoke_fall.find({}).skip(start_index).limit(per_page)
        selected_records_list = [{
            "camera_id": record.get("CameraID"),
            "Event_Occur": record.get("Event_Occur"),
            "Time_stamp": record.get("Time_stamp"),
            "image_name": record.get("image_name")
        } for record in selected_records]

        return jsonify({'records': selected_records_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_model_data', methods=['GET'])
def get_model_data():
    model = request.args.get('model')
    selected_year = request.args.get('year')
    if not model:
        return jsonify({"error": "Model not found"}), 404

    fire_docs, years, camera_id = get_years_and_frames()
    graph_filename = generate_event_graph(selected_year)

    return jsonify({
        "years": list(years),
        "fire_entities": [doc for doc in fire_docs],
        "camera_id": camera_id,
        "graph_filename": graph_filename
    })

def get_years_and_frames():
    camera_id = '1'
    fire_docs = collection_smoke_fall.find({})
    timestamps = [document.get('Time_stamp') for document in fire_docs]
    events = [document.get('Event_Occur') for document in fire_docs]

    years = set()
    for timestamp in timestamps:
        year = timestamp.split()[0].split('/')[-1]
        years.add(year)
        
    frame_numbers = [document.get('frame_number') for document in fire_docs]

    return fire_docs, years, camera_id

def convert_to_month_name(month_number):
    return calendar.month_abbr[int(month_number)]

def generate_event_graph(selected_year):
    selected_year_records = [document for document in collection_smoke_fall.find({'year': selected_year})]
    timestamps = [document.get('Time_stamp') for document in selected_year_records]
    events = [document.get('Event_Occur') == 'Fire Detection' for document in selected_year_records]

    percentage_events = calculate_percentage_events_fire(timestamps, events)
    months = list(percentage_events.keys())
    percentage_values = list(percentage_events.values())
    months = [convert_to_month_name(int(month.split('/')[1])) for month in months]

    plt.figure(figsize=(8, 6))
    bars = plt.bar(months, percentage_values, color='#4e73df')

    for bar, percentage in zip(bars, percentage_values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{percentage}', ha='center', va='bottom', color='black', fontsize=10)

    plt.xlabel('Month')
    plt.ylabel('Count')
    plt.title(f'Count of Real-time Fire Detection for {selected_year}')
    plt.grid(False)
    plt.tight_layout()
    plt.yticks(np.arange(0, max(percentage_values) + 1, 1), fontsize=10)

    graph_filename = f'years_barchart.png'
    graph_filepath = f'static/img/images/fire_detection/{graph_filename}'
    plt.savefig(graph_filepath)
    plt.close()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_filename = base64.b64encode(img.getvalue()).decode()

    return graph_filename

def calculate_percentage_events_fire(timestamps, events):
    monthly_events = defaultdict(int)
    for timestamp, event in zip(timestamps, events):
        dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
        year_month = dt.strftime('%Y/%m')
        monthly_events[year_month] += 1 if event else 0
    return monthly_events


@app.route("/PersonCountIndex" , methods=["POST" , "GET"])
def PersonCountIndex():
    try:
        user_name = request.args.get('user_name', '')
        PersonCount = collection_PersonCountTracking.find({})
        
        Time_stamp = 'Timestamp'
        event = 'Event_Occur'

        timestamps = [document.get(Time_stamp) for document in collection_PersonCountTracking.find({})]
        
        years = set()  # Initialize an empty set to store years
        for timestamp in timestamps:  # Iterate through each timestamp
            if isinstance(timestamp, datetime):
                timestamp = timestamp.strftime("%Y/%m/%d %H:%M:%S")  # Convert datetime object to string
            year = timestamp.split()[0].split('/')[-1]  # Extract the year from the timestamp
            years.add(year) 

        Camera_ID = [document.get("Camera_ID") for document in collection_camera.find({})]
        # Extract the Model Names
        Model_Name = [document.get("Model_Name") for document in collection_model.find({})]
        # Extract the Add Camera Records

        return render_template("counting_dashboard.html",
        user_name=user_name,
        PersonCount=PersonCount,
        years=years,
        Camera_ID=Camera_ID,
        Model_Name=Model_Name)

    except Exception as e:
        print("Error :" , str(e))
        return render_template("counting_dashboard.html")


@app.route("/process_PersonCountIndex", methods=["POST"])
def process_PersonCountIndex():
    try:
        if request.method=="POST":

            data = request.get_json()
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')

            # Parse the date strings into datetime objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M")

            # Convert the datetime objects to strings in the format used in the DB
            start_date_db_format = start_date.strftime("%d/%m/%Y %H:%M:%S")
            end_date_db_format = end_date.strftime("%d/%m/%Y %H:%M:%S")

            # Validate that start date is not greater than end date
            if start_date > end_date:
                raise ValueError("Start date cannot be greater than end date.")

            start_index = 0
            per_page = 5

            print(f"Start index: {start_index}, Per page: {per_page}, Start date: {start_date_db_format}, End date: {end_date_db_format}")

            # Fetch records from the collection based on the date range
            selected_records = collection_PersonCountTracking.find({
                'Timestamp': {
                    '$gte': start_date_db_format,
                    '$lte': end_date_db_format
                }
            }).skip(start_index).limit(per_page)


            # Prepare data to be sent back to the client
            selected_records_list = [{
                "Person_in": record.get("person_in"),
                "Person_out": record.get("person_out"),
                "Time_stamp": record.get("Timestamp"),
                "TotalPerson": record.get("Total Person")
            } for record in selected_records]

            # Extract the Camera
            Camera_IP = [document.get("Camera_IP") for document in collection_camera.find({})]

            # Extract the Model Names
            Model_Name = [document.get("Model_Name") for document in collection_model.find({})]

            # Extract timestamps and other data
            timestamps = [record.get("Time_stamp") for record in selected_records_list]
            person_in = [record.get("Person_in") for record in selected_records_list]
            person_out = [record.get("Person_out") for record in selected_records_list]
            total_person = [record.get("TotalPerson") for record in selected_records_list]

            Person_in=sum(person_in)
            Person_out=sum(person_out)
            Total_person=sum(total_person)

            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, person_in, marker='o', color='blue', label='Person In')
            plt.plot(timestamps, person_out, marker='o', color='red', label='Person Out')
            plt.plot(timestamps, total_person, marker='o', color='green', label='Total Person')

            # Add titles and labels
            plt.title(f'Person In/Out and Total count from {start_date_str} to {end_date_str}')
            plt.xlabel('Timestamp')
            plt.ylabel('Percentage')
            plt.legend()
            plt.grid(False)

            # Save the plot as an image file
            graph_filename = "count_graph.png"
            graph_filepath = f'static/img/images/person_count/{graph_filename}'
            plt.savefig(graph_filepath)            

            # Save image in a Bytes format
            figfile = BytesIO()
            plt.savefig(figfile, format='png')
            figfile.seek(0)

            # Convert bytes to base64 string
            graph_image = base64.b64encode(figfile.getvalue()).decode('utf-8')

            return jsonify({'graph_image': graph_image, 'person_in' : Person_in , 'person_out' : Person_out , 'total_person' : Total_person})

        else:
            print("Inavlid request")
            return "Inavlid request"

    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template("counting_dashboard.html")

    
@app.route('/fetch_data_PersonCount', methods=['GET'])
def fetch_data_PersonCount():
    try:
        page = int(request.args.get('page', 1))
        per_page = 5
        start_index = (page - 1) * per_page

        # Fetch 5 records starting from start_index
        selected_records = collection_PersonCountTracking.find({}).skip(start_index).limit(per_page)

        # Prepare data to be sent back to the client
        selected_records_list = [{

            "Person_in": record.get("person_in"),
            "Person_out": record.get("person_out"),
            "Time_stamp": record.get("Timestamp"),
            "TotalPerson": record.get("Total Person")

        } for record in selected_records]

        return jsonify({'records': selected_records_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_counts_events_dashboard_person(timestamps, person_in, person_out, total_person):
    event_counts = {}
    for i in range(len(timestamps)):
        timestamp = timestamps[i]
        if timestamp not in event_counts:
            event_counts[timestamp] = [0, 0, 0]  # Initialize counts for person_in, person_out, and total_person
        event_counts[timestamp][0] += person_in[i]
        event_counts[timestamp][1] += person_out[i]
        event_counts[timestamp][2] += total_person[i]

    return  event_counts  


def person_count_dashboard_graph(person_count_event):

    data=person_count_event
    years = sorted(data.keys())
    person_in = [data[year][0] for year in years]
    person_out = [data[year][1] for year in years]
    total_person = [data[year][2] for year in years]

    plt.figure(figsize=(8, 6))

    plt.plot(years, person_in, label='Person In', marker='o')
    plt.plot(years, person_out, label='Person Out', marker='o')
    plt.plot(years, total_person, label='Total Person', marker='o')

    plt.xlabel('Year')
    plt.ylabel('Count the Person In, Out, Total')
    plt.title('Real Time Person Count Tracker')
    plt.xticks(years)
    plt.legend()
    plt.grid(True)


    # Save the graph
    graph_save_person = uuid.uuid4().hex + '.png'
    plt.savefig(f'static/{graph_save_person}')
    plt.close()
    
    return graph_save_person


@app.route("/dashboard" , methods=['POST' , 'GET'])
def dashboard():
    try:
        user_name = request.args.get('user_name', '')
        Time_stamp = 'year'
        event = 'Event_Occur'

        Time_stamp = [document.get(Time_stamp) for document in collection_smoke_fall.find({})]
        event = [document.get(event) for document in collection_smoke_fall.find({})]

        Graph_save_fire=generate_dashboard_graph(Time_stamp, event)
       
        timestamps = [record.get('Year') for record in collection_PersonCountTracking.find({})]
        person_in = [record.get("person_in") for record in collection_PersonCountTracking.find({})]
        person_out = [record.get("person_out") for record in collection_PersonCountTracking.find({})]
        total_person = [record.get("Total Person") for record in collection_PersonCountTracking.find({})]

        person_count_event=calculate_counts_events_dashboard_person(timestamps ,person_in,person_out,total_person)
        persongraph=person_count_dashboard_graph(person_count_event)

        # Extract the Camera IP
        Camera_IP=[document.get("Camera_IP") for document in collection_camera.find({})]

        # Extract the Camera ID
        Camera_ID=[document.get("Camera_ID") for document in collection_camera.find({})]

        # Extract the Model Names
        Model_Name = [document.get("Model_Name") for document in collection_model.find({})]

        return render_template("dashboard.html",  fire_graphs=Graph_save_fire , Model_Name=Model_Name , 
                               Camera_IP=Camera_IP, Camera_ID=Camera_ID, person_graph=persongraph ,
                                user_name=user_name)

    except Exception as e:
        print("Error :" ,  str(e))
        return render_template("dashboard.html")

@app.route("/add_camera")
def add_camera():
    return render_template("Add_camera.html")


@app.route("/display_stream")
def display_stream():
    return render_template("display_stream.html")


@app.route("/add_model")
def add_model():
    return render_template("Add_model.html")


@app.route("/view_stream")
def view_stream():

    
    camera_key = 'Camera_ID'
    model_path = 'Model_Name'
    timestamp = 'Time_stamp'



    x = collection_camera.find({})
    y = collection_model.find({})
    fire_data = collection_smoke_fall.find({})




    camera_ids = [document.get(camera_key) for document in x]
    model_paths = [document.get(model_path) for document in y]

    fire_datas = [document.get(timestamp) for document in fire_data]


    return render_template('view_stream.html', camera_ids=camera_ids, model_paths=model_paths,
                           fire_frame_num=fire_datas
                        )


@app.route('/submit_camera', methods=["POST"])
def submit_camera():
    if request.method == "POST":
        data = {
            "Camera_ID": request.form["uniqueId"],
            "Camera_IP": request.form["ipAddress"],
        }
        camera_key = 'Camera_ID'
        camera_ids_exist = [document.get(camera_key) for document in collection_camera.find({})]

        if data['Camera_ID'] != "" and data['Camera_IP'] != "": 
            if int(data['Camera_ID']) >0:
                if data['Camera_ID'] not in camera_ids_exist:
                     try:
                         ipaddress.ip_address(data['Camera_IP'])
                     except ValueError:
                         return render_template('Add_camera.html', error='Invalid IP address format')

                     collection_camera.insert_one(data)

        else:
            return render_template('Add_camera.html' , error='Camera ID is not Valid Number')
        return render_template('Add_camera.html')


@app.route('/submit_model', methods=["POST"])
def submit_model():
    if request.method == "POST":
        data = {
            "Model_ID": request.form["Model_ID"],
            "Model_Name": request.form["Model_Name"],
            "Model_Path": request.form["Model_Path"],
            "Model_Type": request.form["Model_Type"],
        }

        model_names='Model_Name'
        model_id='Model_ID'
        model_names = [document.get(model_names) for document in collection_model.find({})]
        model_id = [document.get(model_id) for document in collection_model.find({})]
    
        # if data['Model_ID']!="" and data['Model_Name']!="" and data['Model_Path']!="" :
        #     if int(data['Model_ID']) > 0:
        #         if data['Model_Name'] not in model_names and data['Model_ID'] not in model_id:
        collection_model.insert_one(data)
        # else: 
        #     return render_template('Add_model.html')
        return render_template('Add_model.html')


@app.route('/submit_view_stream', methods=["POST"])
def submit_view_stream():
    if request.method == "POST":
        data = {
            "Camera_ID": request.form["camera_id"],
            "Model_path": request.form["model_option"],
            'fire_frame_num' : request.form["smoke_detection_frames"],
        
        }
        camera_id = data['Camera_ID']
        model_name = data['Model_path']
        fire_detection = data['fire_frame_num']


        if fire_detection and model_name == 'Fire and Smoke Detection':
            Time_stamp = 'Time_stamp'
            frame_bytes = collection_smoke_fall.find_one({Time_stamp: fire_detection})["frame"]
            frame_image = Image.open(io.BytesIO(frame_bytes))
            frame_image.save('output_image/fire_output_image/frame.jpg')
            frame_fire = base64.b64encode(frame_bytes).decode('utf-8')

            return render_template('display_stream.html', 
                           model_name=model_name, camera_id=camera_id, 
                           frames_number=fire_detection, frame=frame_fire)
        

# Fetch the Camera IPs and Model Names



@app.route("/thank_you")
def thank_you():
    return "Thank you for your submission!"


if __name__ == "__main__":
    app.run(debug=True)
