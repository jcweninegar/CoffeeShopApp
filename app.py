import streamlit as st
import pandas as pd
from fpdf import FPDF

# Load CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Logo
st.markdown('<img src="3.png" class="logo">', unsafe_allow_html=True)

# Title
st.title("Coffee Shop Sales & Labor Forecaster")

# Input Fields
traffic_count = st.number_input("Enter daily traffic count:", min_value=0, step=1, value=1500)
competition = st.number_input("Enter the number of coffee shops within 2 miles:", min_value=0, step=1, value=2)
days_open = st.number_input("Days open per week:", min_value=1, max_value=7, step=1, value=6)
average_sale = st.number_input("Average sale amount ($):", min_value=0.0, step=0.01, value=10.00)

# Hourly Rates for Labor Cost Calculations
manager_hourly_rate = st.number_input("Enter Manager Hourly Rate ($):", min_value=0.0, step=0.01)
supervisor_hourly_rate = st.number_input("Enter Supervisor Hourly Rate ($):", min_value=0.0, step=0.01)
barista_hourly_rate = st.number_input("Enter Part-Time Barista Hourly Rate ($):", min_value=0.0, step=0.01)

# Conversion Rates (Yearly progression by month for first 3 years)
conversion_rates = [
    [0.62, 0.57, 0.70, 0.68, 0.71, 0.74, 0.75, 0.84, 0.80, 0.84, 0.80, 0.77], # Year 1
    [1.30, 1.19, 1.47, 1.43, 1.48, 1.55, 1.58, 1.76, 1.67, 1.77, 1.68, 1.63], # Year 2
    [1.67, 1.52, 1.88, 1.83, 1.90, 1.99, 2.02, 2.25, 2.14, 2.27, 2.15, 2.08]  # Year 3
]

# Calculate Monthly Sales Forecast
def calculate_monthly_sales(traffic, competition, days_open, average_sale, rates):
    sales = []
    adjustment_factor = max(1 - (0.1 * competition), 0.5)  # Adjust for competition, capped at 50%
    for year_rates in rates:
        year_sales = []
        for rate in year_rates:
            monthly_sales = traffic * rate * adjustment_factor * days_open * 4.3 * average_sale / 100
            year_sales.append(monthly_sales)
        sales.append(year_sales)
    return sales

# Calculate Monthly Labor Forecast
def calculate_monthly_labor(sales_projection, manager_rate, supervisor_rate, barista_rate):
    # Use percentages and time block logic to estimate labor needs
    day_percentages = {"Monday": 0.1399, "Tuesday": 0.15, "Wednesday": 0.1599, "Thursday": 0.1599, "Friday": 0.17, "Saturday": 0.2199}
    time_block_percentages = {"7 AM - 9 AM": 0.4, "9 AM - 12 PM": 0.25, "12 PM - 2 PM": 0.15, "2 PM - 5 PM": 0.2}
    
    def daily_labor_cost(daily_sales):
        labor_cost = 0
        for block, perc in time_block_percentages.items():
            block_sales = daily_sales * perc
            hours = 2 if block in ["7 AM - 9 AM", "12 PM - 2 PM"] else 3
            hourly_sales = block_sales / hours
            if hourly_sales <= 200:
                staff = 2
            elif hourly_sales <= 500:
                staff = 3
            elif hourly_sales <= 700:
                staff = 4
            else:
                staff = 5
            
            manager_hours = min(2, staff) * hours
            supervisor_hours = max(0, staff - 2) * hours
            barista_hours = max(0, staff - 3) * hours
            
            labor_cost += manager_hours * manager_rate + supervisor_hours * supervisor_rate + barista_hours * barista_rate
        return labor_cost

    labor_costs = []
    for year_sales in sales_projection:
        year_labor = []
        for monthly_sales in year_sales:
            daily_sales = monthly_sales / 4.3 / days_open
            monthly_labor_cost = daily_labor_cost(daily_sales) * 4.3 * days_open
            year_labor.append(monthly_labor_cost)
        labor_costs.append(year_labor)
    return labor_costs

# Perform Calculations
monthly_sales_forecast = calculate_monthly_sales(traffic_count, competition, days_open, average_sale, conversion_rates)
monthly_labor_forecast = calculate_monthly_labor(monthly_sales_forecast, manager_hourly_rate, supervisor_hourly_rate, barista_hourly_rate)

# Display Results in a Table
st.subheader("3-Year Monthly Sales and Labor Forecast")
forecast_data = []
for year in range(3):
    for month in range(12):
        forecast_data.append({
            "Year": year + 1,
            "Month": month + 1,
            "Projected Sales ($)": monthly_sales_forecast[year][month],
            "Projected Labor Cost ($)": monthly_labor_forecast[year][month]
        })
forecast_df = pd.DataFrame(forecast_data)

st.dataframe(forecast_df.style.format({"Projected Sales ($)": "${:,.2f}", "Projected Labor Cost ($)": "${:,.2f}"}))

# Option to Download Forecast as CSV
st.download_button("Download Forecast as CSV", data=forecast_df.to_csv(index=False), file_name="forecast.csv")

# Option to Download Forecast as PDF
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3-Year Monthly Sales and Labor Forecast", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    for _, row in forecast_df.iterrows():
        pdf.cell(0, 10, f"Year {int(row['Year'])}, Month {int(row['Month'])}: Sales = ${row['Projected Sales ($)']:.2f}, Labor = ${row['Projected Labor Cost ($)']:.2f}", ln=True)
    return pdf.output(dest="S").encode("latin1")

st.download_button("Download Forecast as PDF", data=download_pdf(), file_name="forecast.pdf", mime="application/pdf")
