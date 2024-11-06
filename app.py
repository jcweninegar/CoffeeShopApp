import streamlit as st
import pandas as pd

# Assumptions
capture_rate_years = {
    1: [0.0062, 0.0057, 0.0070, 0.0068, 0.0071, 0.0074, 0.0075, 0.0084, 0.0080, 0.0084, 0.0080, 0.0077],
    2: [0.0130, 0.0119, 0.0147, 0.0143, 0.0148, 0.0155, 0.0158, 0.0176, 0.0167, 0.0177, 0.0168, 0.0163],
    3: [0.0167, 0.0152, 0.0188, 0.0183, 0.0190, 0.0199, 0.0202, 0.0225, 0.0214, 0.0227, 0.0215, 0.0208]
}
hourly_sales_distribution = [0.20, 0.20, 0.10, 0.075, 0.075, 0.05, 0.10, 0.10, 0.05, 0.05]
daily_sales_distribution = [0.1399, 0.15, 0.1599, 0.1599, 0.17, 0.2199]  # Monday to Saturday
manager_hours = 36  # on-floor hours
shift_supervisor_min_hours = 24
payroll_tax_rate = 0.18
benefits_per_employee = 50  # monthly benefits/expenses per employee

# App Interface
st.title("Coffee Shop 3-Year Sales, Labor, and Staffing Forecast")

# User Inputs
traffic_count = st.number_input("Average Daily Traffic Count", min_value=0, step=1)
average_sale = st.number_input("Average Sale ($)", min_value=0.0, step=0.1)
days_open = st.number_input("Days Open per Week", min_value=1, max_value=7, step=1)
operating_hours = st.slider("Operating Hours (Start and End Times)", value=(7, 17), min_value=0, max_value=24)
manager_rate = st.number_input("Manager Hourly Rate ($)", min_value=0.0, step=0.1)
shift_supervisor_rate = st.number_input("Shift Supervisor Hourly Rate ($)", min_value=0.0, step=0.1)
barista_rate = st.number_input("Barista Hourly Rate ($)", min_value=0.0, step=0.1)

# Sales Forecast Calculation
def calculate_sales_forecast():
    forecast = []
    for year in range(1, 4):
        monthly_sales = []
        for month, capture_rate in enumerate(capture_rate_years[year], start=1):
            daily_sales = traffic_count * capture_rate * average_sale
            monthly_sales.append(daily_sales * days_open * 4.3)
        forecast.append(monthly_sales)
    return pd.DataFrame(forecast, index=["Year 1", "Year 2", "Year 3"], columns=[f"Month {i+1}" for i in range(12)])

# Labor Cost Calculation based on sales forecast
def calculate_labor_costs(sales_forecast):
    labor_forecast = []
    for index, monthly_sales in sales_forecast.iterrows():
        monthly_labor_costs = []
        for sales in monthly_sales:
            weekly_labor_cost = calculate_weekly_labor_cost(sales / days_open / 4.3)
            monthly_labor_cost = weekly_labor_cost * 4.3
            monthly_labor_costs.append(monthly_labor_cost)
        labor_forecast.append(monthly_labor_costs)
    return pd.DataFrame(labor_forecast, index=["Year 1", "Year 2", "Year 3"], columns=[f"Month {i+1}" for i in range(12)])

def calculate_weekly_labor_cost(daily_sales):
    # Calculate weekly coverage
    total_hours_weekly = (operating_hours[1] - operating_hours[0]) * days_open
    opening_closing_hours = days_open * 2  # 1 hour per day (30 min open, 30 min close)
    manager_hours_weekly = manager_hours
    shift_supervisor_hours_weekly = max(shift_supervisor_min_hours, total_hours_weekly - manager_hours_weekly)
    barista_hours_weekly = total_hours_weekly - (manager_hours_weekly + shift_supervisor_hours_weekly + opening_closing_hours)
    
    # Calculate costs
    manager_cost_weekly = manager_hours_weekly * manager_rate
    shift_supervisor_cost_weekly = shift_supervisor_hours_weekly * shift_supervisor_rate
    barista_cost_weekly = barista_hours_weekly * barista_rate
    
    # Total weekly labor cost with payroll tax and benefits
    weekly_total_labor_cost = manager_cost_weekly + shift_supervisor_cost_weekly + barista_cost_weekly
    payroll_expenses = weekly_total_labor_cost * payroll_tax_rate
    total_weekly_labor_cost = weekly_total_labor_cost + payroll_expenses + (benefits_per_employee * 3)
    
    return total_weekly_labor_cost

# Staffing Requirements Report
def staffing_report():
    total_hours_weekly = (operating_hours[1] - operating_hours[0]) * days_open
    manager_hours_weekly = manager_hours
    shift_supervisor_hours_weekly = max(shift_supervisor_min_hours, total_hours_weekly - manager_hours_weekly)
    barista_hours_weekly = total_hours_weekly - (manager_hours_weekly + shift_supervisor_hours_weekly)
    
    staffing_data = {
        "Role": ["Manager", "Shift Supervisor", "Barista"],
        "Weekly Hours": [manager_hours_weekly, shift_supervisor_hours_weekly, barista_hours_weekly],
        "Hourly Rate": [manager_rate, shift_supervisor_rate, barista_rate],
        "Weekly Cost": [
            manager_hours_weekly * manager_rate,
            shift_supervisor_hours_weekly * shift_supervisor_rate,
            barista_hours_weekly * barista_rate
        ]
    }
    return pd.DataFrame(staffing_data)

# Generate Results
sales_forecast_df = calculate_sales_forecast()
labor_forecast_df = calculate_labor_costs(sales_forecast_df)
staffing_report_df = staffing_report()

# Display Results
st.subheader("3-Year Sales Forecast")
st.write(sales_forecast_df)

st.subheader("3-Year Labor Cost Forecast")
st.write(labor_forecast_df)

st.subheader("Staffing Requirements Report")
st.write(staffing_report_df)
