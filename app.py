from flask import Flask, request, jsonify
import pandas as pd
import joblib
import datetime
from flask_cors import CORS
import matplotlib.pyplot as plt
import io
import base64
from elevation_api import get_elevation  # Assuming elevation_api.py is in the same directory
from calculate_azimuth import max_azimuth  # Replace with the actual module where max_azimuth is defined

# Load the model and scaler
model = joblib.load('best_solar_model.pkl')
scaler = joblib.load('scaler.pkl')

app = Flask(__name__)
# Allow all origins to access the API from Cors
CORS(app, resources={r"/*": {"origins": "*"}})



@app.route('/predict_energy', methods=['POST'])
def predict_energy():
    try:
        # Get the request data
        data = request.json
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        kwh_price = float(data['kwh_price'])

        # Optional inputs, either area+efficiency or wattage
        panel_area = data.get('panel_area')
        panel_efficiency = data.get('panel_efficiency')
        panel_wattage = data.get('panel_wattage')

        # Validate the optional inputs
        if panel_wattage is not None:
            panel_wattage = float(panel_wattage)
        if panel_area is not None and panel_efficiency is not None:
            panel_area = float(panel_area)
            panel_efficiency = float(panel_efficiency)

        # Get the current year and month
        current_time = datetime.datetime.now()
        year = current_time.year
        month = current_time.month

        # Calculate elevation using get_elevation function
        try:
            elevation = get_elevation(latitude, longitude)[0]
        except:
            elevation = 100

        # # Calculate azimuth (month_number * 30 + 15 for the day of year)
        # day_of_year = (month * 30) + 15
        # azimuth = max_azimuth(latitude, longitude, day_of_year)
        #
        #
        # input_data = {
        #     'Azimuth (deg)': [float(azimuth)],
        #     'Longitude': [float(longitude)],
        #     'Elevation': [float(elevation)],
        #     'Latitude': [float(latitude)],
        #     'Year': [float(year)],
        #     'Month': [float(month)]
        # }

        predicted_irradiations = []
        # Prepare the 30 yearly input for the model
        for j in range(0, 30):
            predicted_irradiations.append([])
            for i in range(0, 12):
                # Calculate azimuth (month_number * 30 + 15 for the day of year)
                day_of_year = (i * 30) + 15
                azimuth = max_azimuth(latitude, longitude, day_of_year)

                input_data = {
                    'Azimuth (deg)': [float(azimuth)],
                    'Longitude': [float(longitude)],
                    'Elevation': [float(elevation)],
                    'Latitude': [float(latitude)],
                    'Year': [float(year)],
                    'Month': [float(i)]
                }
                # Create a DataFrame for the model input and ensure all values are floats
                custom_input = pd.DataFrame(input_data)

                # Normalize the custom input
                custom_input[['Azimuth (deg)', 'Longitude', 'Elevation', 'Latitude', 'Year', 'Month']] = scaler.transform(custom_input)

                # Predict the irradiation for the month
                predict_irradiation = model.predict(custom_input)

                # Ensure the predicted irradiation is non-negative
                predict_irradiation = predict_irradiation if predict_irradiation[0] > 0 else [0]

                # Append the predicted irradiation to the list
                predicted_irradiations[j].append(predict_irradiation)

            year += 1


        # Predicted irradiation for the next month
        predicted_irradiation = predicted_irradiations[0][month % 12][0]

        coeff = 0
        # Calculate energy output
        if panel_wattage:
            # If wattage is provided, use it directly
            coeff = panel_wattage / 1000  # Convert Wh to kWh
            energy_output = coeff * predicted_irradiation / 1000  # Convert Wh/m² to peak sun hours
        else:
            # Calculate energy using area and efficiency
            coeff = panel_area * panel_efficiency
            energy_output = coeff * predicted_irradiation / 1000  # Convert Wh/m² to peak sun hours

        # Calculate the estimated panel price
        if coeff <= 0.1:
            inverter_price = 100
        elif coeff <= 0.3:
            inverter_price = 1300
        elif coeff <= 1:
            inverter_price = 1800
        else:
            inverter_price = 6000
        panel_price = coeff * 13000 + (1500 if coeff > 0.1 else 0) + inverter_price

        # Calculate the monthly and yearly profit
        monthly_profit = energy_output * kwh_price

        yearly_profits = []
        yearly_outputs = []
        monthly_profits = []
        # Calculate the 30 yearly profit
        for j in range(0, 30):
            yearly_profit = 0
            yearly_output = 0

            for i in range(0, 12):
                predicted_irradiation = predicted_irradiations[j][i][0]
                energy_output = coeff * predicted_irradiation / 1000
                monthly_profit = energy_output * kwh_price
                yearly_profit += monthly_profit
                yearly_output += energy_output
                monthly_profits.append(monthly_profit)

            yearly_profits.append(yearly_profit)
            yearly_outputs.append(yearly_output)


        # Round profits to closest integer
        monthly_profit = round(monthly_profit)
        yearly_profits = [round(profit) for profit in yearly_profits]

        # Round energy output to 3 decimal places
        energy_output = round(energy_output, 3)

        # Calculate cumulative yearly profit
        cum_yearly_profits = [sum(yearly_profits[:i+1]) for i in range(0, 30)]

        pn_price_array = [panel_price] * 29
        pn_price_array.insert(0, 0)

        # Plot the panel_price and yearly cumulative profits starting from the current year
        plt.figure(figsize=(10, 6))
        plt.plot(range(current_time.year, current_time.year + 30), cum_yearly_profits, label='Cumulative Profit')
        plt.plot(range(current_time.year, current_time.year + 30), pn_price_array, label='Panel Price')
        plt.xlabel('Year')
        plt.ylabel('Cumulative Profit')
        plt.title('Yearly Cumulative Profit')
        plt.grid(True)
        plt.tight_layout()

        # Convert the plot to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode()

        # Close the plot
        plt.close()

        # Calculate break-even point by month
        break_even_month = 0
        total_profit = 0
        for i in range(len(monthly_profits)):
            total_profit += monthly_profits[i]
            if total_profit >= panel_price:
                break_even_month = i + 1
                break

        # Return the result as JSON
        return jsonify({
            'monthly_energy_output_kWh': energy_output,
            'yearly_energy_output_kWh': yearly_output,
            'monthly_profit': monthly_profit,
            'yearly_profit': yearly_profit,
            'break_even_month': break_even_month,
            'break_even_year': round(break_even_month / 12, 1),
            'chart': '<img src="data:image/png;base64,{}">'.format(plot_base64)
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        })



if __name__ == '__main__':
    app.run(host="0.0.0.0")
