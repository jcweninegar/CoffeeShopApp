import streamlit as st
import pandas as pd

# Define sales percentages by day of the week
day_percentages = {
    "Monday": 0.1399,
    "Tuesday": 0.15,
    "Wednesday": 0.1599,
    "Thursday": 0.1599,
    "Friday": 0.17,
    "Saturday": 0.2199
}

# Define time block percentages for sales distribution within each day
time_block_percentages = {
    "7 AM - 9 AM": 0.4,
    "9 AM - 12 PM": 0.25,
    "12 PM - 2 PM": 0.15,
    "2 PM - 5 PM": 0.2
}

# Define staffing thresholds based on hourly sales
STAFF_THRESHOLDS = {
    200: 2,  # 2 staff for up to $200/hour
    500: 3,  # 3 staff for up to $500/hour
    700: 4,  # 4 staff for up to $700/hour
    float("inf"): 5  # 5 staff for over $700/hour
}

# User Inputs
st.title("Coffee Shop Sales & Labor Forecaster")
monthly_sales_projection = st.number_input("Enter Monthly Sales Projection ($):", min_value=0.0, value=50000.0, step=500.0)
manager_hourly_rate = st.number_input("Enter Manager Hourly Rate ($):", min_value=0.0, value=20.0, step=0.5)
supervisor_hourly_rate = st.number_input("Enter Supervisor Hourly Rate ($):", min_value=0.0, value=15.0, step=0.5)
barista_hourly_rate = st.number_input("Enter Barista Hourly Rate ($):", min_value=0.0, value=12.0, step=0.5)

# Input fields for hours of operation
st.subheader("Hours of Operation")
open_hour = st.number_input("Opening Hour (24-hour format, e.g., 7 for 7 AM):", min_value=0, max_value=23, value=7)
close_hour = st.number_input("Closing Hour (24-hour format, e.g., 17 for 5 PM):", min_value=0, max_value=23, value=17)

# Calculate total operating hours per day
hours_open_per_day = close_hour - open_hour

# Function to determine the staff count needed based on hourly sales
def determine_staff_needed(hourly_sales):
    for threshold, staff_count in STAFF_THRESHOLDS.items():
        if hourly_sales <= threshold:
            return staff_count

# Function to calculate labor cost for a given time block based on staffing needs
def calculate_time_block_labor_cost(time_block_sales, time_block_hours, manager_rate, supervisor_rate, barista_rate):
    hourly_sales = time_block_sales / time_block_hours
    staff_needed = determine_staff_needed(hourly_sales)

    # Calculate the hours for each role based on staffing needs
    manager_hours = min(36, staff_needed * time_block_hours)  # Manager works up to 36 hours per week
    supervisor_hours = max(0, (staff_needed - 1) * time_block_hours)  # Supervisor fills in remaining
    barista_hours = max(0, (staff_needed - 2) * time_block_hours)  # Baristas fill any additional hours

    # Calculate labor cost for this time block
    time_block_labor_cost = (
        manager_hours * manager_rate +
        supervisor_hours * supervisor_rate +
        barista_hours * barista_rate
    )
    return time_block_labor_cost, manager_hours, supervisor_hours, barista_hours

# Calculate the total monthly labor cost based on sales projection, day-of-week percentages, and time block percentages
def calculate_monthly_labor_costs_and_staffing(monthly_sales, manager_rate, supervisor_rate, barista_rate):
    monthly_labor_cost = 0
    staffing_summary = []

    for day, day_percentage in day_percentages.items():
        # Calculate daily sales for each day type
        daily_sales = (monthly_sales * day_percentage) / 4.3  # Average daily sales for this day type

        # Calculate labor cost and staff requirements for each time block in the day
        daily_labor_cost = 0
        day_manager_hours = 0
        day_supervisor_hours = 0
        day_barista_hours = 0
        
        for time_block, block_percentage in time_block_percentages.items():
            time_block_sales = daily_sales * block_percentage
            time_block_hours = 2 if time_block in ["7 AM - 9 AM", "12 PM - 2 PM"] else 3  # Hours per time block

            # Calculate labor cost and hours for this time block
            block_labor_cost, manager_hours, supervisor_hours, barista_hours = calculate_time_block_labor_cost(
                time_block_sales, time_block_hours, manager_rate, supervisor_rate, barista_rate
            )
            daily_labor_cost += block_labor_cost
            day_manager_hours += manager_hours
            day_supervisor_hours += supervisor_hours
            day_barista_hours += barista_hours

        # Multiply by 4.3 to get monthly labor cost for this day type
        monthly_labor_cost += daily_labor_cost * 4.3
        
        # Append to staffing summary
        staffing_summary.append({
            "Day": day,
            "Manager Hours": day_manager_hours * 4.3,
            "Supervisor Hours": day_supervisor_hours * 4.3,
            "Barista Hours": day_barista_hours * 4.3
        })
    
    return monthly_labor_cost, pd.DataFrame(staffing_summary)

# Get the labor cost and staffing summary
monthly_labor_cost, staffing_summary_df = calculate_monthly_labor_costs_and_staffing(
    monthly_sales_projection, manager_hourly_rate, supervisor_hourly_rate, barista_hourly_rate
)

# Display the results
st.subheader("Monthly Labor Cost")
st.write(f"Estimated Monthly Labor Cost: ${monthly_labor_cost:,.2f}")

st.subheader("Staffing Summary (Monthly Hours by Role)")
st.dataframe(staffing_summary_df.style.format({"Manager Hours": "{:,.2f}", "Supervisor Hours": "{:,.2f}", "Barista Hours": "{:,.2f}"}))
