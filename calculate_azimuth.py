import numpy as np

# Function to calculate solar declination angle (delta)
def solar_declination(day_of_year):
    return 23.45 * np.sin(np.deg2rad((360 / 365) * (day_of_year - 81)))


# Function to calculate the solar elevation angle (alpha)
def solar_elevation_angle(latitude, solar_declination, hour_angle):
    return np.arcsin(np.sin(np.deg2rad(latitude)) * np.sin(np.deg2rad(solar_declination)) +
                     np.cos(np.deg2rad(latitude)) * np.cos(np.deg2rad(solar_declination)) * np.cos(
        np.deg2rad(hour_angle)))


# Function to calculate solar azimuth angle (A)
def solar_azimuth_angle(latitude, solar_declination, solar_elevation):
    numerator = np.sin(np.deg2rad(solar_declination)) - np.sin(np.deg2rad(solar_elevation)) * np.sin(
        np.deg2rad(latitude))
    denominator = np.cos(np.deg2rad(solar_elevation)) * np.cos(np.deg2rad(latitude))
    azimuth = np.rad2deg(np.arccos(numerator / denominator))
    return azimuth


# Function to calculate the maximum azimuth angle at sunrise or sunset
def max_azimuth(latitude, longitude, day_of_year):
    declination = solar_declination(day_of_year)
    # Approximate hour angle at sunset or sunrise (sun at horizon)
    solar_elevation = 0  # at sunrise/sunset
    max_azimuth = 180 - np.rad2deg(
        np.arctan(-np.sin(np.deg2rad(latitude)) * np.cos(np.deg2rad(declination)) / np.sin(np.deg2rad(declination))))

    # Optionally: adjust azimuth based on time zone (longitude affects solar time)
    time_offset = (longitude / 15.0)  # Time zone adjustment based on longitude (degrees to hours)
    return max_azimuth