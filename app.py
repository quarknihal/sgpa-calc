from flask import Flask, render_template, request
import psycopg2
import json
from datetime import datetime

app = Flask(__name__)

# Fixed subject details
subjects = [
    {"name": "Physics", "max_marks": 150, "credits": 5, "type": "internal_external"},
    {"name": "Mathematics-II", "max_marks": 100, "credits": 4, "type": "internal_external"},
    {"name": "Engineering Drawing", "max_marks": 100, "credits": 3, "type": "internal_external"},
    {"name": "Programming with Python", "max_marks": 150, "credits": 3, "type": "internal_external"},
    {"name": "Economics", "max_marks": 100, "credits": 3, "type": "internal_external"},
    {"name": "Manufacturing Practices", "max_marks": 50, "credits": 2, "type": "total_only"},
    {"name": "Mentoring", "max_marks": 100, "credits": 1, "type": "total_only"},
]

# DB config - replace these with your Render/Postgres credentials
DB_NAME = "sgpa_database"
DB_USER = "sgpa_database_user"
DB_PASSWORD = "SX1CaaJHo1jOPbD1yAM2VRHIbdZtCjF0"
DB_HOST = "dpg-d1ucdvumcj7s73ectj6g-a"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )

# Create table if it doesn’t exist
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            data JSONB,
            sgpa FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

def calculate_grade_point(percentage):
    if percentage >= 90:
        return 10
    elif percentage >= 80:
        return 9
    elif percentage >= 70:
        return 8
    elif percentage >= 60:
        return 7
    elif percentage >= 50:
        return 6
    elif percentage >= 45:
        return 5
    elif percentage >= 40:
        return 4
    else:
        return 0

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        total_credits = 0
        weighted_points = 0
        results = []

        for idx, subject in enumerate(subjects):
            if subject["type"] == "internal_external":
                internal = float(request.form.get(f"internal_{idx}", 0))
                external = float(request.form.get(f"external_{idx}", 0))
                total = internal + external
            else:  # total_only
                total = float(request.form.get(f"total_{idx}", 0))

            percentage = (total / subject["max_marks"]) * 100
            gp = calculate_grade_point(percentage)
            weighted = gp * subject["credits"]
            total_credits += subject["credits"]
            weighted_points += weighted

            results.append({
                "name": subject["name"],
                "total": total,
                "percentage": round(percentage, 2),
                "grade_point": gp,
                "credits": subject["credits"]
            })

        sgpa = round(weighted_points / total_credits, 2)

        # Save submission to DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO submissions (data, sgpa) VALUES (%s, %s)",
            (json.dumps(results), sgpa)
        )
        conn.commit()
        cur.close()
        conn.close()

        return render_template("result.html", results=results, sgpa=sgpa)

    return render_template("index.html", subjects=subjects)

@app.route("/submissions")
def submissions():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, data, sgpa, timestamp FROM submissions ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    all_submissions = []
    for row in rows:
        all_submissions.append({
            "id": row[0],
            "data": row[1],
            "sgpa": row[2],
            "timestamp": row[3]
        })

    return render_template("submissions.html", submissions=all_submissions)

if __name__ == "__main__":
    app.run(debug=True)
