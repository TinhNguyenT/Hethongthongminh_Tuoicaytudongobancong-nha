import requests
import pandas as pd
import os
import sys

def fetch_nasa_data(lat=10.82, lon=106.63, start="20260101", end="20260413", label="weather"):
    """
    Fetch weather data from NASA POWER API.
    Parameters:
    - T2M: Temp at 2m (C)
    - RH2M: Relative Humidity at 2m (%)
    - PRECTOTCORR: Precipitation (mm/day)
    """
    print(f"Connecting to NASA POWER API for {label} ({start} to {end})...")
    
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,RH2M,PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        base_data = data['properties']['parameter']
        dates = list(base_data['T2M'].keys())
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(dates, format='%Y%m%d'),
            'Temp_C': [base_data['T2M'][d] for d in dates],
            'Humidity_pct': [base_data['RH2M'][d] for d in dates],
            'Precipitation_mm': [base_data['PRECTOTCORR'][d] for d in dates]
        })

        df.replace(-999, float('nan'), inplace=True)
        df.ffill(inplace=True) 
        
        print(f"Successfully fetched {len(df)} days of data for {label}.")
        return df
        
    except Exception as e:
        print(f"Error fetching {label} data: {e}")
        return None

def main():
    # Set encoding for Windows logs
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    # 1. Fetch Historic Weather (2020) to match Soil Sensors
    weather_2020 = fetch_nasa_data(start="20200301", end="20200331", label="2020_Historic")
    if weather_2020 is not None:
        weather_2020.to_csv("data/vietnam_weather_2020.csv", index=False)
        print("Saved data/vietnam_weather_2020.csv")

    # 2. Fetch Current Weather (2026) for Demo
    weather_2026 = fetch_nasa_data(start="20260101", end="20260413", label="2026_Current")
    if weather_2026 is not None:
        weather_2026.to_csv("data/vietnam_weather_2026.csv", index=False)
        print("Saved data/vietnam_weather_2026.csv")

if __name__ == "__main__":
    main()
