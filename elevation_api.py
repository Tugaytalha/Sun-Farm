import requests


def get_elevation(lat, lon):
    # Base URL for Open-Meteo Elevation API
    url = 'https://api.open-meteo.com/v1/elevation'

    # Parameters for latitude and longitude
    params = {'latitude': lat, 'longitude': lon}

    try:
        # Sending GET request to the API
        response = requests.get(url, params=params, timeout=10)

        # Check if the response status is OK (200)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            elevation = data.get('elevation')  # Get the elevation from the response
            if elevation is not None:
                return elevation
            else:
                return "Elevation data not found."
        else:
            # Handle non-200 responses
            return f"Error: Unable to fetch elevation data. Status code: {response.status_code}"

    except requests.exceptions.Timeout:
        # Handle timeout errors
        return "Error: Request timed out. Please try again later."

    except requests.exceptions.RequestException as e:
        # Handle other request errors (network, etc.)
        return f"An error occurred: {e}"


