import pandas as pd
import os
import sys

# Ensure project root is in path for 'core' import
sys.path.append(os.getcwd())
# Import Fuzzy Logic to augment missing labels
from core.fuzzy_logic import FuzzyIrrigationController

def build_final_dataset():
    print("Building Final Training Dataset...")
    
    # 1. Load Preprocessed Soil Data (Minute-level)
    soil_path = 'data/consolidated_soil_moisture.csv'
    if not os.path.exists(soil_path):
        print(f"Error: Missing {soil_path}")
        return
        
    soil_df = pd.read_csv(soil_path)
    soil_df['timestamp'] = pd.to_datetime(soil_df['timestamp'])
    soil_df['Date'] = soil_df['timestamp'].dt.date
    
    # 2. Load NASA Weather Data (Daily-level)
    weather_path = 'data/data_raw/vietnam_weather_2020.csv'
    if not os.path.exists(weather_path):
        print(f"Error: Missing {weather_path}")
        return
        
    weather_df = pd.read_csv(weather_path)
    weather_df['Date'] = pd.to_datetime(weather_df['Date']).dt.date
    
    # 3. Merge (Broadcast Daily Weather to Minutes)
    print("Merging Soil data with NASA Weather...")
    final_df = pd.merge(soil_df, weather_df, on='Date', how='inner')
    
    # 4. Standardize column names BEFORE augmentation
    final_df.rename(columns={
        'Temp_C': 'air_temp',
        'Humidity_pct': 'air_humidity',
        'Precipitation_mm': 'rain_mm',
        'soil_moisture_avg': 'soil_moisture'
    }, inplace=True)

    # 5. AUGMENTATION: Use Fuzzy logic to decide labels
    print("Augmenting missing irrigation labels using Fuzzy Logic...")
    fuzzy = FuzzyIrrigationController()
    
    def get_fuzzy_label(row):
        # Fuzzy expects moisture in 0-100, but sensor data is 0-1.0
        moisture_pct = row['soil_moisture'] * 100
        # Use a more balanced threshold
        duration = fuzzy.decide(moisture_pct, row['air_temp'], row['rain_mm'])
        # Threshold 13 gives a better split for this dataset range (8.5 - 25.0)
        return 1 if duration > 13 else 0

    final_df['irrigation'] = final_df.apply(get_fuzzy_label, axis=1)
    
    # 6. Select final columns
    cols_to_keep = ['timestamp', 'air_temp', 'air_humidity', 'rain_mm', 'soil_moisture', 'irrigation']
    final_df = final_df[cols_to_keep]
    
    # 7. Save
    output_path = 'data/final_training_dataset.csv'
    final_df.to_csv(output_path, index=False)
    
    print(f"Success! Final dataset created at: {output_path}")
    print(f"Total rows: {len(final_df)}")
    print("Class distribution:")
    print(final_df['irrigation'].value_counts())

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    build_final_dataset()
