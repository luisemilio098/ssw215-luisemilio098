import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{(Path(app.instance_path) / 'portfolio.db').as_posix()}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Path(app.instance_path).mkdir(parents=True, exist_ok=True)
db = SQLAlchemy(app)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default="")
    likes = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "likes": self.likes,
            "author_name": self.author.name,
        }


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    projects = db.relationship("Project", backref="author")


def init_seed_data():
    if Project.query.first() is not None:
        return

    seed_file = Path(__file__).resolve().parent / "projects_seed.json"
    with seed_file.open(encoding="utf-8") as projects_file:
        seed_projects = json.load(projects_file)

    author = Author(name="Luis Emilio Amezquita Zapata")
    db.session.add_all(
        Project(
            id=project["id"],
            title=project["title"],
            description=project.get("description", ""),
            likes=project.get("likes", 0),
            author=author,
        )
        for project in seed_projects
    )
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise


with app.app_context():
    db.create_all()
    init_seed_data()


@app.route("/")
def index():
    projects_db = [
        project.to_dict()
        for project in Project.query.order_by(Project.id).all()
    ]
    return render_template("index.html", projects=projects_db)


@app.get("/api/projects")
def get_projects():
    projects_db = Project.query.order_by(Project.id).all()
    return jsonify([project.to_dict() for project in projects_db])


@app.post("/api/projects/<int:project_id>/upvote")
def upvote_project(project_id):
    project = db.session.get(Project, project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    project.likes += 1
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to update project"}), 400

    return jsonify({"project_id": project_id, "likes": project.likes})


@app.post("/api/projects")
def create_project():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A project title is required"}), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A project title is required"}), 400

    author = Author.query.first()
    project = Project(
        title=title.strip(),
        description="",
        likes=0,
        author=author,
    )
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "A project with that title already exists"}), 400

    return jsonify(project.to_dict()), 201


@app.route("/assets/<path:filename>")
def assets(filename):
    assets_directory = Path(app.static_folder) / "assets"
    return send_from_directory(assets_directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
