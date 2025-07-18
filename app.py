from flask import Flask, render_template, request

app = Flask(__name__)

# Fixed subject details: (name, max marks, credits, type)
subjects = [
    {"name": "Physics", "max_marks": 150, "credits": 5, "type": "internal_external"},
    {"name": "Mathematics-II", "max_marks": 100, "credits": 4, "type": "internal_external"},
    {"name": "Engineering Drawing", "max_marks": 100, "credits": 3, "type": "internal_external"},
    {"name": "Programming with Python", "max_marks": 150, "credits": 3, "type": "internal_external"},
    {"name": "Economics", "max_marks": 100, "credits": 3, "type": "internal_external"},
    {"name": "Manufacturing Practices", "max_marks": 50, "credits": 2, "type": "total_only"},
    {"name": "Mentoring", "max_marks": 100, "credits": 1, "type": "total_only"},
]

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

        return render_template("result.html", results=results, sgpa=sgpa)

    return render_template("index.html", subjects=subjects)

if __name__ == "__main__":
    app.run(debug=True)
