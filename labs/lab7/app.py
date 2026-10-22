import json
from pathlib import Path

from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__)

PROJECTS_FILE = Path(__file__).resolve().parent / "projects.json"


def load_projects():
    with PROJECTS_FILE.open(encoding="utf-8") as projects_file:
        return json.load(projects_file)


def save_projects(projects):
    with PROJECTS_FILE.open("w", encoding="utf-8") as projects_file:
        json.dump(projects, projects_file, indent=2)


projects_db = load_projects()


@app.route("/")
def index():
    projects_db[:] = load_projects()
    return render_template("index.html", projects=projects_db)


@app.post("/api/projects/<int:project_id>/upvote")
def upvote_project(project_id):
    projects_db[:] = load_projects()
    project = next(
        (project for project in projects_db if project["id"] == project_id),
        None,
    )
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project["likes"] += 1
    save_projects(projects_db)
    return jsonify({"project_id": project_id, "likes": project["likes"]})


@app.route("/assets/<path:filename>")
def assets(filename):
    assets_directory = Path(app.static_folder) / "assets"
    return send_from_directory(assets_directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
