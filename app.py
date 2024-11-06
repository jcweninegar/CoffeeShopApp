import streamlit as st
import pandas as pd

# Define capture rates for each year and month
capture_rate_years = {
    1: [0.0062, 0.0057, 0.0070, 0.0068, 0.0071, 0.0074, 0.0075, 0.0084, 0.0080, 0.0084, 0.0080, 0.0077],
    2: [0.0130, 0.0119, 0.0147, 0.0143, 0.0148, 0.0155, 0.0158, 0.0176, 0.0167, 0.0177, 0.0168, 0.0163],
    3: [0.0167, 0.0152, 0.0188, 0.0183, 0.0190, 0.0199, 0.0202, 0.0225, 0.0214, 0.0227, 0.0215, 0.0208]
}

# Define hourly sales percentages for a full 24-hour period
hourly_sales_percentages = [
    0.005, 0.005, 0.005, 0.005, 0.005,  # 12 AM - 5 AM
    0.01, 0.02,                         # 6 AM - 7 AM
    0.20, 0.20, 0.0833, 0.0833, 0.0833, # 7 AM - 12 PM (peak hours)
    0.075, 0.075, 0.0667, 0.0667, 0.0667, # 12 PM - 5 PM
    0.02, 0.02,                         # 5 PM - 7 PM
    0.015, 0.015,                       # 7 PM - 9 PM
    0.01, 0.005, 0.005                 # 9 PM - 12 AM
]

# Helper function to convert 24-hour time to 12-hour format with AM/PM
def convert_to_12_hour_format(hour):
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"

# Streamlit App Interface
st.title("Coffee Sales Forecaster")

# User Inputs
average_daily_traffic = st.number_input(
    "Average Daily Traffic Count", 
    min_value=0, 
    step=1, 
    help="Estimated number of people passing by the coffee shop each day."
)

average_sale = st.number_input(
    "Average Sale Amount ($)", 
    min_value=0.0, 
    step=0.1, 
    help="Average amount spent by each customer."
)

days_open_per_week = st.number_input(
    "Days Open per Week", 
    min_value=1, 
    max_value=7, 
    step=1, 
    help="Enter the number of days your shop is open each week."
)

number_of_competitors = st.number_input(
    "Number of Coffee Shops within a 2-Mile Radius",
    min_value=0,
    step=1,
    help="Enter the number of competing coffee shops within a 2-mile radius."
)

# Labor Rates Inputs
manager_rate = st.number_input("Manager Hourly Rate ($)", min_value=0.0, step=0.1)
shift_supervisor_rate = st.number_input("Shift Supervisor Hourly Rate ($)", min_value=0.0, step=0.1)
barista_rate = st.number_input("Barista Hourly Rate ($)", min_value=0.0, step=0.1)

# Adjust capture rate based on competition
def adjust_capture_rate(rate, competitors):
    # Decrease the capture rate by 5% for each competitor
    adjustment_factor = 1 - (competitors * 0.05)
    return rate * adjustment_factor

# Operating Hours Slider with 12-hour display format
operating_hours = st.slider(
    "Operating Hours (Start and End Times)", 
    value=(7, 17), 
    min_value=0, 
    max_value=24, 
    format="%d:00",
    help="Select the start and end times for daily operation in 24-hour format."
)

# Display the selected times in 12-hour format
start_time, end_time = operating_hours
st.write(f"**Selected Operating Hours:** {convert_to_12_hour_format(start_time)} - {convert_to_12_hour_format(end_time)}")

# Step 1: Calculate total operating hours per week (including open/close hours)
daily_operating_hours = end_time - start_time
weekly_operating_hours = daily_operating_hours * days_open_per_week
open_close_hours = days_open_per_week * 2  # 1 hour each for opening and closing
total_supervisory_hours = weekly_operating_hours + open_close_hours

# Step 2: Calculate supervisory hours (Manager + Shift Supervisor)
# Manager covers 36 hours on the floor; subtract from total to find Shift Supervisor hours needed
shift_supervisor_hours = total_supervisory_hours - 36  # Remaining hours for Shift Supervisors

# Step 5: Calculate Total Coverage Hours based on sales
# Apply coverage rules for each hour in the day based on hourly sales
total_coverage_hours = 0
for percentage in hourly_sales_percentages:
    # Estimate daily sales per hour and apply coverage rules
    hourly_sales = (average_daily_traffic * adjust_capture_rate(percentage, number_of_competitors) * average_sale)
    if hourly_sales > 700:
        total_coverage_hours += 5  # 5 employees
    elif hourly_sales > 500:
        total_coverage_hours += 4  # 4 employees
    elif hourly_sales > 200:
        total_coverage_hours += 3  # 3 employees
    else:
        total_coverage_hours += 2  # Minimum 2 employees

# Multiply by days open per week to get weekly total coverage hours
total_coverage_hours *= days_open_per_week

# Step 6: Calculate barista hours
barista_hours = total_coverage_hours - total_supervisory_hours

# Step 7: Calculate labor costs
# Multiply hours by rates to get monthly costs for each role
weekly_manager_cost = manager_rate * 36  # 36 hours on floor
weekly_shift_supervisor_cost = shift_supervisor_rate * shift_supervisor_hours
weekly_barista_cost = barista_rate * barista_hours

# Calculate monthly cost for each role and total labor cost
monthly_manager_cost = weekly_manager_cost * 4.3
monthly_shift_supervisor_cost = weekly_shift_supervisor_cost * 4.3
monthly_barista_cost = weekly_barista_cost * 4.3
monthly_total_labor_cost = monthly_manager_cost + monthly_shift_supervisor_cost + monthly_barista_cost

# Display Estimated Labor Cost Table for 3 Years
st.subheader("Estimated Labor for 3 Years ($)")
labor_cost_data = {
    "Manager": [monthly_manager_cost] * 12,
    "Shift Supervisor": [monthly_shift_supervisor_cost] * 12,
    "Barista": [monthly_barista_cost] * 12,
    "Total": [monthly_total_labor_cost] * 12
}
labor_cost_df = pd.DataFrame(labor_cost_data, index=months).applymap(lambda x: f"${int(x):,}")
st.write(labor_cost_df)

# Calculate labor cost as a percentage of sales
labor_cost_percentage_df = pd.DataFrame({
    "Manager %": [monthly_manager_cost / float(sales.strip('$').replace(',', '')) * 100 for sales in sales_df.iloc[year - 1]],
    "Shift Supervisor %": [monthly_shift_supervisor_cost
