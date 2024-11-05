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

# User Inputs
st.title("Coffee Shop Sales Forecaster")
monthly_sales_projection = st.number_input("Enter Monthly Sales Projection ($):", min_value=0.0, value=50000.0, step=500.0)

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

# Calculate daily sales forecast
daily_sales = {day: (monthly_sales_projection * percentage) / 4.3 for day, percentage in day_percentages.items()}

# Calculate yearly sales forecast for 3 years
sales_forecast = [monthly_sales_projection * 12 for _ in range(3)]
sales_forecast_df = pd.DataFrame({"Year": ["Year 1", "Year 2", "Year 3"], "Projected Sales": sales_forecast})

# Display and Download Sales Forecast Table
st.subheader("Sales Forecast (Yearly Totals)")
st.dataframe(sales_forecast_df.style.format({"Projected Sales": "${:,.2f}"}))
csv_sales = sales_forecast_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Sales Forecast as CSV", data=csv_sales, file_name="sales_forecast.csv", mime="text/csv")

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

# PDF Download Button
pdf_sales = create_pdf(sales_forecast_df, "Sales Forecast")
st.download_button("Download Sales Forecast as PDF", data=pdf_sales, file_name="sales_forecast.pdf", mime="application/pdf")
