import pandas as pd
import joblib
import matplotlib.pyplot as plt
import os
import sys

def verify_on_2026_heatwave():
    print("Verifying AI Model on 2026 Heatwave Data...")
    
    # 1. Load Model and Scaler
    if not os.path.exists('models/mlp_irrigation_model.pkl'):
        print("Error: Model not found.")
        return
    
    mlp = joblib.load('models/mlp_irrigation_model.pkl')
    scaler = joblib.load('models/irrigation_scaler.pkl')
    
    # 2. Load 2026 Weather
    weather_2026 = pd.read_csv('data/vietnam_weather_2026.csv')
    
    # 3. Simulate
    current_moisture = 0.6  # 60%
    moisture_history = []
    decision_history = []
    
    for i, row in weather_2026.iterrows():
        temp = row['Temp_C']
        humid = row['Humidity_pct']
        rain = row['Precipitation_mm']
        
        # Simple evaporation physics for simulation
        evap = (temp / 35.0) * (1.1 - (humid / 100.0)) * 0.05
        current_moisture -= evap
        if rain > 1.0:
            current_moisture += min(rain * 0.02, 0.1)
        
        current_moisture = max(0.05, min(0.95, current_moisture))
        
        # AI DECISION
        # Input features: air_temp, air_humidity, rain_mm, soil_moisture
        input_data = pd.DataFrame([[temp, humid, rain, current_moisture]], 
                                 columns=['air_temp', 'air_humidity', 'rain_mm', 'soil_moisture'])
        input_scaled = scaler.transform(input_data)
        
        decision = mlp.predict(input_scaled)[0]
        
        if decision == 1:
            current_moisture += 0.25  # Irrigation adds 25% moisture
            current_moisture = min(0.95, current_moisture)
            
        moisture_history.append(current_moisture * 100)
        decision_history.append(decision)
        
    weather_2026['Simulated_Moisture'] = moisture_history
    weather_2026['AI_Decision'] = decision_history
    
    # 4. Plot
    plt.figure(figsize=(15, 8))
    
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    ax1.plot(weather_2026['Date'], weather_2026['Simulated_Moisture'], label='Soil Moisture (%)', color='green', linewidth=2)
    ax1.set_ylabel('Moisture %', color='green')
    ax1.set_ylim(0, 100)
    
    ax2.bar(weather_2026['Date'], weather_2026['AI_Decision'], alpha=0.3, color='blue', label='AI Pump Action')
    ax2.set_ylabel('Pump (1=ON)', color='blue')
    
    plt.title('AI Irrigation Performance during 2026 Heatwave (Demo)')
    plt.grid(True, alpha=0.3)
    
    # Simple x-axis formatting
    plt.xticks(weather_2026['Date'][::10], rotation=45)
    
    plt.savefig('data/ai_verification_2026.png')
    print("Success! Verification plot saved to: data/ai_verification_2026.png")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    verify_on_2026_heatwave()
