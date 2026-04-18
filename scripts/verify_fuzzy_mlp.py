import sys
import os
# Thêm thư mục gốc vào path để import được core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fuzzy_logic import FuzzyIrrigationController
from core.mlp_network import MLPPredictor

def verify():
    print("="*50)
    print("VERIFYING FUZZY + MLP SYSTEM")
    print("="*50)

    # 1. Test MLP Predictor
    predictor = MLPPredictor('data/mlp_forecasting.pkl')
    test_temp, test_humid, test_soil = 32.0, 55.0, 45.0
    predicted = predictor.predict(test_temp, test_humid, test_soil)
    print(f"\n[MLP Test]")
    print(f"Input: Temp={test_temp}C, Humid={test_humid}%, Soil={test_soil}%")
    print(f"Predicted Soil (15m ahead): {predicted:.2f}%")

    # 2. Test Fuzzy Controller
    fuzzy = FuzzyIrrigationController()
    print(f"\n[Fuzzy Logic Test]")
    
    test_scenarios = [
        {"name": "Rule 1: Current Soil is Dry (Dry -> Long)", "cur": 30, "fut": 35},
        {"name": "Rule 2: Current Med + Future Dry (Med & Dry -> Short)", "cur": 55, "fut": 30},
        {"name": "Rule 3: Current Soil is Wet (Wet -> Off)", "cur": 85, "fut": 80},
        {"name": "Rule 3: Future Soil is Wet (Med & Wet -> Off)", "cur": 55, "fut": 85},
    ]

    for scenario in test_scenarios:
        duration = fuzzy.decide(scenario['cur'], scenario['fut'])
        print(f"- {scenario['name']}")
        print(f"  Result: {duration:.1f} seconds")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    verify()
