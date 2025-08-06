import streamlit as st
import pickle
import numpy as np

# Load the trained model
with open("Mortgage_model.pkl", "rb") as f:
    model = pickle.load(f)

# App title
st.markdown("<h1 style='text-align: center;'>🏡 Mortgage Price Predictor</h1>", unsafe_allow_html=True)
st.write("Enter property details below to predict the estimated price.")

# Input fields
bedroom = st.number_input("Number of Bedrooms", min_value=1, value=3)
bathroom = st.number_input("Number of Bathrooms", min_value=1, value=2)
house_size = st.number_input("House Size (in m²)", min_value=10.0, value=120.0)
land_size = st.number_input("Land Size (in acres)", min_value=0.01, value=0.5)

# Predict button
if st.button("Predict Price"):
    input_data = np.array([[bedroom, bathroom, house_size, land_size]])
    log_price = model.predict(input_data)[0]
    price = np.exp(log_price)  # Convert log price back to normal price

    st.success(f"💰 Estimated Property Price: KSh {price:,.0f}")