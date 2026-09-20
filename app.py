from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "ok", "app": "Crop Yield Prediction Dashboard"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
