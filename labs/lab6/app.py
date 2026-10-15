from pathlib import Path

from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

projects_db = [
    {
        "id": 1,
        "title": "Website for People to Use",
        "description": "I want to make a website for people to use to help with their day to day lives.",
        "likes": 0,
    },
    {
        "id": 2,
        "title": "Student Athlete Planner",
        "description": "Plan classes, workouts, and recovery time more efficiently.",
        "likes": 0,
    },
    {
        "id": 3,
        "title": "Robotics Prototype",
        "description": "Develop a robot that can help people complete simple home tasks.",
        "likes": 0,
    },
]


@app.route("/")
def index():
    return render_template("index.html", projects=projects_db)


@app.route("/assets/<path:filename>")
def assets(filename):
    assets_directory = Path(app.static_folder) / "assets"
    return send_from_directory(assets_directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
