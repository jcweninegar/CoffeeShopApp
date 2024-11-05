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
days_open_per_week = st.number_input("Days Open per Week:", min_value=1, max_value=7, value=6)

# Calculate total operating hours per week
hours_open_per_day = close_hour - open_hour
total_hours_per_week = hours_open_per_day * days_open_per_week

# Manager hours per week
manager_hours_per_week = 36

# Calculate shift supervisor required hours
supervisor_hours_needed = total_hours_per_week - manager_hours_per_week
supervisor_hours_per_week = min(supervisor_hours_needed, 40)

# Any remaining hours will be covered by baristas
barista_hours_per_week = max(0, supervisor_hours_needed - supervisor_hours_per_week)

# Function to determine the staff count needed based on hourly sales
def determine_staff_needed(hourly_sales):
    for threshold, staff_count in STAFF_THRESHOLDS.items():
        if hourly_sales <= threshold:
            return staff_count

# Function to calculate daily labor and staffing requirements
def calculate_daily_labor_and_staffing(daily_sales, manager_rate, supervisor_rate, barista_rate):
    daily_labor_cost = 0
    total_manager_hours = 0
    total_supervisor_hours = 0
    total_barista_hours = 0
    
    for time_block, block_percentage in time_block_percentages.items():
        # Calculate time block sales and hours
        time_block_sales = daily_sales * block_percentage
        time_block_hours = 2 if time_block in ["7 AM - 9 AM", "12 PM - 2 PM"] else 3
        
        # Determine staffing needs
        hourly_sales = time_block_sales / time_block_hours
        staff_needed = determine_staff_needed(hourly_sales)
        
        # Allocate hours based on staffing rules
        manager_hours = min(manager_hours_per_week - total_manager_hours, staff_needed * time_block_hours)
        remaining_hours = staff_needed * time_block_hours - manager_hours

        # Allocate shift supervisor hours based on remaining coverage
        supervisor_hours = min(supervisor_hours_per_week - total_supervisor_hours, remaining_hours)
        remaining_hours -= supervisor_hours

        # Allocate any remaining hours to baristas
        barista_hours = remaining_hours

        # Update total hours for each role
        total_manager_hours += manager_hours
        total_supervisor_hours += supervisor_hours
        total_barista_hours += barista_hours
        
        # Calculate cost for this time block
        daily_labor_cost += (manager_hours * manager_rate) + (supervisor_hours * supervisor_rate) + (barista_hours * barista_rate)
        
    return daily_labor_cost, total_manager_hours, total_supervisor_hours, total_barista_hours

# Calculate weekly labor costs and staffing requirements for each day
weekly_labor_cost = 0
staffing_summary = []

for day, percentage in day_percentages.items():
    daily_sales = (monthly_sales_projection * percentage) / 4.3
    daily_labor_cost, manager_hours, supervisor_hours, barista_hours = calculate_daily_labor_and_staffing(
        daily_sales, manager_hourly_rate, supervisor_hourly_rate, barista_hourly_rate
    )
    weekly_labor_cost += daily_labor_cost
    staffing_summary.append({
        "Day": day,
        "Manager Hours": manager_hours,
        "Shift Supervisor Hours": supervisor_hours,
        "Barista Hours": barista_hours,
        "Daily Labor Cost": daily_labor_cost
    })

# Convert staffing summary to DataFrame
staffing_summary_df = pd.DataFrame(staffing_summary)

# Display Results
st.subheader("Weekly Labor Cost")
st.write(f"Estimated Weekly Labor Cost: ${weekly_labor_cost:,.2f}")

st.subheader("Staffing Requirements (Daily Breakdown)")
st.dataframe(staffing_summary_df.style.format({
    "Manager Hours": "{:.2f}",
    "Shift Supervisor Hours": "{:.2f}",
    "Barista Hours": "{:.2f}",
    "Daily Labor Cost": "${:,.2f}"
}))
