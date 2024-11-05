import streamlit as st
import pandas as pd

# Load CSS styles
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Logo
st.image("3.png", width=200)  # Ensure this matches your logo filename

# Title
st.title("Coffee Shop Sales Forecaster")

# Monthly conversion rates for the first 3 years
conversion_rates = [
    [0.62, 0.57, 0.70, 0.68, 0.71, 0.74, 0.75, 0.84, 0.80, 0.84, 0.80, 0.77],  # Year 1
    [1.30, 1.19, 1.47, 1.43, 1.48, 1.55, 1.58, 1.76, 1.67, 1.77, 1.68, 1.63],  # Year 2
    [1.67, 1.52, 1.88, 1.83, 1.90, 1.99, 2.02, 2.25, 2.14, 2.27, 2.15, 2.08]   # Year 3
]

# Function to adjust conversion rates based on competition
def adjust_conversion_rate(base_rate, coffee_shops_nearby):
    if coffee_shops_nearby == 0:
        return base_rate * 1.1  # Increase by 10% if no competition
    elif coffee_shops_nearby <= 2:
        return base_rate * 1.05  # Increase by 5% if few competitors
    elif coffee_shops_nearby <= 5:
        return base_rate * 1.0  # No adjustment for moderate competition
    else:
        return base_rate * 0.9  # Decrease by 10% if heavy competition

# Function to calculate monthly sales forecast considering competition
def calculate_monthly_sales(traffic_count, coffee_shops_nearby, days_open, avg_sale):
    all_monthly_sales = []

    for year in range(3):
        monthly_sales = []
        conversion_rate_year = conversion_rates[year]

        for month_rate in conversion_rate_year:
            # Adjust the conversion rate based on competition
            adjusted_rate = adjust_conversion_rate(month_rate, coffee_shops_nearby) / 100
            # Calculate estimated customers per day using adjusted rate
            estimated_customers = traffic_count * adjusted_rate
            # Calculate monthly sales
            monthly_sales.append(estimated_customers * days_open * 4.3 * avg_sale)

        all_monthly_sales.append(monthly_sales)

    return all_monthly_sales

# User inputs
traffic_count = st.number_input("Enter daily traffic count:", min_value=0)
coffee_shops_nearby = st.number_input("Enter the number of coffee shops within 2 miles:", min_value=0)
days_open = st.number_input("Days open per week:", min_value=1, max_value=7, value=6)
avg_sale = st.number_input("Average sale amount ($):", min_value=0.0, step=0.01)

# Calculate and display forecasted sales
if st.button("Calculate Monthly Sales Forecast"):
    all_monthly_sales = calculate_monthly_sales(traffic_count, coffee_shops_nearby, days_open, avg_sale)

    # Create a DataFrame to display results with Years as Rows and Months as Columns
    sales_data = {
        "Year": [1, 2, 3],
        "January": [all_monthly_sales[0][0], all_monthly_sales[1][0], all_monthly_sales[2][0]],
        "February": [all_monthly_sales[0][1], all_monthly_sales[1][1], all_monthly_sales[2][1]],
        "March": [all_monthly_sales[0][2], all_monthly_sales[1][2], all_monthly_sales[2][2]],
        "April": [all_monthly_sales[0][3], all_monthly_sales[1][3], all_monthly_sales[2][3]],
        "May": [all_monthly_sales[0][4], all_monthly_sales[1][4], all_monthly_sales[2][4]],
        "June": [all_monthly_sales[0][5], all_monthly_sales[1][5], all_monthly_sales[2][5]],
        "July": [all_monthly_sales[0][6], all_monthly_sales[1][6], all_monthly_sales[2][6]],
        "August": [all_monthly_sales[0][7], all_monthly_sales[1][7], all_monthly_sales[2][7]],
        "September": [all_monthly_sales[0][8], all_monthly_sales[1][8], all_monthly_sales[2][8]],
        "October": [all_monthly_sales[0][9], all_monthly_sales[1][9], all_monthly_sales[2][9]],
        "November": [all_monthly_sales[0][10], all_monthly_sales[1][10], all_monthly_sales[2][10]],
        "December": [all_monthly_sales[0][11], all_monthly_sales[1][11], all_monthly_sales[2][11]],
        "Total": [sum(all_monthly_sales[0]), sum(all_monthly_sales[1]), sum(all_monthly_sales[2])]
    }

    # Convert to DataFrame
    df_sales = pd.DataFrame(sales_data)

    # Display the DataFrame in Streamlit
    st.subheader("Monthly Sales Forecast")
    st.dataframe(df_sales)  # Display the DataFrame as a table

