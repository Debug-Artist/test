import numpy as np
import pandas as pd

CSV_PATH = "data/crop_yield_dataset.csv"
OUTPUT_PATH = "model_weights.npz"

# ------------------------------------------------------------
# CHANGE THESE COLUMN NAMES to match your Kaggle dataset
# ------------------------------------------------------------

FEATURE_COLUMNS = [
    "Rainfall_mm",
    "Temperature_C",
    "Soil_pH",
    "Humidity_pct",
    "Fertilizer_Used_kg"
]

TARGET_COLUMN = "Yield_ton_per_ha"

# Set True if your Kaggle yield column is in tons/ha.
# The website will then display the result in kg/ha.
TARGET_IS_TONS_PER_HECTARE = True

# ------------------------------------------------------------
# Load and clean data
# ------------------------------------------------------------

df = pd.read_csv(CSV_PATH)

required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(
        f"Missing columns in CSV: {missing_columns}\n"
        f"Available columns: {list(df.columns)}"
    )

df = df[required_columns].dropna()

X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
y = df[TARGET_COLUMN].to_numpy(dtype=float)

# ------------------------------------------------------------
# Standardize features
# ------------------------------------------------------------

feature_means = X.mean(axis=0)
feature_stds = X.std(axis=0)
feature_stds[feature_stds == 0] = 1.0

X_scaled = (X - feature_means) / feature_stds

# ------------------------------------------------------------
# Linear regression:
# y_hat = w.x + b
#
# MSE loss:
# L = mean((y_hat - y)^2)
#
# Gradients:
# dL/dw = X.T @ residuals / n
# dL/db = mean(residuals)
#
# The constant factor 2 is omitted because it is absorbed
# into the learning rate.
# ------------------------------------------------------------

def mse_loss(X, y, w, b):
    residuals = X @ w + b - y
    return np.mean(residuals ** 2)


def compute_gradients(X, y, w, b):
    residuals = X @ w + b - y
    dw = X.T @ residuals / len(y)
    db = residuals.mean()
    return dw, db


def gradient_descent(X, y, lr=0.05, epochs=5000):
    w = np.zeros(X.shape[1])
    b = 0.0
    history = []

    for _ in range(epochs):
        dw, db = compute_gradients(X, y, w, b)

        w -= lr * dw
        b -= lr * db

        history.append(mse_loss(X, y, w, b))

    return w, b, history


def momentum_gradient_descent(
    X,
    y,
    lr=0.05,
    momentum=0.9,
    epochs=5000
):
    w = np.zeros(X.shape[1])
    b = 0.0

    velocity_w = np.zeros_like(w)
    velocity_b = 0.0

    history = []

    for _ in range(epochs):
        dw, db = compute_gradients(X, y, w, b)

        velocity_w = momentum * velocity_w - lr * dw
        velocity_b = momentum * velocity_b - lr * db

        w += velocity_w
        b += velocity_b

        history.append(mse_loss(X, y, w, b))

    return w, b, history


# Train both optimizers and select the better final model

gd_w, gd_b, gd_history = gradient_descent(X_scaled, y)
momentum_w, momentum_b, momentum_history = momentum_gradient_descent(X_scaled, y)

if momentum_history[-1] <= gd_history[-1]:
    final_w = momentum_w
    final_b = momentum_b
    chosen_optimizer = "Momentum Gradient Descent"
else:
    final_w = gd_w
    final_b = gd_b
    chosen_optimizer = "Vanilla Gradient Descent"

# ------------------------------------------------------------
# Evaluate final model
# ------------------------------------------------------------

predictions = X_scaled @ final_w + final_b
final_mse = np.mean((predictions - y) ** 2)

ss_res = np.sum((y - predictions) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2_score = 1 - ss_res / ss_tot

# ------------------------------------------------------------
# Real-world feature effects:
# dYield / dFeature = standardized weight / feature std
# ------------------------------------------------------------

feature_effects = final_w / feature_stds

# ------------------------------------------------------------
# Save model artifacts for the FastAPI website
# ------------------------------------------------------------

np.savez(
    OUTPUT_PATH,
    weights=final_w,
    bias=np.array(final_b),
    means=feature_means,
    stds=feature_stds,
    feature_columns=np.array(FEATURE_COLUMNS),
    target_column=np.array(TARGET_COLUMN),
    target_is_tons=np.array(TARGET_IS_TONS_PER_HECTARE)
)

print("Training complete.")
print(f"Optimizer selected: {chosen_optimizer}")
print(f"Final MSE: {final_mse:.6f}")
print(f"R2 score: {r2_score:.4f}")

print("\nFeature effects: dYield / dFeature")
for name, effect in zip(FEATURE_COLUMNS, feature_effects):
    print(f"  {name}: {effect:.6f}")

print(f"\nModel saved to: {OUTPUT_PATH}")


=====================================================
FILE: main.py
=====================================================
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import numpy as np

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------
# Load trained crop-yield model
# ------------------------------------------------------------

MODEL_PATH = "model_weights.npz"

model_data = np.load(MODEL_PATH, allow_pickle=True)

CROP_WEIGHTS = model_data["weights"]
CROP_BIAS = float(model_data["bias"])
FEATURE_MEANS = model_data["means"]
FEATURE_STDS = model_data["stds"]
FEATURE_COLUMNS = [str(col) for col in model_data["feature_columns"]]
TARGET_COLUMN = str(model_data["target_column"])
TARGET_IS_TONS = bool(model_data["target_is_tons"])

# Real-world effect:
# dYield / dFeature = standardized weight / feature standard deviation
FEATURE_EFFECTS = CROP_WEIGHTS / FEATURE_STDS


def get_ranked_feature_effects():
    effects = []

    for name, effect in zip(FEATURE_COLUMNS, FEATURE_EFFECTS):
        effects.append((name, float(effect)))

    return sorted(
        effects,
        key=lambda item: abs(item[1]),
        reverse=True
    )


# ------------------------------------------------------------
# Original EduLink homepage
# ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ------------------------------------------------------------
# Crop yield predictor page
# ------------------------------------------------------------

@app.get("/crop-yield", response_class=HTMLResponse)
async def crop_yield_page(request: Request):
    return templates.TemplateResponse(
        "crop_yield.html",
        {
            "request": request,
            "prediction": None,
            "feature_effects": get_ranked_feature_effects(),
            "form_values": None
        }
    )


@app.post("/crop-yield", response_class=HTMLResponse)
async def predict_crop_yield(
    request: Request,
    rainfall: float = Form(...),
    temperature: float = Form(...),
    soil_ph: float = Form(...),
    humidity: float = Form(...),
    nutrients: float = Form(...)
):
    features = np.array(
        [rainfall, temperature, soil_ph, humidity, nutrients],
        dtype=float
    )

    if len(features) != len(CROP_WEIGHTS):
        raise ValueError(
            "The website form and trained model use different feature counts."
        )

    # Apply the exact scaling learned during training
    features_scaled = (features - FEATURE_MEANS) / FEATURE_STDS

    prediction = float(CROP_WEIGHTS @ features_scaled + CROP_BIAS)

    # Convert tons/ha to kg/ha if required
    if TARGET_IS_TONS:
        prediction *= 1000

    return templates.TemplateResponse(
        "crop_yield.html",
        {
            "request": request,
            "prediction": round(prediction, 2),
            "feature_effects": get_ranked_feature_effects(),
            "form_values": {
                "rainfall": rainfall,
                "temperature": temperature,
                "soil_ph": soil_ph,
                "humidity": humidity,
                "nutrients": nutrients
            }
        }
    )
