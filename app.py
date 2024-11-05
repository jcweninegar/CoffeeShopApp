import streamlit as st
import pandas as pd

# Load CSS styles
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Display the logo with the CSS class
st.markdown('<img src="3.png" class="logo">', unsafe_allow_html=True)

# Title
st.title("Coffee Shop Sales & Labor Forecaster")

# User Inputs
monthly_sales_projection = st.number_input("Enter Monthly Sales Projection ($):", min_value=0.0, step=0.01)
manager_hourly_rate = st.number_input("Enter Manager Hourly Rate ($):", min_value=0.0, step=0.01)
supervisor_hourly_rate = st.number_input("Enter Supervisor Hourly Rate ($):", min_value=0.0, step=0.01)
barista_hourly_rate = st.number_input("Enter Part-Time Barista Hourly Rate ($):", min_value=0.0, step=0.01)

# Sales distribution percentages by day
day_percentages = {
    "Monday": 0.1399,
    "Tuesday": 0.15,
    "Wednesday": 0.1599,
    "Thursday": 0.1599,
    "Friday": 0.17,
    "Saturday": 0.2199
}

# Time block sales distribution percentages
time_block_percentages = {
    "7 AM - 9 AM": 0.4,
    "9 AM - 12 PM": 0.25,
    "12 PM - 2 PM": 0.15,
    "2 PM - 5 PM": 0.2
}

# Function to calculate labor cost based on hourly sales
def calculate_labor_cost(time_block_sales, time_block_hours):
    hourly_sales = time_block_sales / time_block_hours
    if hourly_sales <= 200:
        required_staff = 2
    elif hourly_sales <= 500:
        required_staff = 3
    elif hourly_sales <= 700:
        required_staff = 4
    else:
        required_staff = 5

    # Assign roles based on staffing needs
    manager_hours = min(required_staff, 2) * time_block_hours  # Manager covers up to 2 spots
    supervisor_hours = max(0, required_staff - 2) * time_block_hours  # Supervisor covers the next spots
    barista_hours = max(0, required_staff - 3) * time_block_hours  # Remaining filled by baristas

    # Calculate labor cost
    manager_cost = manager_hours * manager_hourly_rate
    supervisor_cost = supervisor_hours * supervisor_hourly_rate
    barista_cost = barista_hours * barista_hourly_rate

    return manager_cost + supervisor_cost + barista_cost

# Calculate daily and monthly labor costs
def calculate_daily_labor_costs(daily_sales):
    daily_labor_cost = 0
    for time_block, percentage in time_block_percentages.items():
        time_block_sales = daily_sales * percentage
        time_block_hours = 2 if time_block == "7 AM - 9 AM" or time_block == "12 PM - 2 PM" else 3
        labor_cost = calculate_labor_cost(time_block_sales, time_block_hours)
        daily_labor_cost += labor_cost
    return daily_labor_cost

# Calculate monthly labor costs
if st.button("Calculate Monthly Labor Costs"):
    monthly_labor_cost = 0
    for day, percentage in day_percentages.items():
        daily_sales = monthly_sales_projection * percentage / 4.3  # Estimate individual day sales
        daily_labor_cost = calculate_daily_labor_costs(daily_sales)
        monthly_labor_cost += daily_labor_cost * 4.3  # Multiply by 4.3 to get monthly total for this day type

    st.write(f"Estimated Monthly Labor Cost: ${monthly_labor_cost:,.2f}")
