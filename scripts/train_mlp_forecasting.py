"""
=============================================================
  Module: MLP Forecasting - Predict soil moisture 15 min ahead
  Role: Person 1 - Hybrid System (MLP + FLC)
  Dataset: cleaned_iot_data.csv (time-series, 5 min/row)
  Technique: Time-Shifting Regression with MLPRegressor (sklearn)
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend (no display needed)
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
DATA_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'cleaned_iot_data.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mlp_forecasting.pkl')
PLOTS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data', 'plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

print("=" * 60)
print("  STEP 1: Load data from cleaned_iot_data.csv")
print("=" * 60)

df = pd.read_csv(DATA_PATH, parse_dates=['date'])
df = df.sort_values('date').reset_index(drop=True)

print(f"  Total rows (sorted): {len(df)}")
print(f"  Columns: {df.columns.tolist()}")

# ─────────────────────────────────────────────
# 2. TIME-SHIFTING
#    Predict 15 min ahead = shift water_level up by 3 rows
#    (each row = 5 min -> 3 rows = 15 min)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 2: Create Target column (future_water_level = shift -3)")
print("=" * 60)

df['future_water_level'] = df['water_level'].shift(-3)

# Drop NaN rows introduced at the tail by shift
df.dropna(inplace=True)

print(f"  Rows remaining after dropna: {len(df)}")
print(f"  Sample (water_level vs future_water_level):")
print(df[['date', 'water_level', 'future_water_level']].head(5).to_string(index=False))

# ─────────────────────────────────────────────
# 3. SPLIT FEATURES (X) AND TARGET (y)
#    Use only 3 columns: Temperature_C, humidity, water_level
#    Ignore: Watering_plant_pump_ON
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 3: Separate Features X and Target y")
print("=" * 60)

FEATURES = ['Temperature_C', 'humidity', 'water_level']
TARGET   = 'future_water_level'

X = df[FEATURES]
y = df[TARGET]

print(f"  Features (X): {FEATURES}")
print(f"  Target (y):   {TARGET}")
print(f"  X shape: {X.shape}  |  y shape: {y.shape}")

# ─────────────────────────────────────────────
# 4. SLIDING WINDOW SPLIT
#    - Giữ nguyên thứ tự thời gian (no shuffle, no data leakage)
#    - Tìm cửa sổ liên tục ~20% dữ liệu có std(water_level) cao nhất
#    - Test  = cửa sổ dao động mạnh nhất (học được pattern thực tế)
#    - Train = phần còn lại (trước + sau cửa sổ, vẫn liên tục)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 4: Sliding Window Split (find max-variance test window)")
print("=" * 60)

n_total      = len(df)
window_size  = int(n_total * 0.20)   # 20% of total rows
water_series = df['water_level'].values

# Sliding window: compute std of water_level in each window position
best_std   = -1
best_start = 0
for start in range(0, n_total - window_size + 1, 10):   # step=10 for speed
    window_std = water_series[start : start + window_size].std()
    if window_std > best_std:
        best_std   = window_std
        best_start = start

best_end = best_start + window_size

print(f"  Total rows       : {n_total}")
print(f"  Window size (20%): {window_size}")
print(f"  Best window      : rows [{best_start} : {best_end}]")
print(f"  Window std       : {best_std:.4f}  (water_level variance in test set)")
print(f"  Window date range: {df['date'].iloc[best_start].date()} -> {df['date'].iloc[best_end - 1].date()}")

# --- Build index masks (preserve original integer index of df) ---
test_mask  = (df.index >= best_start) & (df.index < best_end)
train_mask = ~test_mask

X_train = X[train_mask]
y_train = y[train_mask]
X_test  = X[test_mask]
y_test  = y[test_mask]

print(f"  Train samples    : {len(X_train)}  (rows outside window)")
print(f"  Test  samples    : {len(X_test)}   (rows inside window)")


# ─────────────────────────────────────────────
# 5. SCALE FEATURES (StandardScaler)
# ─────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ─────────────────────────────────────────────
# 6. TRAIN MLPRegressor
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 5: Train MLPRegressor (hidden_layer_sizes=(16, 8))")
print("=" * 60)

model = MLPRegressor(
    hidden_layer_sizes=(16, 8),
    activation='relu',
    solver='adam',
    max_iter=500,
    early_stopping=True,
    n_iter_no_change=10,
    verbose=True,
    random_state=42
)

model.fit(X_train_scaled, y_train)
print(f"  Training complete! Final Loss: {model.loss_:.4f}")

# ─────────────────────────────────────────────
# 7. EVALUATE MODEL (MSE & MAE)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 6: Evaluate model on Test set")
print("=" * 60)

y_pred = model.predict(X_test_scaled)
# Clamp predictions to physical range [0, 100] — soil moisture cannot exceed 100%
y_pred = np.clip(y_pred, 0, 100)

mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print(f"  MSE (Mean Squared Error) : {mse:.4f}")
print(f"  MAE (Mean Absolute Error): {mae:.4f}")
print(f"  R2  (R-squared Score)    : {r2:.4f}")
print(f"\n  >> The model explains {r2 * 100:.1f}% of the variation in soil moisture.")
print(f"     Average absolute error: {mae:.2f} units over 15-min horizon.")

# ─────────────────────────────────────────────
# 8. SAVE MODEL + SCALER TO mlp_forecasting.pkl
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 7: Save model -> mlp_forecasting.pkl")
print("=" * 60)

# Pack model + scaler together for easy inference
joblib.dump({'model': model, 'scaler': scaler, 'features': FEATURES}, MODEL_PATH)
print(f"  Saved to: {os.path.abspath(MODEL_PATH)}")

print("\n  DONE. Person 2 (FLC) can load this .pkl to get")
print("  future_water_level predictions for the Fuzzy Controller.")
print("=" * 60)

# ─────────────────────────────────────────────
# 9. PLOT 1: LOSS CURVE
#    Shows training loss decreasing over iterations
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 8: Generate Loss Curve plot")
print("=" * 60)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(model.loss_curve_, color='#E74C3C', linewidth=2, label='Training Loss')
if hasattr(model, 'validation_scores_') and model.validation_scores_:
    # Validation score is stored as R²-like, invert to show as loss tendency
    ax.plot(
        [-s for s in model.validation_scores_],
        color='#3498DB', linewidth=2, linestyle='--', label='Validation Loss (neg score)'
    )
ax.set_title('MLP Training Loss Curve', fontsize=14, fontweight='bold')
ax.set_xlabel('Iteration (Epoch)', fontsize=12)
ax.set_ylabel('Loss (MSE)', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
loss_path = os.path.join(PLOTS_DIR, 'loss_curve.png')
plt.savefig(loss_path, dpi=150)
plt.close()
print(f"  Saved: {os.path.abspath(loss_path)}")

# ─────────────────────────────────────────────
# 10. PLOT 2: ACTUAL VS PREDICTED
#     Show first 200 test samples for clarity
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 9: Generate Actual vs Predicted plot")
print("=" * 60)

N_SAMPLES = 200  # Show first 200 points to keep chart readable
y_actual_plot   = list(y_test)[:N_SAMPLES]
y_predicted_plot = y_pred[:N_SAMPLES]

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(y_actual_plot,    color='#2ECC71', linewidth=1.5, label='Actual soil moisture')
ax.plot(y_predicted_plot, color='#E74C3C', linewidth=1.5, linestyle='--', label='Predicted (15 min ahead)')
ax.set_title(
    f'Actual vs Predicted Soil Moisture (first {N_SAMPLES} test samples)\n'
    f'R² = {r2:.4f}  |  MAE = {mae:.2f}  |  MSE = {mse:.2f}',
    fontsize=13, fontweight='bold'
)
ax.set_xlabel('Sample index', fontsize=12)
ax.set_ylabel('Water level (%)', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
actual_pred_path = os.path.join(PLOTS_DIR, 'actual_vs_predicted.png')
plt.savefig(actual_pred_path, dpi=150)
plt.close()
print(f"  Saved: {os.path.abspath(actual_pred_path)}")

print("\n" + "=" * 60)
print("  ALL DONE. Summary:")
print(f"    R2  Score : {r2:.4f}  ({r2*100:.1f}% variance explained)")
print(f"    MAE       : {mae:.4f}")
print(f"    MSE       : {mse:.4f}")
print(f"    Loss Curve: data/plots/loss_curve.png")
print(f"    Act vs Pred: data/plots/actual_vs_predicted.png")
print("=" * 60)
