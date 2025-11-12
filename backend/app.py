from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory, render_template_string, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import certifi
import os
from datetime import datetime, timezone, timedelta
from dateutil import tz
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in .env")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# ------------------- INITIAL SETUP ------------------- #
app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")

# Enable CORS for all routes and allow credentials
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

app.secret_key = "supersecretkey123"  # session secret key

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["data_detective"]
sub_col = db["submissions"]

# Hardcoded admin credentials
ADMIN_USER = "admin@123"
ADMIN_PASS = "HelloWorld!"

# ------------------- PARTICIPANT ENDPOINTS ------------------- #
# Helper to get UTC timestamp
def utc_now():
    return datetime.now(timezone.utc)

@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    team = data.get("team")
    start_time = data.get('timestamp')

    if not team:
        return jsonify({"error": "Team name required"}), 400

    # from_timezone = tz.gettz('UTC')
    # ist_tz = tz.gettz('Asia/Kolkata')

    # now = datetime.now()

    # now_ist = now.replace(tzinfo=ist_tz)

    # IST = timezone(timedelta(hours=5, minutes=30))
    # ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(IST)


    # Convert current time to IST (UTC+5:30)
    # IST = timezone(timedelta(hours=5, minutes=30))
    # start_time = now_ist  # ✅ This stores timezone-aware IST datetime

    existing = sub_col.find_one({"team": team})
    if existing:
        return jsonify({"message": "Welcome back, resuming your session."}), 200

    # Create new team document in MongoDB
    sub_col.insert_one({
        "team": team,
        "start_time": start_time,
        "level1": {},
        "level2": {},
        "level3": {},
        "final": {}
    })

    return jsonify({"message": f"Session started for {team}"}), 200

@app.route("/submit-level", methods=["POST"])
def submit_level():
    data = request.get_json()
    team = data.get("team")
    level = data.get("level")
    answer = data.get("answer")
    attempts = data.get("attempts", 1)
    timestamp = data.get("timestamp")

    if not all([team, level, answer]):
        return jsonify({"error": "Missing data"}), 400

    IST = timezone(timedelta(hours=5, minutes=30))
    ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(IST)

    sub_col.update_one(
        {"team": team},
        {"$set": {
            f"level{level}": {
                "answer": answer,
                "attempts": attempts,
                "timestamp": ts
            }
        }}
    )

    return jsonify({"message": f"Level {level} recorded"}), 200

@app.route("/submit-final", methods=["POST"])
def submit_final():
    data = request.get_json()
    team = data.get("team")
    a1 = data.get("answer1")
    a2 = data.get("answer2")
    attempts = data.get("attempts", 1)
    timestamp = data.get("timestamp")

    if not all([team, a1, a2]):
        return jsonify({"error": "Missing data"}), 400

    # IST = timezone(timedelta(hours=5, minutes=30))
    # ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(IST)

    sub_col.update_one(
        {"team": team},
        {"$set": {
            "final": {
                "answer1": a1,
                "answer2": a2,
                "attempts": attempts,
                "timestamp": timestamp
            },
            "completed": True
        }}
    )

    return jsonify({"message": "Final answers recorded"}), 200


# ------------------- ADMIN LOGIN SYSTEM ------------------- #

login_html = """
<!DOCTYPE html>
<html>
<head>
  <title>Admin Login</title>
  <style>
    body { font-family: Arial; background:#0e0e0e; color:#eee; text-align:center; padding-top:100px; }
    input { margin:10px; padding:8px; width:200px; }
    button { padding:8px 20px; }
  </style>
</head>
<body>
  <h2>Admin Login</h2>
  <form method="POST" action="/admin/login">
    <input type="text" name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
  </form>
</body>
</html>
"""

@app.route("/admin", methods=["GET"])
def admin_login_page():
    if session.get("logged_in"):
        return redirect(url_for("results_page"))
    return render_template_string(login_html)

@app.route("/admin/login", methods=["POST"])
def admin_login():
    # Accept both JSON (from React) and form (from browser)
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    if username == ADMIN_USER and password == ADMIN_PASS:
        session["logged_in"] = True
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


# ------------------- PROTECTED RESULTS ------------------- #

@app.route("/results", methods=["GET"])
def get_results():
    from datetime import datetime, timezone, timedelta

    # IST timezone
    IST = timezone(timedelta(hours=5, minutes=30))

    def to_ist_dt(value):
        """
        Convert value (datetime or ISO string) to an IST-aware datetime.
        - If value is None -> return None
        - If naive -> assume it's IST (keeps previous behaviour)
        - If aware -> convert to IST
        """
        if not value:
            return None

        # If it's a string, try to parse ISO format
        if isinstance(value, str):
            try:
                # Python 3.11+ supports fromisoformat with offset
                dt = datetime.fromisoformat(value)
            except Exception:
                # Fallback: try common formats
                try:
                    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    dt = dt.replace(tzinfo=IST)
                except Exception:
                    return None
        elif isinstance(value, datetime):
            dt = value
        else:
            return None

        # If datetime is naive, assume it is IST (this matches how timestamps
        # were previously stored/displayed in your app).
        if dt.tzinfo is None:
            return dt.replace(tzinfo=IST)
        # If aware, convert to IST
        return dt.astimezone(IST)

    def format_delta(delta):
        """Format timedelta as 'Hh Mm Ss' or 'Xm Ys' if hours = 0."""
        if delta is None:
            return "-"
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            return "-"  # guard against negative durations

        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        return f"{minutes}m {seconds}s"

    teams = list(sub_col.find({}, {"_id": 0}))
    results = []

    for team in teams:
        name = team.get("team", "-")

        # Convert start_time and final.timestamp to IST-aware datetimes
        start_raw = team.get("start_time")
        final_obj = team.get("final", {}) or {}
        final_raw = final_obj.get("timestamp")  # can be datetime or ISO string

        start_ist = to_ist_dt(start_raw)
        final_ist = to_ist_dt(final_raw)

        # Compute total_time as final.timestamp - start_time (both in IST)
        if start_ist and final_ist:
            try:
                delta = final_ist - start_ist
                total_time = format_delta(delta)
            except Exception:
                total_time = "-"
        else:
            total_time = "-"

        # Helper to extract each level info (status, attempts, timestamp string)
        def level_info(lvl):
            data = team.get(f"level{lvl}", {}) or {}
            status = "Yes" if data.get("answer") else "-"
            attempts = data.get("attempts", "-")
            ts_raw = data.get("timestamp")
            ts_dt = to_ist_dt(ts_raw)
            ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S") if ts_dt else "-"
            return {"status": status, "attempts": attempts, "timestamp": ts_str}

        # Final info (final has answer1/answer2)
        final_status = "-"
        final_attempts = "-"
        final_ts_str = "-"
        if final_obj:
            final_status = "Yes" if (final_obj.get("answer1") or final_obj.get("answer2")) else "-"
            final_attempts = final_obj.get("attempts", "-")
            final_ts_dt = to_ist_dt(final_obj.get("timestamp"))
            final_ts_str = final_ts_dt.strftime("%Y-%m-%d %H:%M:%S") if final_ts_dt else "-"

        results.append({
            "team": name,
            "start_time": start_raw,
            "level1": level_info(1),
            "level2": level_info(2),
            "level3": level_info(3),
            "final": {
                "status": final_status,
                "attempts": final_attempts,
                "timestamp": final_ts_str
            },
            "total_time": total_time
        })

    return jsonify(results), 200


@app.route("/api/results", methods=["GET"])
def api_results():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    data = list(sub_col.find({}, {"_id": 0}))
    safe_data = [serialize_doc(d) for d in data]

    return jsonify(safe_data)

# ------------------- SERVE FRONTEND ------------------- #

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    """Serve React app for all routes"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")
    
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

@app.route("/download/<level>")
def download_dataset(level):
    # ✅ Define where your datasets are saved
    dataset_folder = "datasets"  # e.g. backend/datasets/
    
    # ✅ Map level to the correct file
    file_map = {
        "1": "access_logs(Level 1).csv",
        "2": "transaction_logs(Level 2).csv",
        "3": "shipment_data(Level 3).csv"
    }

    filename = file_map.get(level)
    if not filename:
        return jsonify({"error": "Invalid level"}), 404

    return send_from_directory(dataset_folder, filename, as_attachment=True)

# ------------------- MAIN ------------------- #
if __name__ == "__main__":
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host="0.0.0.0", port=5000)