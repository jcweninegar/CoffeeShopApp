import streamlit as st
import pandas as pd

# Define capture rates for each year and month
capture_rate_years = {
    1: [0.0062, 0.0057, 0.0070, 0.0068, 0.0071, 0.0074, 0.0075, 0.0084, 0.0080, 0.0084, 0.0080, 0.0077],
    2: [0.0130, 0.0119, 0.0147, 0.0143, 0.0148, 0.0155, 0.0158, 0.0176, 0.0167, 0.0177, 0.0168, 0.0163],
    3: [0.0167, 0.0152, 0.0188, 0.0183, 0.0190, 0.0199, 0.0202, 0.0225, 0.0214, 0.0227, 0.0215, 0.0208]
}

# Streamlit App Interface
st.title("Coffee Shop Sales and Labor Forecaster")

# User Inputs
average_daily_traffic = st.number_input("Average Daily Traffic Count", min_value=0, step=1)
average_sale = st.number_input("Average Sale Amount ($)", min_value=0.0, step=0.1)
days_open_per_week = st.number_input("Days Open per Week", min_value=1, max_value=7, step=1)
number_of_competitors = st.number_input("Number of Coffee Shops within a 2-Mile Radius", min_value=0, step=1)
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

    # Calculate estimated monthly sales for each year with adjusted capture rates
    yearly_sales_data = {}
    for year in capture_rate_years:
        capture_rates = capture_rate_years[year]
        monthly_sales_estimates = [
            (average_daily_traffic * adjust_capture_rate(rate, number_of_competitors) * average_sale * days_open_per_week * 4.3)
            for rate in capture_rates
        ]
        yearly_sales_data[year] = monthly_sales_estimates + [sum(monthly_sales_estimates)]

    # Convert sales data to a DataFrame for display and format as currency
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December", "Yearly Total"]
    sales_df = pd.DataFrame(yearly_sales_data, index=months).T
    sales_df.index.name = "Year"
    sales_df = sales_df.applymap(lambda x: f"${int(x):,}")

    st.subheader("Estimated Sales for 3 Years")
    st.write(sales_df)

    # Calculate monthly labor costs based on weekly labor needs
    def calculate_monthly_labor_cost():
        monthly_labor_cost = []
        for year in range(1, 4):
            year_cost = []
            for month in range(12):
                # Assume weekly labor costs based on provided rates and coverages
                weekly_labor_cost = (
                    (36 * manager_rate) +
                    (max(0, days_open_per_week * 2) * shift_supervisor_rate) + 
                    ((days_open_per_week * (end_time - start_time) - 36) * barista_rate)
                )
                year_cost.append(weekly_labor_cost * 4.3)  # Approximate monthly labor cost
            monthly_labor_cost.append(year_cost + [sum(year_cost)])  # Append yearly total
        return monthly_labor_cost

    labor_cost_data = calculate_monthly_labor_cost()
    labor_cost_df = pd.DataFrame(labor_cost_data, index=["Year 1", "Year 2", "Year 3"], columns=months)
    labor_cost_df = labor_cost_df.applymap(lambda x: f"${int(x):,}")

    st.subheader("Estimated Monthly Labor Cost for 3 Years")
    st.write(labor_cost_df)

    # Calculate labor cost as a percentage of sales
    labor_cost_percentage_data = []
    for year in range(3):
        year_percentage = []
        for month in range(12):
            sales_value = int(sales_df.iloc[year, month].replace('$', '').replace(',', ''))
            labor_cost_value = int(labor_cost_df.iloc[year, month].replace('$', '').replace(',', ''))
            percentage = (labor_cost_value / sales_value * 100) if sales_value > 0 else 0
            year_percentage.append(f"{percentage:.2f}%")
        labor_cost_percentage_data.append(year_percentage + ["-"])  # Skip yearly total in percentage

    labor_cost_percentage_df = pd.DataFrame(labor_cost_percentage_data, index=["Year 1", "Year 2", "Year 3"], columns=months)

    st.subheader("Labor Cost as a Percentage of Sales for 3 Years")
    st.write(labor_cost_percentage_df)
