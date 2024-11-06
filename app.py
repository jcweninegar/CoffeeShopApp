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
st.title("24-Hour Coffee Shop Sales and Staffing Forecast")

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

day_percentage = st.slider(
    "Select Day's Sales Percentage of Monthly Sales", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.15, 
    step=0.01,
    help="Percentage of monthly sales expected on this day (e.g., 0.15 for 15%)."
)

year = st.selectbox(
    "Select Year of Operation",
    options=[1, 2, 3],
    help="Choose the operational year for adjusted capture rates."
)

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

# Coverage Rules for Staff based on Sales
st.markdown("### Staffing Coverage Rules")
st.markdown("""
- **Base Coverage**: At least 2 employees on the floor at all times.
- **Sales Thresholds**:
    - 3 employees if sales exceed $200/hour.
    - 4 employees if sales exceed $500/hour.
    - 5 employees if sales exceed $700/hour.
""")

# Calculate monthly sales for each month in the selected year
capture_rates = capture_rate_years[year]
monthly_sales_estimates = [
    (average_daily_traffic * rate * average_sale * days_open_per_week * 4.3) for rate in capture_rates
]

# Display estimated monthly sales
monthly_sales_df = pd.DataFrame({
    "Month": ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"],
    "Estimated Monthly Sales": [round(sales, 2) for sales in monthly_sales_estimates]
})

st.subheader("Estimated Monthly Sales for Selected Year")
st.write(monthly_sales_df)

# Total estimated monthly sales for the year
total_estimated_sales = sum(monthly_sales_estimates)
st.write(f"**Total Estimated Sales for Year {year}:** ${total_estimated_sales:,.2f}")

# Step 3: Calculate hourly sales and determine required coverage
hourly_coverage = []
for hour, percentage in enumerate(hourly_sales_percentages):
    hourly_sales = (total_estimated_sales / 12) * day_percentage * percentage  # Assuming average monthly sales / day pattern
    
    # Determine coverage based on hourly sales thresholds
    if hourly_sales > 700:
        staff_needed = 5
    elif hourly_sales > 500:
        staff_needed = 4
    elif hourly_sales > 200:
        staff_needed = 3
    else:
        staff_needed = 2  # Minimum coverage
    
    # Format each hour in 12-hour format with AM/PM
    hour_label = f"{hour % 12 or 12}{'AM' if hour < 12 else 'PM'} - {(hour + 1) % 12 or 12}{'AM' if hour + 1 < 12 else 'PM'}"
    hourly_coverage.append({
        "Hour": hour_label,
        "Hourly Sales": round(hourly_sales, 2),
        "Staff Needed": staff_needed
    })

# Step 4: Convert to DataFrame for easier display and calculation of daily totals
coverage_df = pd.DataFrame(hourly_coverage)

# Step 5: Calculate total daily and weekly coverage
daily_total_coverage = coverage_df["Staff Needed"].sum()
weekly_total_coverage = daily_total_coverage * days_open_per_week

# Display Results
st.subheader("Hourly Coverage Based on Sales")
st.write(coverage_df)

st.subheader("Total Coverage Needed")
st.write(f"**Total Daily Coverage Needed**: {daily_total_coverage} employee-hours")
st.write(f"**Total Weekly Coverage Needed**: {weekly_total_coverage} employee-hours")
