import streamlit as st
import pandas as pd
from fpdf import FPDF

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

# Input fields for hours of operation in 12-hour format
st.subheader("Hours of Operation")

# Opening Time
open_hour_12 = st.number_input("Opening Hour:", min_value=1, max_value=12, value=7)
open_am_pm = st.selectbox("AM/PM for Opening Time", ["AM", "PM"])

# Closing Time
close_hour_12 = st.number_input("Closing Hour:", min_value=1, max_value=12, value=5)
close_am_pm = st.selectbox("AM/PM for Closing Time", ["AM", "PM"])

# Convert 12-hour format to 24-hour format
open_hour = open_hour_12 % 12 + (12 if open_am_pm == "PM" else 0)
close_hour = close_hour_12 % 12 + (12 if close_am_pm == "PM" else 0)

# Calculate hours open per day
hours_open_per_day = close_hour - open_hour if close_hour > open_hour else (24 - open_hour + close_hour)

# Days open per week
days_open_per_week = st.number_input("Days Open per Week:", min_value=1, max_value=7, value=6)

# Calculate total operating hours per week
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

# Cache the function to improve performance on recalculations
@st.cache_data
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

# Sales Forecast, Labor Forecast, and Staffing Requirements Tables
sales_forecast_df = pd.DataFrame({"Year": ["Year 1", "Year 2", "Year 3"], "Projected Sales": [monthly_sales_projection * 12 for _ in range(3)]})
labor_forecast_df = pd.DataFrame({"Year": ["Year 1", "Year 2", "Year 3"], "Projected Labor Cost": [weekly_labor_cost * 4.3 * 12 for _ in range(3)]})

# Display and Download Tables as CSV
st.subheader("Sales Forecast (Yearly Totals)")
st.dataframe(sales_forecast_df.style.format({"Projected Sales": "${:,.2f}"}))
csv_sales = sales_forecast_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Sales Forecast as CSV", data=csv_sales, file_name="sales_forecast.csv", mime="text/csv")

st.subheader("Labor Forecast (Yearly Total Cost)")
st.dataframe(labor_forecast_df.style.format({"Projected Labor Cost": "${:,.2f}"}))
csv_labor = labor_forecast_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Labor Forecast as CSV", data=csv_labor, file_name="labor_forecast.csv", mime="text/csv")

st.subheader("Staffing Requirements (Monthly Hours by Role)")
st.dataframe(staffing_summary_df.style.format({"Manager Hours": "{:,.2f}", "Shift Supervisor Hours": "{:,.2f}", "Barista Hours": "{:,.2f}", "Daily Labor Cost": "${:,.2f}"}))
csv_staffing = staffing_summary_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Staffing Requirements as CSV", data=csv_staffing, file_name="staffing_requirements.csv", mime="text/csv")

# PDF Download Function
def create_pdf(dataframe, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    
    # Add table headers
    col_widths = [pdf.get_string_width(col) + 10 for col in dataframe.columns]
    pdf.set_fill_color(200, 220, 255)
    for i, col in enumerate(dataframe.columns):
        pdf.cell(col_widths[i], 10, col, border=1, fill=True)
    pdf.ln()

    # Add table rows
    for _, row in dataframe.iterrows():
        for i, col in enumerate(dataframe.columns):
            pdf.cell(col_widths[i], 10, str(row[col]), border=1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin1')

# PDF Download Buttons
pdf_sales = create_pdf(sales_forecast_df, "Sales Forecast")
st.download_button("Download Sales Forecast as PDF", data=pdf_sales, file_name="sales_forecast.pdf", mime="application/pdf")

pdf_labor = create_pdf(labor_forecast_df, "Labor Forecast")
st.download_button("Download Labor Forecast as PDF", data=pdf_labor, file_name="labor_forecast.pdf", mime="application/pdf")

pdf_staffing = create_pdf(staffing_summary_df, "Staffing Requirements")
st.download_button("Download Staffing Requirements as PDF", data=pdf_staffing, file_name="staffing_requirements.pdf", mime="application/pdf")

