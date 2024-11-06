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

# Calculate estimated monthly sales for each year with adjusted capture rates
yearly_sales_data = {}
for year in capture_rate_years:
    capture_rates = capture_rate_years[year]
    monthly_sales_estimates = [
        (average_daily_traffic * adjust_capture_rate(rate, number_of_competitors) * average_sale * days_open_per_week * 4.3)
        for rate in capture_rates
    ]
    yearly_sales_data[year] = monthly_sales_estimates + [sum(monthly_sales_estimates)]  # Add yearly total as the last column

# Convert sales data to a DataFrame for display and format as currency
months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December", "Yearly Total"]
sales_df = pd.DataFrame(yearly_sales_data, index=months).T
sales_df.index.name = "Year"
sales_df = sales_df.applymap(lambda x: f"${int(x):,}")  # Format as currency without cents

st.subheader("Estimated Sales for 3 Years")
st.write(sales_df)

# Calculate labor costs for each year based on average weekly hours from coverage data
average_weekly_hours = 612 / 6  # Assume daily coverage requirement from earlier analysis
yearly_labor_cost_data = {
    year: [round(average_weekly_hours * 4.3 * (manager_rate + shift_supervisor_rate + barista_rate)) for _ in range(12)] + 
          [round(average_weekly_hours * 4.3 * (manager_rate + shift_supervisor_rate + barista_rate) * 12)]
    for year in capture_rate_years
}

labor_cost_df = pd.DataFrame(yearly_labor_cost_data, index=months).T
labor_cost_df.index.name = "Year"
labor_cost_df = labor_cost_df.applymap(lambda x: f"${int(x):,}")  # Format as currency without cents

st.subheader("Estimated Labor for 3 Years ($)")
st.write(labor_cost_df)

# Calculate labor cost as a percentage of sales
labor_cost_percentage_df = pd.DataFrame({
    year: [(labor / float(sales.strip('$').replace(',', '')) * 100) if float(sales.strip('$').replace(',', '')) > 0 else 0 
           for labor, sales in zip(labor_cost_df.iloc[year - 1], sales_df.iloc[year - 1])]
    for year in yearly_sales_data
}, index=months).T
labor_cost_percentage_df = labor_cost_percentage_df.applymap(lambda x: f"{x:.2f}%")  # Format as percentage

st.subheader("Estimated Labor for 3 Years (%)")
st.write(labor_cost_percentage_df)

# Initial Staffing Needs based on average week for Month 7 of Year 1
initial_manager_staff = round(average_weekly_hours / manager_rate)
initial_supervisor_staff = round(average_weekly_hours / shift_supervisor_rate)
initial_barista_staff = round(average_weekly_hours / barista_rate)

st.subheader("Initial Staffing Needs")
st.write(f"Manager(s): {initial_manager_staff}")
st.write(f"Shift Supervisor(s): {initial_supervisor_staff}")
st.write(f"Barista(s): {initial_barista_staff}")
