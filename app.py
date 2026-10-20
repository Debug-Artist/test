import os
import numpy as np
import pandas as pd

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from jinja2 import Template

# ============================================================
# CONFIGURATION
# Change these three things to match YOUR Kaggle CSV.
# ============================================================

CSV_PATH = "data/crop_data.csv"

FEATURE_COLUMNS = [
    "Rainfall_mm",
    "Temperature_C",
    "Soil_pH",
    "Humidity_pct",
    "Fertilizer_Used_kg"
]

TARGET_COLUMN = "Yield_ton_per_ha"

# Set True if your yield column is in tons/hectare.
# The website will display kg/hectare.
TARGET_IS_TONS_PER_HECTARE = True

MODEL_PATH = "model_weights.npz"

# ============================================================
# TRAIN OR LOAD MODEL
# ============================================================

def train_model():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"CSV not found at: {CSV_PATH}\n"
            "Upload your Kaggle dataset to data/crop_data.csv"
        )

    df = pd.read_csv(CSV_PATH)

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in CSV: {missing_columns}\n"
            f"Available columns: {list(df.columns)}"
        )

    df = df[required_columns].dropna()

    X = df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y = df[TARGET_COLUMN].to_numpy(dtype=float)

    feature_means = X.mean(axis=0)
    feature_stds = X.std(axis=0)
    feature_stds[feature_stds == 0] = 1.0

    X_scaled = (X - feature_means) / feature_stds

    def mse_loss(X, y, w, b):
        residuals = X @ w + b - y
        return np.mean(residuals ** 2)

    def gradients(X, y, w, b):
        residuals = X @ w + b - y
        dw = X.T @ residuals / len(y)
        db = residuals.mean()
        return dw, db

    def gradient_descent(X, y, lr=0.05, epochs=3000):
        w = np.zeros(X.shape[1])
        b = 0.0

        for _ in range(epochs):
            dw, db = gradients(X, y, w, b)
            w -= lr * dw
            b -= lr * db

        return w, b

    def momentum_gradient_descent(
        X,
        y,
        lr=0.05,
        momentum=0.9,
        epochs=3000
    ):
        w = np.zeros(X.shape[1])
        b = 0.0
        velocity_w = np.zeros_like(w)
        velocity_b = 0.0

        for _ in range(epochs):
            dw, db = gradients(X, y, w, b)

            velocity_w = momentum * velocity_w - lr * dw
            velocity_b = momentum * velocity_b - lr * db

            w += velocity_w
            b += velocity_b

        return w, b

    gd_w, gd_b = gradient_descent(X_scaled, y)
    momentum_w, momentum_b = momentum_gradient_descent(X_scaled, y)

    gd_mse = mse_loss(X_scaled, y, gd_w, gd_b)
    momentum_mse = mse_loss(X_scaled, y, momentum_w, momentum_b)

    if momentum_mse <= gd_mse:
        weights = momentum_w
        bias = momentum_b
        optimizer_name = "Momentum Gradient Descent"
    else:
        weights = gd_w
        bias = gd_b
        optimizer_name = "Vanilla Gradient Descent"

    np.savez(
        MODEL_PATH,
        weights=weights,
        bias=np.array(bias),
        means=feature_means,
        stds=feature_stds,
        feature_columns=np.array(FEATURE_COLUMNS),
        target_column=np.array(TARGET_COLUMN),
        target_is_tons=np.array(TARGET_IS_TONS_PER_HECTARE)
    )

    print(f"Model trained using: {optimizer_name}")
    print(f"Final MSE: {mse_loss(X_scaled, y, weights, bias):.6f}")

    return weights, bias, feature_means, feature_stds


if os.path.exists(MODEL_PATH):
    print("Loading existing trained model...")
    saved_model = np.load(MODEL_PATH, allow_pickle=True)

    WEIGHTS = saved_model["weights"]
    BIAS = float(saved_model["bias"])
    FEATURE_MEANS = saved_model["means"]
    FEATURE_STDS = saved_model["stds"]
else:
    print("No saved model found. Training from CSV...")
    WEIGHTS, BIAS, FEATURE_MEANS, FEATURE_STDS = train_model()

FEATURE_EFFECTS = WEIGHTS / FEATURE_STDS


def get_ranked_feature_effects():
    effects = []

    for name, effect in zip(FEATURE_COLUMNS, FEATURE_EFFECTS):
        effects.append((name, float(effect)))

    return sorted(
        effects,
        key=lambda item: abs(item[1]),
        reverse=True
    )


# ============================================================
# HTML AND CSS
# ============================================================

BASE_STYLE = """
:root {
    --bg: #0f172a;
    --card: #1e293b;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #38bdf8;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

header,
main,
footer {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
}

header h1 {
    font-size: 2.2rem;
    color: var(--accent);
    margin-bottom: 0.5rem;
}

header p {
    color: var(--muted);
}

section {
    background: var(--card);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 1.5rem 0;
}

section h2 {
    margin-bottom: 0.75rem;
    color: var(--accent);
}

ul {
    padding-left: 1.25rem;
    color: var(--muted);
}

form {
    display: grid;
    gap: 1rem;
}

label {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    font-weight: 600;
}

input {
    padding: 0.6rem;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #0b1220;
    color: var(--text);
}

.button {
    display: inline-block;
    margin-top: 0.75rem;
    padding: 0.7rem 1.1rem;
    background: var(--accent);
    color: #0b1220;
    text-decoration: none;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
}

.tool-card {
    border: 1px solid rgba(56, 189, 248, 0.35);
}

.tool-card p {
    color: var(--muted);
    margin-bottom: 0.5rem;
}

footer {
    text-align: center;
    color: var(--muted);
    font-size: 0.9rem;
    padding-bottom: 2rem;
}
"""

HOME_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>EduLink – Your Learning Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>""" + BASE_STYLE + """</style>
</head>
<body>
    <header>
        <h1>EduLink</h1>
        <p>Your centralized platform for notes, resources, and collaboration.</p>
    </header>

    <main>
        <section class="features">
            <h2>What EduLink offers</h2>
            <ul>
                <li>Organized course notes and summaries</li>
                <li>Shared resources and links for each subject</li>
                <li>Simple, fast, and mobile-friendly interface</li>
            </ul>
        </section>

        <section class="cta">
            <h2>Get started</h2>
            <p>
                Explore materials, contribute notes, and stay updated
                with your courses.
            </p>
            <a href="#" class="button">Browse Resources</a>
        </section>

        <section class="tool-card">
            <h2>Crop Yield Predictor</h2>
            <p>
                Estimate crop yield using rainfall, temperature, soil pH,
                humidity, and soil nutrients.
            </p>
            <a href="/crop-yield" class="button">Open Predictor</a>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 EduLink. Built with Python &amp; FastAPI.</p>
    </footer>
</body>
</html>
""")

CROP_YIELD_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>EduLink – Crop Yield Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>""" + BASE_STYLE + """</style>
</head>
<body>
    <header>
        <h1>Crop Yield Predictor</h1>
        <p>
            Estimate crop yield using rainfall, temperature, soil pH,
            humidity, and soil nutrients.
        </p>
    </header>

    <main>
        <section>
            <h2>Enter field conditions</h2>

            <form method="post" action="/crop-yield">
                <label>
                    Rainfall (mm)
                    <input
                        type="number"
                        step="any"
                        name="rainfall"
                        value="{{ rainfall }}"
                        required
                    />
                </label>

                <label>
                    Temperature (°C)
                    <input
                        type="number"
                        step="any"
                        name="temperature"
                        value="{{ temperature }}"
                        required
                    />
                </label>

                <label>
                    Soil pH
                    <input
                        type="number"
                        step="any"
                        name="soil_ph"
                        value="{{ soil_ph }}"
                        required
                    />
                </label>

                <label>
                    Humidity (%)
                    <input
                        type="number"
                        step="any"
                        name="humidity"
                        value="{{ humidity }}"
                        required
                    />
                </label>

                <label>
                    Soil nutrients
                    <input
                        type="number"
                        step="any"
                        name="nutrients"
                        value="{{ nutrients }}"
                        required
                    />
                </label>

                <button type="submit" class="button">
                    Predict Yield
                </button>
            </form>
        </section>

        {% if prediction is not none %}
        <section>
            <h2>Predicted crop yield</h2>
            <p>
                <strong>{{ prediction }} kg/ha</strong>
            </p>
        </section>
        {% endif %}

        <section>
            <h2>Factor influence</h2>
            <p>
                Estimated yield change for a one-unit increase in each factor:
            </p>

            <ul>
                {% for feature, effect in feature_effects %}
                <li>
                    <strong>{{ feature }}</strong>:
                    {{ "%.4f" | format(effect) }} kg/ha per unit
                </li>
                {% endfor %}
            </ul>
        </section>

        <section>
            <h2>Navigation</h2>
            <a href="/" class="button">Back to EduLink</a>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 EduLink. Built with Python &amp; FastAPI.</p>
    </footer>
</body>
</html>
""")

# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return HOME_TEMPLATE.render()


@app.get("/crop-yield", response_class=HTMLResponse)
async def crop_yield_page():
    return CROP_YIELD_TEMPLATE.render(
        rainfall=900,
        temperature=27,
        soil_ph=6.5,
        humidity=65,
        nutrients=120,
        prediction=None,
        feature_effects=get_ranked_feature_effects()
    )


@app.post("/crop-yield", response_class=HTMLResponse)
async def predict_crop_yield(
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

    features_scaled = (features - FEATURE_MEANS) / FEATURE_STDS

    prediction = float(WEIGHTS @ features_scaled + BIAS)

    if TARGET_IS_TONS_PER_HECTARE:
        prediction *= 1000

    return CROP_YIELD_TEMPLATE.render(
        rainfall=rainfall,
        temperature=temperature,
        soil_ph=soil_ph,
        humidity=humidity,
        nutrients=nutrients,
        prediction=round(prediction, 2),
        feature_effects=get_ranked_feature_effects()
    )