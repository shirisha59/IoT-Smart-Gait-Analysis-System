import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, send_file, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# RECORDING CONTROL
# =========================

recording = False

@app.route("/start")
def start():
    global recording
    recording = True
    return "Recording Started"

@app.route("/stop")
def stop():
    global recording
    recording = False
    return "Recording Stopped"

# =========================
# DATABASE INIT
# =========================
def init_db():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    ''')

    # SENSOR TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Lx REAL,
        Ly REAL,
        Lz REAL,
        Rx REAL,
        Ry REAL,
        Rz REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ANALYSIS HISTORY TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,
        date TEXT,

        result TEXT,
        confidence REAL,

        steps INTEGER,
        cadence REAL,

        symmetry REAL,
        stride_var REAL,
        rom REAL,
        stability REAL,

        advice TEXT,

        performance REAL
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# =========================
# LOAD MODEL
# =========================
model = joblib.load("parkinson_model.pkl")
scaler = joblib.load("scaler.pkl")

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

# =========================
# SIGNUP
# =========================
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  (username,password,role))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

# =========================
# GENERATE DATA (FIXED)
# =========================
@app.route("/generate_data")
def generate_data():
    global recording

    if not recording:
        return "Not Recording"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    data = (
        random.randint(-16000,16000),
        random.randint(-16000,16000),
        random.randint(-16000,16000),
        random.randint(-16000,16000),
        random.randint(-16000,16000),
        random.randint(-16000,16000)
    )

    c.execute("INSERT INTO sensor_data (Lx,Ly,Lz,Rx,Ry,Rz) VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

    return "Data Added"

# =========================
# GRAPH DATA
# =========================
@app.route("/get_data")
def get_data():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT Lx FROM sensor_data ORDER BY id DESC LIMIT 20")
    data = c.fetchall()
    conn.close()

    return {"data": [int(x[0]) for x in data[::-1]]}

# =========================
# PREDICTION
# =========================
@app.route("/predict")
def predict():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT Lx, Ly, Lz, Rx, Ry, Rz FROM sensor_data ORDER BY id DESC LIMIT 50")
    data = c.fetchall()
    conn.close()

    if not data:
        return {"result": "No Data", "confidence": 0}

    X = pd.DataFrame(data, columns=["Lx","Ly","Lz","Rx","Ry","Rz"])
    X_scaled = scaler.transform(X)

    preds = model.predict(X_scaled)
    avg = float(preds.mean())

    result = "Parkinson Detected" if avg > 0.5 else "Normal Walking"

    lx = X["Lx"].values
    steps = int(sum(abs(lx[i] - lx[i-1]) > 5000 for i in range(1,len(lx))))
    cadence = float((steps / 100) * 60)

    if avg > 0.6:
        suggestion = "Consult Doctor Immediately"
    elif avg > 0.4:
        suggestion = "Monitor Regularly"
    else:
        suggestion = "No Immediate Concern"

    return {
        "result": result,
        "confidence": float(avg),
        "steps": steps,
        "cadence": round(cadence, 2),
        "suggestion": suggestion
    }

# =========================
# FINAL REPORT
# =========================
@app.route("/download_report")
def download_report():

    from flask import request, send_file

    if "report" not in session:
        return "Please analyze data first"

    r = session["report"]

    # 👤 PATIENT INFO (from URL)
    name = request.args.get("name", "Unknown")
    age = request.args.get("age", "N/A")
    gender = request.args.get("gender", "N/A")
    height = request.args.get("height", "N/A")
    weight = request.args.get("weight", "N/A")
    performance = 100 - (r["confidence"] * 100)

    # ✔ SYMMETRY INTERPRETATION
    if r["symmetry"] < 10:
        sym_text = "Normal"
    elif r["symmetry"] < 25:
        sym_text = "Mild imbalance"
    else:
        sym_text = "Significant imbalance"

    report_path = "patient_report.txt"

    with open(report_path, "w") as f:

        f.write("====== PARKINSON DIAGNOSTIC REPORT ======\n\n")
        f.write("====== PARKINSON DIAGNOSTIC REPORT ======\n\n")
        f.write("PATIENT INFORMATION\n")
        f.write("---------------------------\n")
        f.write(f"Name: {name}\n")
        f.write(f"Age: {age}\n")
        f.write(f"Gender: {gender}\n")
        f.write(f"Height: {height} cm\n")
        f.write(f"Weight: {weight} kg\n\n")

        f.write("ANALYSIS RESULT\n")
        f.write("---------------------------\n")
        f.write(f"Condition: {r['result']}\n")
        f.write(f"Confidence: {r['confidence']*100:.2f}%\n\n")
        f.write(f"Overall Walking Performance: {performance:.2f}%\n\n")

        f.write("GAIT PARAMETERS\n")
        f.write("---------------------------\n")
        f.write(f"Step Count: {r['steps']}\n")
        f.write(f"Cadence: {r['cadence']:.2f} steps/min\n")
        f.write(f"Stride Variability: {r['stride_var']:.2f}\n")
        f.write(f"Range of Motion: {r['rom']:.2f}\n")
        f.write(f"Gait Symmetry Index: {r['symmetry']:.2f}% ({sym_text})\n")
        f.write(f"Movement Stability: {r['stability']:.2f}\n\n")
        f.write(f"Movement Stability Score: {r['stability']/1000000:.2f}\n\n")
        f.write("MEDICAL INTERPRETATION\n")
        f.write("---------------------------\n")
        if r["result"] == "Parkinson Detected":
            f.write("Irregular gait pattern detected.\n\n")
        else:
            f.write("Walking pattern appears normal.\n\n")

        f.write("RECOMMENDATION\n")
        f.write("---------------------------\n")
        f.write(r["advice"] + "\n\n")

        f.write("NOTE:\n")
        f.write("Graph visualization available in dashboard.\n")
        f.write("\nThis report is intended for assistive analysis only.\n")
        f.write("Final diagnosis should be confirmed by a medical professional.\n")

    return send_file(report_path, as_attachment=True)

# =========================
# STATS PAGE
# =========================
@app.route("/stats")
def stats():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='patient'")
    patients = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='doctor'")
    doctors = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM sensor_data")
    total_data = c.fetchone()[0]

    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()

    conn.close()

    return render_template("stats.html",
                           total_users=total_users,
                           patients=patients,
                           doctors=doctors,
                           total_data=total_data,
                           users=users)

def validate_sensor_placement(df):

    # Mean acceleration values
    Lx_mean = df["Lx"].mean()
    Rx_mean = df["Rx"].mean()

    Ly_mean = df["Ly"].mean()
    Ry_mean = df["Ry"].mean()

    Lz_mean = df["Lz"].mean()
    Rz_mean = df["Rz"].mean()

    # Variance
    L_var = df["Lx"].var()
    R_var = df["Rx"].var()

    # -----------------------------
    # 1. SENSOR ACTIVE CHECK
    # -----------------------------
    if L_var < 100 or R_var < 100:
        return False, "One sensor may be inactive or loose."

    # -----------------------------
    # 2. UPSIDE DOWN DETECTION
    # -----------------------------
    # If one leg axis is opposite direction
    # compared to expected orientation

    if (Lz_mean > 0 and Rz_mean < 0) or \
       (Lz_mean < 0 and Rz_mean > 0):

        return False, "Sensors appear upside down. Please reposition correctly."

    # -----------------------------
    # 3. EXTREME ORIENTATION CHECK
    # -----------------------------
    if abs(Lx_mean - Rx_mean) > 12000:
        return False, "Sensors are not aligned properly on both legs."

    # -----------------------------
    # 4. EXCESSIVE NOISE
    # -----------------------------
    if L_var > 1e9 or R_var > 1e9:
        return False, "Abnormal movement detected. Reattach sensors."

    return True, "Correct placement"

import os

@app.route("/analyze_file")
def analyze_file():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "patient_data.csv")

    if not os.path.exists(file_path):
        return {"error": "No data file found"}

    # READ DATA
    df = pd.read_csv(file_path)
    df = df[["Lx","Ly","Lz","Rx","Ry","Rz"]]
    # SENSOR POSITION VALIDATION
    valid, sensor_msg = validate_sensor_placement(df)

    if not valid:
        return {
            "error": sensor_msg
        }
    
    # ---------------------------------
    # WALKING DETECTION CHECK
    # ---------------------------------

    movement = (
        df["Lx"].std() +
        df["Ly"].std() +
        df["Lz"].std() +
        df["Rx"].std() +
        df["Ry"].std() +
        df["Rz"].std()
    )

    # Step estimation
    lx = df["Lx"].values

    steps = int(sum(
        abs(lx[i] - lx[i-1]) > 2500
        for i in range(1, len(lx))
    ))

    # If no real walking
    if movement < 15000 or steps < 8:

        return {
            "error": "No proper walking detected. Please walk correctly and try again."
        }

    # ML PREDICTION
    X_scaled = scaler.transform(df)

    probs = model.predict_proba(X_scaled)[:,1]

    confidence = float(probs.mean())

    result = "Parkinson Detected" if confidence > 0.5 else "Normal Walking"

    # PARAMETERS
    lx = df["Lx"].values

    steps = int(sum(abs(lx[i] - lx[i-1]) > 2500
                    for i in range(1,len(lx))))

    cadence = float((steps / len(df)) * 60)

    stride_var = float(df["Lx"].std())

    rom = float(df["Lx"].max() - df["Lx"].min())

    # SYMMETRY
    L_mean = abs(df["Lx"].mean())
    R_mean = abs(df["Rx"].mean())

    if (L_mean + R_mean) == 0:
        symmetry_percent = 0
    else:
        symmetry_percent = abs(L_mean - R_mean) / (
            L_mean + R_mean
        ) * 100

    # STABILITY
    stability = float(df["Lx"].var())

    # PERFORMANCE SCORE
    performance = (
    0.4 * (100 - confidence * 100)
    + 0.2 * min(cadence, 100)
    + 0.2 * (100 - min(symmetry_percent, 100))
    + 0.2 * (100 - min(stride_var / 100, 100))
)

    # RECOMMENDATION
    if confidence > 0.7:
        suggestion = "Consult Doctor Immediately"

    elif confidence > 0.4:
        suggestion = "Monitor Regularly"

    else:
        suggestion = "No Immediate Concern"

    # DATABASE STORAGE
    import datetime

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''
    INSERT INTO analysis_history
    (
        username,
        date,
        result,
        confidence,
        steps,
        cadence,
        symmetry,
        stride_var,
        rom,
        stability,
        advice,
        performance
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        session["user"],
        str(datetime.datetime.now()),
        result,
        confidence,
        steps,
        cadence,
        symmetry_percent,
        stride_var,
        rom,
        stability,
        suggestion,
        performance
    ))

    conn.commit()
    conn.close()

    # REPORT STORAGE
    session["report"] = {
        "result": result,
        "confidence": confidence,
        "steps": steps,
        "cadence": cadence,
        "stride_var": stride_var,
        "rom": rom,
        "symmetry": symmetry_percent,
        "stability": stability,
        "performance": performance,
        "advice": suggestion
    }

    return {
    "result": result,
    "confidence": confidence,
    "steps": steps,
    "cadence": cadence,
    "performance": performance,
    "suggestion": suggestion
}

@app.route("/graph_data")
def graph_data():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "patient_data.csv")

    if not os.path.exists(file_path):
        return {"error": "No patient data file"}

    df = pd.read_csv(file_path)

    return {
        "Lx": df["Lx"].tolist(),
        "Rx": df["Rx"].tolist()
    }
    
@app.route("/trend_graph")
def trend_graph():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT date, performance
    FROM analysis_history
    WHERE username=?
    ORDER BY id ASC
    """, (session["user"],))

    rows = c.fetchall()

    conn.close()

    # FULL DATE + TIME
    dates = [r[0][:19] for r in rows]

    performance = [round(r[1],2) for r in rows]

    return {
        "dates": dates,
        "performance": performance,
        "normal": [90] * len(performance)
    }

@app.route("/history")
def history():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM analysis_history WHERE username=?",
              (session["user"],))

    data = c.fetchall()
    conn.close()

    return render_template("history.html", data=data)

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# =========================
# RUN (UPDATED FOR RENDER)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)