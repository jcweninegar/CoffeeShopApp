import streamlit as st
import pandas as pd
import numpy as np

st.title("Coffee Shop Sales & Labor Forecaster")

# User inputs
traffic_count = st.number_input("Enter daily traffic count:", min_value=0, value=1500, step=1)
competition = st.number_input("Enter the number of coffee shops within 2 miles:", min_value=0, value=2, step=1)
days_open = st.number_input("Days open per week:", min_value=1, max_value=7, value=6, step=1)
average_sale = st.number_input("Average sale amount ($):", min_value=0.0, value=10.0, step=0.5)

# Labor cost inputs
manager_rate = st.number_input("Enter Manager Hourly Rate ($):", min_value=0.0, value=20.0, step=0.5)
supervisor_rate = st.number_input("Enter Supervisor Hourly Rate ($):", min_value=0.0, value=15.0, step=0.5)
barista_rate = st.number_input("Enter Part-Time Barista Hourly Rate ($):", min_value=0.0, value=12.0, step=0.5)

# Conversion rates by month (3 years)
conversion_rates = [
    [0.62, 0.57, 0.70, 0.68, 0.71, 0.74, 0.75, 0.84, 0.80, 0.84, 0.80, 0.77],
    [1.30, 1.19, 1.47, 1.43, 1.48, 1.55, 1.58, 1.76, 1.67, 1.77, 1.68, 1.63],
    [1.67, 1.52, 1.88, 1.83, 1.90, 1.99, 2.02, 2.25, 2.14, 2.27, 2.15, 2.08]
]

# Calculate monthly sales forecasts
def calculate_monthly_sales(traffic_count, competition, days_open, average_sale, conversion_rates):
    monthly_sales = []
    for year_rates in conversion_rates:
        year_sales = []
        for rate in year_rates:
            monthly_sales_projection = traffic_count * days_open * 4.3 * (rate / (competition + 1)) * average_sale / 100
            year_sales.append(monthly_sales_projection)
        monthly_sales.append(year_sales)
    return monthly_sales

# Calculate monthly labor costs
def calculate_monthly_labor_costs(monthly_sales, manager_rate, supervisor_rate, barista_rate):
    labor_costs = []
    for year_sales in monthly_sales:
        year_labor = []
        for sales in year_sales:
            # Determine staff needed based on sales volume
            if sales / (4.3 * 6) > 700:  # Assume sales divided by days per month and hours per day
                staff_needed = 5
            elif sales / (4.3 * 6) > 500:
                staff_needed = 4
            elif sales / (4.3 * 6) > 200:
                staff_needed = 3
            else:
                staff_needed = 2
            
            # Manager works 36 hours per week, supervisor or barista fills the rest
            manager_hours = min(36, 6 * staff_needed)  # 6 days per week
            supervisor_hours = (staff_needed * 6 * 4.3) - manager_hours  # Remaining hours per month

            # Calculate monthly labor cost
            monthly_labor_cost = (
                (manager_hours * manager_rate) +
                (supervisor_hours * supervisor_rate) +
                ((staff_needed - 2) * supervisor_hours * barista_rate)
            )
            year_labor.append(monthly_labor_cost)
        labor_costs.append(year_labor)
    return labor_costs

# Get sales and labor forecasts
monthly_sales = calculate_monthly_sales(traffic_count, competition, days_open, average_sale, conversion_rates)
monthly_labor_costs = calculate_monthly_labor_costs(monthly_sales, manager_rate, supervisor_rate, barista_rate)

# Prepare data for display
def prepare_dataframe(data, title):
    columns = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Total"]
    rows = ["Year 1", "Year 2", "Year 3"]
    df = pd.DataFrame(data, columns=columns[:-1], index=rows)
    df["Total"] = df.sum(axis=1)
    st.subheader(title)
    st.dataframe(df.style.format("${:,.2f}"))
    return df

# Show sales and labor forecasts
sales_df = prepare_dataframe(monthly_sales, "Sales Forecast")
labor_df = prepare_dataframe(monthly_labor_costs, "Labor Cost Forecast")
