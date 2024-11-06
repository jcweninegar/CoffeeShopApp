import streamlit as st
import pandas as pd

# Function to calculate weekly hours and staffing needs
def calculate_staffing(monthly_sales, days_per_week, manager_rate, supervisor_rate, barista_rate):
    # Example percentages for each day of the week (based on sales distribution)
    day_percentages = {
        'Monday': 13.99,
        'Tuesday': 15.00,
        'Wednesday': 15.99,
        'Thursday': 15.99,
        'Friday': 17.00,
        'Saturday': 21.99
    }

    # Calculate daily sales from monthly sales
    daily_sales = {day: (monthly_sales * (percentage / 100)) / 4.3 for day, percentage in day_percentages.items()}
    
    # Hourly staffing needs based on time blocks
    time_block_percentages = {
        "7-9 AM": 0.40,
        "9-12 PM": 0.25,
        "12-2 PM": 0.15,
        "2-5 PM": 0.20
    }

    # Calculate hours per day for each role based on sales and coverage logic
    total_weekly_hours_needed = 0
    for day, sales in daily_sales.items():
        for block, percentage in time_block_percentages.items():
            block_sales = sales * percentage
            if block_sales > 700:
                staff_needed = 5
            elif block_sales > 500:
                staff_needed = 4
            elif block_sales > 200:
                staff_needed = 3
            else:
                staff_needed = 2
            total_weekly_hours_needed += staff_needed * (3 if block == "9-12 PM" else 2)
    
    # Calculate supervisory and barista hours
    manager_hours = 36  # Manager fixed on-floor hours
    supervisory_coverage = total_weekly_hours_needed - manager_hours
    shift_supervisor_hours = min(supervisory_coverage, 80)  # Max 40 hours per supervisor, 2 supervisors for redundancy
    barista_hours = total_weekly_hours_needed - (manager_hours + shift_supervisor_hours)

    # Weekly costs based on role rates
    weekly_cost_manager = manager_hours * manager_rate
    weekly_cost_supervisor = shift_supervisor_hours * supervisor_rate
    weekly_cost_barista = barista_hours * barista_rate

    # Total weekly cost with a payroll expense assumption (e.g., 20% on top)
    payroll_expense = 0.20
    total_weekly_cost = (weekly_cost_manager + weekly_cost_supervisor + weekly_cost_barista) * (1 + payroll_expense)

    # Create data for the staffing report table
    staffing_data = {
        "Role": ["Manager", "Shift Supervisor", "Barista"],
        "Weekly Hours": [manager_hours, shift_supervisor_hours, barista_hours],
        "Hourly Rate": [manager_rate, supervisor_rate, barista_rate],
        "Weekly Cost": [weekly_cost_manager, weekly_cost_supervisor, weekly_cost_barista]
    }
    staffing_df = pd.DataFrame(staffing_data)

    return staffing_df, total_weekly_cost

# Streamlit app layout
st.title("Coffee Shop Sales & Staffing Forecaster")

# Input fields
monthly_sales = st.number_input("Enter Monthly Sales Projection ($):", min_value=0, value=30000)
days_per_week = st.slider("Days open per week:", min_value=1, max_value=7, value=6)
manager_rate = st.number_input("Enter Manager Hourly Rate ($):", min_value=0.0, value=18.0)
supervisor_rate = st.number_input("Enter Supervisor Hourly Rate ($):", min_value=0.0, value=15.0)
barista_rate = st.number_input("Enter Barista Hourly Rate ($):", min_value=0.0, value=12.0)

# Calculate staffing requirements
staffing_df, total_weekly_cost = calculate_staffing(monthly_sales, days_per_week, manager_rate, supervisor_rate, barista_rate)

# Display the Staffing Requirements Report
st.header("Staffing Requirements Report")
st.table(staffing_df)

# Display the total weekly cost
st.write(f"**Total Weekly Cost (including payroll expense):** ${total_weekly_cost:.2f}")

# Summary of staffing needs
total_shift_supervisors = 2  # Based on redundancy requirement
total_baristas = max(1, (staffing_df["Weekly Hours"][2] // 24) + 1)  # Estimate baristas based on total barista hours needed
st.write(f"You need 1 manager, {total_shift_supervisors} shift supervisors, and approximately {total_baristas} baristas based on your staffing requirements.")
