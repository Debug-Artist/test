import os
import numpy as np
import pandas as pd

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from jinja2 import Template

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

# ============================================================
# CONFIGURATION
# Change these to match your Kaggle CSV.
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

TARGET_IS_TONS_PER_HECTARE = True

MODEL_PATH = "model_weights.npz"

TEST_SIZE = 0.2
RANDOM_STATE = 42

# ============================================================
# MODEL TRAINING
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

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    feature_means = X_train.mean(axis=0)
    feature_stds = X_train.std(axis=0)
    feature_stds[feature_stds == 0] = 1.0

    X_train_scaled = (X_train - feature_means) / feature_stds
    X_test_scaled = (X_test - feature_means) / feature_stds

    def mse_loss(X, y, w, b):
        residuals = X @ w + b - y
        return np.mean(residuals ** 2)

    def gradients(X, y, w, b):
        residuals = X @ w + b - y

        # Partial derivatives of MSE loss
        # dL/dw = X.T @ residuals / n
        # dL/db = mean(residuals)
        dw = X.T @ residuals / len(y)
        db = residuals.mean()

        return dw, db

    def gradient_descent(X, y, lr=0.05, epochs=3000):
        w = np.zeros(X.shape[1])
        b = 0.0
        history = []

        for _ in range(epochs):
            dw, db = gradients(X, y, w, b)

            w -= lr * dw
            b -= lr * db

            history.append(mse_loss(X, y, w, b))

        return w, b, history

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

        history = []

        for _ in range(epochs):
            dw, db = gradients(X, y, w, b)

            velocity_w = momentum * velocity_w - lr * dw
            velocity_b = momentum * velocity_b - lr * db

            w += velocity_w
            b += velocity_b

            history.append(mse_loss(X, y, w, b))

        return w, b, history

    gd_w, gd_b, gd_history = gradient_descent(X_train_scaled, y_train)
    momentum_w, momentum_b, momentum_history = momentum_gradient_descent(
        X_train_scaled,
        y_train
    )

    gd_train_mse = mse_loss(X_train_scaled, y_train, gd_w, gd_b)
    momentum_train_mse = mse_loss(
        X_train_scaled,
        y_train,
        momentum_w,
        momentum_b
    )

    if momentum_train_mse <= gd_train_mse:
        weights = momentum_w
        bias = momentum_b
        optimizer_name = "Momentum Gradient Descent"
        history = momentum_history
    else:
        weights = gd_w
        bias = gd_b
        optimizer_name = "Vanilla Gradient Descent"
        history = gd_history

    np.savez(
        MODEL_PATH,
        weights=weights,
        bias=np.array(bias),
        means=feature_means,
        stds=feature_stds,
        feature_columns=np.array(FEATURE_COLUMNS),
        target_column=np.array(TARGET_COLUMN),
        target_is_tons=np.array(TARGET_IS_TONS_PER_HECTARE),
        gd_history=np.array(gd_history),
        momentum_history=np.array(momentum_history),
        optimizer_name=np.array(optimizer_name)
    )

    return {
        "weights": weights,
        "bias": bias,
        "means": feature_means,
        "stds": feature_stds,
        "optimizer_name": optimizer_name,
        "gd_history": gd_history,
        "momentum_history": momentum_history,
        "X_test_scaled": X_test_scaled,
        "y_test": y_test
    }


if os.path.exists(MODEL_PATH):
    print("Loading existing trained model...")

    saved_model = np.load(MODEL_PATH, allow_pickle=True)

    WEIGHTS = saved_model["weights"]
    BIAS = float(saved_model["bias"])
    FEATURE_MEANS = saved_model["means"]
    FEATURE_STDS = saved_model["stds"]
    OPTIMIZER_NAME = str(saved_model["optimizer_name"])
    GD_HISTORY = saved_model["gd_history"]
    MOMENTUM_HISTORY = saved_model["momentum_history"]

    # Recreate a test split using the same random state
    temp_model = train_model()
    X_TEST_SCALED = temp_model["X_test_scaled"]
    Y_TEST = temp_model["y_test"]
else:
    print("No saved model found. Training from CSV...")
    trained = train_model()

    WEIGHTS = trained["weights"]
    BIAS = trained["bias"]
    FEATURE_MEANS = trained["means"]
    FEATURE_STDS = trained["stds"]
    OPTIMIZER_NAME = trained["optimizer_name"]
    GD_HISTORY = trained["gd_history"]
    MOMENTUM_HISTORY = trained["momentum_history"]
    X_TEST_SCALED = trained["X_test_scaled"]
    Y_TEST = trained["y_test"]

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


def get_evaluation_metrics():
    y_pred = X_TEST_SCALED @ WEIGHTS + BIAS

    mse = mean_squared_error(Y_TEST, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(Y_TEST, y_pred)
    r2 = r2_score(Y_TEST, y_pred)

    if TARGET_IS_TONS_PER_HECTARE:
        mse *= 1_000_000
        rmse *= 1000
        mae *= 1000

    return {
        "mse": mse,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "test_samples": len(Y_TEST),
        "training_samples": len(GD_HISTORY)
    }


# ============================================================
# HTML AND CSS
# ============================================================

BASE_STYLE = """
:root {
    --background: #ffffff;
    --text: #111827;
    --muted: #4b5563;
    --card: #f9fafb;
    --border: #e5e7eb;
    --blue: #2563eb;
    --green: #16a34a;
    --purple: #7c3aed;
    --orange: #ea580c;
    --pink: #db2777;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--background);
    color: var(--text);
    line-height: 1.65;
}

header {
    background: linear-gradient(135deg, #eff6ff, #ecfeff 50%, #f5f3ff);
    border-bottom: 1px solid var(--border);
}

header,
main,
footer {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

header h1 {
    font-size: 2.4rem;
    color: var(--blue);
}

header p {
    color: var(--muted);
    font-size: 1.05rem;
}

section {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

section h2 {
    margin-bottom: 0.75rem;
}

.blue-heading { color: var(--blue); }
.green-heading { color: var(--green); }
.purple-heading { color: var(--purple); }
.orange-heading { color: var(--orange); }
.pink-heading { color: var(--pink); }

ul {
    padding-left: 1.25rem;
    color: var(--muted);
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}

.badge-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.badge-green {
    background: #dcfce7;
    color: #15803d;
}

.badge-purple {
    background: #ede9fe;
    color: #6d28d9;
}

.badge-orange {
    background: #ffedd5;
    color: #c2410c;
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
    padding: 0.7rem;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    background: #ffffff;
    color: var(--text);
}

.button {
    display: inline-block;
    margin-top: 0.75rem;
    padding: 0.75rem 1.2rem;
    background: var(--blue);
    color: #ffffff;
    text-decoration: none;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    cursor: pointer;
}

.button-green {
    background: var(--green);
}

.button-purple {
    background: var(--purple);
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
}

.metric-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
}

.metric-card h3 {
    font-size: 0.9rem;
    color: var(--muted);
}

.metric-card p {
    font-size: 1.4rem;
    font-weight: 800;
}

.formula {
    background: #f3f4f6;
    border-left: 5px solid var(--blue);
    padding: 1rem;
    border-radius: 8px;
    font-family: "Courier New", monospace;
    overflow-x: auto;
    white-space: pre-wrap;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th,
td {
    border: 1px solid var(--border);
    padding: 0.65rem;
    text-align: left;
}

th {
    background: #f3f4f6;
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
    <title>Crop Yield Predictor – Your Learning Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>""" + BASE_STYLE + """</style>
</head>
<body>
    <header>
        <h1>Crop Yield Predictor</h1>
        <p>Your centralized platform for notes, resources, and intelligent learning tools.</p>
    </header>

    <main>
        <section>
            <span class="badge badge-blue">Featured Tool</span>
            <h2 class="blue-heading">Crop Yield Predictor</h2>
            <p>
                Estimate crop yield from rainfall, temperature, soil pH,
                humidity, and soil nutrients using a linear regression model
                trained with Mean Squared Error.
            </p>
            <a href="/crop-yield" class="button">Open Predictor</a>
        </section>

        <section>
            <span class="badge badge-purple">Project Concept</span>
            <h2 class="purple-heading">Momentum Optimization</h2>
            <p>
                Explore how partial derivatives guide parameter updates and how
                momentum accelerates convergence compared with vanilla
                gradient descent.
            </p>
            <a href="/integration" class="button button-purple">
                View Integration & Results
            </a>
        </section>

        <section>
            <span class="badge badge-green">What Crop Yield Predictor Offers</span>
            <h2 class="green-heading">Learning Resources</h2>
            <ul>
                <li>Organized course notes and summaries</li>
                <li>Shared resources and links for each subject</li>
                <li>Simple, fast, and mobile-friendly interface</li>
            </ul>
        </section>

        <section>
            <span class="badge badge-orange">Machine Learning</span>
            <h2 class="orange-heading">How the Model Works</h2>
            <p>
                The predictor learns a linear relationship between agricultural
                factors and crop yield. It uses partial derivatives of the Mean
                Squared Error loss to update weights and bias during training.
            </p>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 Crop Yield Predictor. Built with Python, FastAPI &amp; Momentum Optimization.</p>
    </footer>
</body>
</html>
""")

CROP_YIELD_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Crop Yield Predictor – Crop Yield Predictor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>""" + BASE_STYLE + """</style>
</head>
<body>
    <header>
        <h1>Crop Yield Predictor</h1>
        <p>Estimate crop yield using rainfall, temperature, soil pH, humidity, and nutrients.</p>
    </header>

    <main>
        <section>
            <h2 class="blue-heading">Enter Field Conditions</h2>

            <form method="post" action="/crop-yield">
                <label>
                    Rainfall (mm)
                    <input type="number" step="any" name="rainfall"
                           value="{{ rainfall }}" required />
                </label>

                <label>
                    Temperature (°C)
                    <input type="number" step="any" name="temperature"
                           value="{{ temperature }}" required />
                </label>

                <label>
                    Soil pH
                    <input type="number" step="any" name="soil_ph"
                           value="{{ soil_ph }}" required />
                </label>

                <label>
                    Humidity (%)
                    <input type="number" step="any" name="humidity"
                           value="{{ humidity }}" required />
                </label>

                <label>
                    Soil Nutrients
                    <input type="number" step="any" name="nutrients"
                           value="{{ nutrients }}" required />
                </label>

                <button type="submit" class="button">
                    Predict Yield
                </button>
            </form>
        </section>

        {% if prediction is not none %}
        <section>
            <h2 class="green-heading">Predicted Crop Yield</h2>
            <p><strong>{{ prediction }} kg/ha</strong></p>
        </section>
        {% endif %}

        <section>
            <h2 class="purple-heading">Factor Influence</h2>
            <p>
                Estimated yield change for a one-unit increase in each factor,
                holding other factors constant:
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
            <h2 class="orange-heading">Explore the Model</h2>
            <a href="/integration" class="button button-purple">
                View Integration & Results
            </a>
            <a href="/" class="button">Back to Crop Yield Predictor</a>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 Crop Yield Predictor. Built with Python, FastAPI &amp; Momentum Optimization.</p>
    </footer>
</body>
</html>
""")

INTEGRATION_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Crop Yield Predictor – Momentum Optimization Integration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>""" + BASE_STYLE + """</style>
</head>
<body>
    <header>
        <h1>Momentum Optimization Integration</h1>
        <p>
            How partial derivatives and momentum optimization are used to train
            the crop-yield prediction model.
        </p>
    </header>

    <main>
        <section>
            <span class="badge badge-blue">Model</span>
            <h2 class="blue-heading">Linear Regression Model</h2>

            <div class="formula">
y_hat = w1(x1) + w2(x2) + w3(x3) + w4(x4) + w5(x5) + b

Where:
x1 = Rainfall
x2 = Temperature
x3 = Soil pH
x4 = Humidity
x5 = Soil Nutrients
            </div>
        </section>

        <section>
            <span class="badge badge-green">Loss Function</span>
            <h2 class="green-heading">Mean Squared Error</h2>

            <div class="formula">
L = (1 / n) * sum((y_hat_i - y_i)^2)

Residual:
e_i = y_hat_i - y_i
            </div>

            <p>
                The model minimizes the average squared difference between
                predicted and actual crop yield.
            </p>
        </section>

        <section>
            <span class="badge badge-purple">Partial Derivatives</span>
            <h2 class="purple-heading">Gradient Calculation</h2>

            <div class="formula">
dL/dw_j = (2 / n) * sum(e_i * x_ij)

dL/db = (2 / n) * sum(e_i)
            </div>

            <p>
                Each weight gradient measures how much a small change in that
                feature weight affects the total loss. The bias gradient
                measures the overall prediction error.
            </p>

            <p>
                In the implementation, the constant factor 2 is omitted because
                it is absorbed into the learning rate.
            </p>
        </section>

        <section>
            <span class="badge badge-orange">Optimizer</span>
            <h2 class="orange-heading">Momentum Optimization</h2>

            <div class="formula">
velocity_w = momentum * velocity_w - learning_rate * dL/dw
velocity_b = momentum * velocity_b - learning_rate * dL/db

w = w + velocity_w
b = b + velocity_b
            </div>

            <p>
                Momentum accumulates past gradient directions, allowing the
                optimizer to move faster through consistent downhill directions
                and reduce oscillation.
            </p>

            <p>
                <strong>Selected optimizer:</strong> {{ optimizer_name }}
            </p>
        </section>

        <section>
            <span class="badge badge-blue">Evaluation</span>
            <h2 class="blue-heading">Testing Results</h2>

            <div class="metric-grid">
                <div class="metric-card">
                    <h3>Mean Squared Error</h3>
                    <p>{{ "%.4f" | format(metrics.mse) }}</p>
                </div>

                <div class="metric-card">
                    <h3>Root Mean Squared Error</h3>
                    <p>{{ "%.4f" | format(metrics.rmse) }}</p>
                </div>

                <div class="metric-card">
                    <h3>Mean Absolute Error</h3>
                    <p>{{ "%.4f" | format(metrics.mae) }}</p>
                </div>

                <div class="metric-card">
                    <h3>R² Score</h3>
                    <p>{{ "%.4f" | format(metrics.r2) }}</p>
                </div>
            </div>

            <table>
                <tr>
                    <th>Dataset Split</th>
                    <th>Samples</th>
                </tr>
                <tr>
                    <td>Training samples</td>
                    <td>{{ metrics.training_samples }}</td>
                </tr>
                <tr>
                    <td>Testing samples</td>
                    <td>{{ metrics.test_samples }}</td>
                </tr>
            </table>
        </section>

        <section>
            <span class="badge badge-green">Convergence</span>
            <h2 class="green-heading">Training Progress</h2>

            <table>
                <tr>
                    <th>Epoch</th>
                    <th>Gradient Descent MSE</th>
                    <th>Momentum MSE</th>
                </tr>

                {% for row in convergence_rows %}
                <tr>
                    <td>{{ row.epoch }}</td>
                    <td>{{ "%.4f" | format(row.gd_mse) }}</td>
                    <td>{{ "%.4f" | format(row.momentum_mse) }}</td>
                </tr>
                {% endfor %}
            </table>

            <p>
                Lower MSE means better fit. Momentum usually reduces the loss
                faster in the early epochs because it carries forward useful
                gradient information.
            </p>
        </section>

        <section>
            <span class="badge badge-purple">Feature Impact</span>
            <h2 class="purple-heading">Partial Derivative Interpretation</h2>

            <table>
                <tr>
                    <th>Feature</th>
                    <th>dYield / dFeature</th>
                    <th>Interpretation</th>
                </tr>

                {% for feature, effect in feature_effects %}
                <tr>
                    <td>{{ feature }}</td>
                    <td>{{ "%.4f" | format(effect) }} kg/ha per unit</td>
                    <td>
                        {% if effect >= 0 %}
                        Increasing this feature increases predicted yield.
                        {% else %}
                        Increasing this feature decreases predicted yield.
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </section>

        <section>
            <h2 class="blue-heading">Navigation</h2>
            <a href="/crop-yield" class="button">Open Crop Yield Predictor</a>
            <a href="/" class="button button-green">Back to Crop Yield Predictor</a>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 Crop Yield Predictor. Built with Python, FastAPI &amp; Momentum Optimization.</p>
    </footer>
</body>
</html>
""")

# ============================================================
# FASTAPI ROUTES
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


@app.get("/integration", response_class=HTMLResponse)
async def integration_page():
    metrics = get_evaluation_metrics()

    checkpoints = [1, 10, 50, 100, 500, 1000, 2000, 3000]
    convergence_rows = []

    for epoch in checkpoints:
        if epoch <= len(GD_HISTORY) and epoch <= len(MOMENTUM_HISTORY):
            convergence_rows.append({
                "epoch": epoch,
                "gd_mse": float(GD_HISTORY[epoch - 1]),
                "momentum_mse": float(MOMENTUM_HISTORY[epoch - 1])
            })

    return INTEGRATION_TEMPLATE.render(
        optimizer_name=OPTIMIZER_NAME,
        metrics=metrics,
        convergence_rows=convergence_rows,
        feature_effects=get_ranked_feature_effects()
    )
