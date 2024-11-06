import streamlit as st
import pandas as pd

# Define capture rates for each year and month
capture_rate_years = {
    1: [0.0062, 0.0057, 0.0070, 0.0068, 0.0071, 0.0074, 0.0075, 0.0084, 0.0080, 0.0084, 0.0080, 0.0077],
    2: [0.0130, 0.0119, 0.0147, 0.0143, 0.0148, 0.0155, 0.0158, 0.0176, 0.0167, 0.0177, 0.0168, 0.0163],
    3: [0.0167, 0.0152, 0.0188, 0.0183, 0.0190, 0.0199, 0.0202, 0.0225, 0.0214, 0.0227, 0.0215, 0.0208]
}

# Define hourly sales percentages for operating hours (24 hours total)
hourly_sales_percentages = [
    0.005, 0.005, 0.005, 0.005, 0.005,  # 12 AM - 5 AM
    0.01, 0.02,                         # 6 AM - 7 AM
    0.20, 0.20, 0.0833, 0.0833, 0.0833, # 7 AM - 12 PM (peak hours)
    0.075, 0.075, 0.0667, 0.0667, 0.0667, # 12 PM - 5 PM
    0.02, 0.02,                         # 5 PM - 7 PM
    0.015, 0.015,                       # 7 PM - 9 PM
    0.01, 0.005, 0.005                 # 9 PM - 12 AM
]

# Streamlit App Interface
st.title("Coffee Shop Sales and Labor Forecaster")

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

manager_rate = st.number_input("Manager Hourly Rate ($)", min_value=0.0, step=0.1)
shift_supervisor_rate = st.number_input("Shift Supervisor Hourly Rate ($)", min_value=0.0, step=0.1)
barista_rate = st.number_input("Barista Hourly Rate ($)", min_value=0.0, step=0.1)

# Helper function to convert 24-hour format to 12-hour format with AM/PM
def convert_to_12_hour_format(hour):
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"

# Operating Hours Slider
operating_hours = st.slider(
    "Operating Hours (Start and End Times)", 
    value=(7, 17), 
    min_value=0, 
    max_value=24, 
    format="%d:00",
    help="Select the start and end times for daily operation in 24-hour format."
)

# Convert the selected start and end times to 12-hour format for display
start_time, end_time = operating_hours
start_time_12hr = convert_to_12_hour_format(start_time)
end_time_12hr = convert_to_12_hour_format(end_time)

# Display the selected times in 12-hour format with AM/PM
st.write(f"**Selected Operating Hours:** {start_time_12hr} - {end_time_12hr}")


# Button to Generate Projections
if st.button("Generate Projections"):

    # Adjust capture rate based on competition
    def adjust_capture_rate(rate, competitors):
        adjustment_factor = 1 - (competitors * 0.05)
        return rate * adjustment_factor

    start_time, end_time = operating_hours
    st.write(f"**Selected Operating Hours:** {start_time}:00 - {end_time}:00")

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

    # Implement Coverage Rules to Calculate Weekly Labor Requirements
    def calculate_weekly_coverage(hours_open):
        total_hours_weekly = hours_open * days_open_per_week
        manager_hours = min(36, total_hours_weekly)  # Manager covers up to 36 hours
        remaining_hours = max(0, total_hours_weekly - manager_hours)  # Remaining hours after manager
        
        # Shift Supervisors fill remaining floor hours with open/close time
        shift_supervisor_hours = remaining_hours + days_open_per_week * 2
        barista_hours = total_hours_weekly - (manager_hours + shift_supervisor_hours)
        
        return {
            "Manager": manager_hours,
            "Shift Supervisor": shift_supervisor_hours,
            "Barista": barista_hours
        }

    # Calculate total hours per week based on user inputs and coverage rules
    total_weekly_hours = calculate_weekly_coverage(end_time - start_time)
    labor_costs = {
        "Manager": total_weekly_hours["Manager"] * manager_rate,
        "Shift Supervisor": total_weekly_hours["Shift Supervisor"] * shift_supervisor_rate,
        "Barista": total_weekly_hours["Barista"] * barista_rate
    }
    total_weekly_labor_cost = sum(labor_costs.values())

    # Estimate Monthly Labor Costs
    estimated_monthly_labor = total_weekly_labor_cost * 4.3
    st.subheader("Estimated Monthly Labor Cost")
    st.write(f"${int(estimated_monthly_labor):,}")

    # Display labor costs as a percentage of sales for comparison
    # (Using the first year's average monthly sales for simplicity)
    average_monthly_sales = sum(yearly_sales_data[1]) / 12 if sum(yearly_sales_data[1]) > 0 else 0
    labor_cost_percentage = (estimated_monthly_labor / average_monthly_sales * 100) if average_monthly_sales > 0 else 0

    st.subheader("Labor Cost as a Percentage of Sales")
    st.write(f"{labor_cost_percentage:.2f}%")

    # Initial Staffing Needs
    initial_staffing = {
        "Manager(s)": total_weekly_hours["Manager"] / 36,
        "Shift Supervisor(s)": total_weekly_hours["Shift Supervisor"] / 36,
        "Barista(s)": total_weekly_hours["Barista"] / 36
    }

    st.subheader("Initial Staffing Needs")
    st.write(initial_staffing)
