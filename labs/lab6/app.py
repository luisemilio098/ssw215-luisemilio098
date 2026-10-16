from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory

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
    {
        "id": 4,
        "title": "Website For People With Mental Health Issues",
        "description": "I want to make a website for people with mental health issues to help with their day to day lives.",
        "likes": 0,
    }
]


@app.route("/")
def index():
    return render_template("index.html", projects=projects_db)


@app.post("/api/projects/<int:project_id>/upvote")
def upvote_project(project_id):
    project = next(
        (project for project in projects_db if project["id"] == project_id),
        None,
    )
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    return jsonify({"project_id": project_id, "likes": project["likes"]})


@app.route("/assets/<path:filename>")
def assets(filename):
    assets_directory = Path(app.static_folder) / "assets"
    return send_from_directory(assets_directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
