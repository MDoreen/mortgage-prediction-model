import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load the trained model
with open("MortgageApp_model.pkl", "rb") as f:
    model = pickle.load(f)

# Get the expected features from the model
expected_features = model.feature_names_in_

# Define the list of locations from your training data
location_options = [
    'Karen', 'Kiambu Road', 'Kileleshwa', 'Kilimani', 'Kitisuru', 'Kyuna',
    'Lavington', 'Loresho', 'Lower Kabete', 'Mombasa Rd', 'Muthaiga',
    'Muthaiga North', 'Nairobi West', 'Ngong Rd', 'Nyari', 'Ongata Rongai',
    'Parklands', 'Riverside', 'Rosslyn', 'Runda', 'Syokimau', 'Thigiri',
    'Thome', 'Waithaka', 'Westlands'
]

# Streamlit App Title
st.title("🏠 Nairobi Smart Mortgage Price Predictor")

# Sidebar input fields
st.sidebar.header("Enter Property Features:")

bedroom = st.sidebar.slider("Number of Bedrooms", 1, 10, 3)
bathroom = st.sidebar.slider("Number of Bathrooms", 1, 10, 2)
house_size = st.sidebar.number_input("House Size (m²)", min_value=10.0, value=100.0)
land_size = st.sidebar.number_input("Land Size (acres)", min_value=0.01, value=0.25)
location = st.sidebar.selectbox("Location", location_options)

# Build input DataFrame
input_dict = {
    "Bedroom": bedroom,
    "bathroom": bathroom,
    "House size": house_size,
    "Land size": land_size,
}

# One-hot encode location
for loc in location_options:
    input_dict[f"Location_{loc}"] = 1 if loc == location else 0

# Convert to DataFrame
input_df = pd.DataFrame([input_dict])

# Ensure all expected features are present
for col in expected_features:
    if col not in input_df.columns:
        input_df[col] = 0

# Reorder columns to match training
input_df = input_df[expected_features]

# Predict
if st.button("Predict Price"):
    log_price = model.predict(input_df)[0]
    price = np.exp(log_price)
    st.success(f"💰 Estimated Price: KSh {price:,.0f}")