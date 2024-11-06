import streamlit as st
import pandas as pd

# Define capture rates for each year and month
capture_rate_years = {
    1: [0.0062, 0.0057, 0.0070, 0.0068, 0.0071, 0.0074, 0.0075, 0.0084, 0.0080, 0.0084, 0.0080, 0.0077],
    2: [0.0130, 0.0119, 0.0147, 0.0143, 0.0148, 0.0155, 0.0158, 0.0176, 0.0167, 0.0177, 0.0168, 0.0163],
    3: [0.0167, 0.0152, 0.0188, 0.0183, 0.0190, 0.0199, 0.0202, 0.0225, 0.0214, 0.0227, 0.0215, 0.0208]
}

# Hourly and daily sales percentages
hourly_sales_percentages = [0.20, 0.20, 0.0833, 0.0833, 0.0833, 0.075, 0.075, 0.0667, 0.0667, 0.0667]
daily_sales_percentages = [0.1399, 0.15, 0.1599, 0.1599, 0.17, 0.2199]  # Monday to Saturday

# Streamlit App Interface
st.title("Coffee Shop Sales and Labor Forecaster")

# User Inputs
average_daily_traffic = st.number_input("Average Daily Traffic Count", min_value=0, step=1)
average_sale = st.number_input("Average Sale Amount ($)", min_value=0.0, step=0.1)
days_open_per_week = st.number_input("Days Open per Week", min_value=1, max_value=7, step=1)
number_of_competitors = st.number_input("Number of Coffee Shops within a 2-Mile Radius", min_value=0, step=1)
manager_rate = st.number_input("Manager Hourly Rate ($)", min_value=0.0, step=0.1)
shift_supervisor_rate = st.number_input("Shift Supervisor Hourly Rate ($)", min_value=0.0, step=0.1)
barista_rate = st.number_input("Barista Hourly Rate ($)", min_value=0.0, step=0.1)
payroll_tax_rate = 0.15  # Assuming a 15% payroll tax and benefits rate

# Helper function to convert 24-hour format to 12-hour format with AM/PM
def convert_to_12_hour_format(hour):
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour - 12}:00 PM"

# Operating Hours Slider
operating_hours = st.slider(
    "Operating Hours (Start and End Times)", 
    value=(7, 17), 
    min_value=0, 
    max_value=24, 
    format="%d:00",
    help="Select the start and end times for daily operation in 24-hour format."
)

# Convert the selected start and end times to 12-hour format for display
start_time, end_time = operating_hours
start_time_12hr = convert_to_12_hour_format(start_time)
end_time_12hr = convert_to_12_hour_format(end_time)

# Display the selected times in 12-hour format with AM/PM
st.write(f"**Selected Operating Hours:** {start_time_12hr} - {end_time_12hr}")

# Adjusted hourly rates to account for payroll taxes and benefits
effective_manager_rate = manager_rate * (1 + payroll_tax_rate)
effective_shift_supervisor_rate = shift_supervisor_rate * (1 + payroll_tax_rate)
effective_barista_rate = barista_rate * (1 + payroll_tax_rate)

# Button to Generate Projections
if st.button("Generate Projections"):

    # Adjust capture rate based on competition
    def adjust_capture_rate(rate, competitors):
        return rate * (1 - competitors * 0.05)

    # Initialize DataFrames to store results
    monthly_labor_cost = []
    yearly_sales_data = {}

    # Loop through each year and month
    for year in range(1, 4):
        capture_rates = capture_rate_years[year]
        monthly_sales_estimates = []
        monthly_labor_estimates = []

        for month_index, capture_rate in enumerate(capture_rates):
            
            # Calculate total monthly sales and weekly sales
            monthly_sales = average_daily_traffic * adjust_capture_rate(capture_rate, number_of_competitors) * average_sale * days_open_per_week * 4.3
            weekly_sales = monthly_sales / 4.3

            # Calculate daily sales estimates
            daily_sales = [weekly_sales * pct for pct in daily_sales_percentages]

            # Determine employee hours for each day based on hourly sales percentages
            total_employee_hours = 0
            for day_sales in daily_sales:
                hourly_sales = [day_sales * pct for pct in hourly_sales_percentages]
                
                for hour_sales in hourly_sales:
                    if hour_sales > 700:
                        total_employee_hours += 5
                    elif hour_sales > 500:
                        total_employee_hours += 4
                    elif hour_sales > 200:
                        total_employee_hours += 3
                    else:
                        total_employee_hours += 2
                
                total_employee_hours += 2  # Additional 1 hour (30 min open and 30 min close)

            # Calculate supervisory and barista hours
            total_supervisory_hours = 66  # 10 hours per day * 6 days + 1 hour for opening/closing
            manager_hours = 36
            shift_supervisor_hours = total_supervisory_hours - manager_hours
            barista_hours = total_employee_hours - total_supervisory_hours

            # Calculate costs using effective hourly rates
            manager_cost = effective_manager_rate * 40  # Paid for 40 hours
            shift_supervisor_cost = shift_supervisor_hours * effective_shift_supervisor_rate
            barista_cost = barista_hours * effective_barista_rate
            weekly_labor_cost = manager_cost + shift_supervisor_cost + barista_cost

            # Calculate monthly labor cost
            monthly_labor_estimates.append(weekly_labor_cost * 4.3)
            monthly_sales_estimates.append(monthly_sales)

        yearly_sales_data[year] = monthly_sales_estimates + [sum(monthly_sales_estimates)]
        monthly_labor_cost.append(monthly_labor_estimates + [sum(monthly_labor_estimates)])

    # Convert sales data to DataFrame for display
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December", "Yearly Total"]
    sales_df = pd.DataFrame(yearly_sales_data, index=months).T
    sales_df.index.name = "Year"
    sales_df = sales_df.applymap(lambda x: f"${int(x):,}")

    st.subheader("Estimated Sales for 3 Years")
    st.write(sales_df)

    # Convert labor cost data to DataFrame for display
    labor_cost_df = pd.DataFrame(monthly_labor_cost, index=["Year 1", "Year 2", "Year 3"], columns=months)
    labor_cost_df = labor_cost_df.applymap(lambda x: f"${int(x):,}")

    st.subheader("Estimated Monthly Labor Cost for 3 Years")
    st.write(labor_cost_df)

    # Calculate labor cost as a percentage of sales
    labor_cost_percentage_data = []
    for year in range(3):
        year_percentage = []
        for month in range(12):
            sales_value = int(sales_df.iloc[year, month].replace('$', '').replace(',', ''))
            labor_cost_value = int(labor_cost_df.iloc[year, month].replace('$', '').replace(',', ''))
            percentage = (labor_cost_value / sales_value * 100) if sales_value > 0 else 0
            year_percentage.append(f"{percentage:.2f}%")
        labor_cost_percentage_data.append(year_percentage + ["-"])  # Skip yearly total in percentage

    labor_cost_percentage_df = pd.DataFrame(labor_cost_percentage_data, index=["Year 1", "Year 2", "Year 3"], columns=months)

    st.subheader("Labor Cost as a Percentage of Sales for 3 Years")
    st.write(labor_cost_percentage_df)

    # Summary Text
    st.subheader("Summary")
    st.write(
        f"**Estimated Sales**: Over the 3-year period, monthly sales are expected to grow based on capture rates. "
        f"This provides insight into the seasonal or month-by-month changes, allowing for planning around peak periods.\n\n"
        f"**Estimated Monthly Labor Costs**: The monthly labor costs reflect the staffing needs based on coverage rules "
        f"and employee wages. This will help in budgeting for labor expenses and determining if the staffing aligns with "
        f"expected sales volumes.\n\n"
        f"**Labor Cost as a Percentage of Sales**: This percentage indicates labor efficiency. Lower percentages suggest "
        f"better labor cost efficiency in relation to sales. Monitoring this metric over time will help ensure labor "
        f"costs are in line with profitability goals."
    )
