#!/usr/bin/env python
# coding: utf-8

# import statements
from fastapi import FastAPI, HTTPException
import json
import numpy as np
import pickle
from datetime import datetime

app = FastAPI()

# Import the airport encodings file
with open('airport_encodings.json', 'r') as f:

# returns JSON object as a dictionary
    airports = json.load(f)

#Importing trained model
with open('finalized_model.pkl', 'rb') as f:
    model = pickle.load(f)

def create_airport_encoding(airport: str, airports: dict) -> np.array:
    """
    create_airport_encoding is a function that creates an array the length of all arrival airports from the chosen
    departure aiport.  The array consists of all zeros except for the specified arrival airport, which is a 1.  

    Parameters
    ----------
    airport : str
        The specified arrival airport code as a string
    airports: dict
        A dictionary containing all of the arrival airport codes served from the chosen departure airport
        
    Returns
    -------
    np.array
        A NumPy array the length of the number of arrival airports.  All zeros except for a single 1 
        denoting the arrival airport.  Returns None if arrival airport is not found in the input list.
        This is a one-hot encoded airport array.

    """
    temp = np.zeros(len(airports))
    if airport in airports:
        temp[airports.get(airport)] = 1
        temp = temp.T
        return temp
    else:
        return None

# TODO:  write the back-end logic to provide a prediction given the inputs
# requires finalized_model.pkl to be loaded 
# the model must be passed a NumPy array consisting of the following:
# (polynomial order, encoded airport array, departure time as seconds since midnight, arrival time as seconds since midnight)
# the polynomial order is 1 unless you changed it during model training in Task 2
# YOUR CODE GOES HERE
def as_seconds_since_midnight(time_str: str) -> int:
    time_obj = datetime.strptime(time_str, "%H:%M")
    seconds = time_obj.hour * 3600 + time_obj.minute * 60
    return seconds

def predict_delay(arrival_airport: str, local_dep_time: str, local_arr_time: str, polynomial_order: int = 1):
    encoded_airport = create_airport_encoding(arrival_airport, airports)
    if encoded_airport is None:
        raise HTTPException(status_code=404, detail="Arrival airport not found")
    dep_time = as_seconds_since_midnight(local_dep_time)
    arr_time = as_seconds_since_midnight(local_arr_time)
    features = np.concatenate([
        [polynomial_order],
        encoded_airport,
        [dep_time],
        [arr_time]
    ])

    features = features.reshape(1, -1)
    prediction = model.predict(features)
    return prediction.item()

# TODO:  write the API endpoints.  
# YOUR CODE GOES HERE
@app.get('/')
def home():
    return {'message': 'You have successfully reached the main page for predicting flight delays'}

@app.get('/predict/delays')
def predict_delays(arrival_airport: str, local_dep_time: str, local_arr_time: str):
    if arrival_airport not in airports:
        raise HTTPException(status_code=404, detail="Arrival airport not found")

    try:
        datetime.strptime(local_dep_time, "%H:%M")
        datetime.strptime(local_arr_time, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid time format.")

    try:
        avg_delay = predict_delay(arrival_airport, local_dep_time, local_arr_time)
    except Exception as e:
        raise HTTPException(status_code=404, detail= f'Prediction error: {str(e)}')

    return {
        'arrival_airport': arrival_airport,
        'local_dep_time': local_dep_time,
        'local_arr_time': local_arr_time,
        'average_dep_delay_min': round(avg_delay, 2)
    }
