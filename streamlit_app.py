import streamlit as st
import requests
import pandas as pd
import numpy as np

import ast

from statsmodels.tsa.arima.model import ARIMA

from datetime import datetime

from pmdarima import auto_arima

st.title("Restaurant Wastage Food Analysis")

st.write("Select a date range:")

# Date range input
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
print(start_date.isoformat())
# print(type(start_date))

if start_date and end_date:
    if start_date <= end_date:
    # Make API request to Flask backend
        response = requests.post(f"http://127.0.0.1:5000/predict_wastage_food",data = {'date_start_input': start_date.isoformat(), 'date_end_input': end_date.isoformat()})
        
        if response.status_code == 200:
            predictions = response.json()["predictions"]
            pred_list = ast.literal_eval(predictions)
            st.write(pd.DataFrame({'Date' : pd.date_range(start = start_date, end = end_date),'Predictions' : pred_list}))
        else:
            st.write("Error fetching prediction")
    else:
        st.write('End date must be after start date')
