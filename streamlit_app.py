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

selected_hotel = st.selectbox("Select Hotel:", ["Hotel-1", "Hotel-2"])

# print(type(start_date))


predicted_wastage = {
    'Monday': 228.5883,
    'Tuesday': 228.8125,
    'Wednesday': 219.6875,
    'Thursday': 224.1875,
    'Friday': 196.1875,
    'Saturday': 210.375,
    'Sunday': 243.7647
}



if start_date and end_date:
    if start_date <= end_date:
    # Make API request to Flask backend
        response = requests.post(f"http://127.0.0.1:5000/predict_wastage_food",data = {'date_start_input': start_date.isoformat(), 'date_end_input': end_date.isoformat(),'selected_hotel': selected_hotel})
        
        if response.status_code == 200:
            if selected_hotel == "Hotel-1":
                predictions = response.json()["prediction_hotel_1"]
                pred_list = ast.literal_eval(predictions)
                op_df = pd.DataFrame({'Date' : pd.date_range(start = start_date, end = end_date),'ARIMA_Predictions' : pred_list})
                op_df.set_index('Date', inplace=True)
                op_df['OLS_Regression_Result'] = op_df.index.day_name().map(predicted_wastage)
                op_df.index = op_df.index.strftime('%Y-%m-%d')
                st.write(op_df)
            elif selected_hotel == "Hotel-2":
                predictions = response.json()["prediction_hotel_2"]
                pred_list = ast.literal_eval(predictions)
                op_df = pd.DataFrame({'Date' : pd.date_range(start = start_date, end = end_date),'ARIMA_Predictions' : pred_list})
                op_df.set_index('Date', inplace=True)
                op_df['OLS_Regression_Result'] = op_df.index.day_name().map(predicted_wastage)
                op_df.index = op_df.index.strftime('%Y-%m-%d')
                st.write(op_df)
        else:
            st.write("Error fetching prediction")
    else:
        st.write('End date must be after start date')
