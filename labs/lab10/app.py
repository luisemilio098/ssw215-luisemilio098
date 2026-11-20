import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from ai_service import (
    ModelRefusalError,
    ProviderUnavailableError,
    SessionNotFoundError,
    extract_project,
    finish_github_session,
    get_github_draft,
    refine_github_session,
    start_github_session,
)
from github_service import (
    GitHubUnavailableError,
    RepositoryNotFoundError,
    fetch_readme,
)

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
    summary = db.Column(db.Text, nullable=False, default="")
    technologies = db.Column(db.Text, nullable=False, default="")
    difficulty = db.Column(db.String(20), nullable=False, default="Intermediate")
    likes = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "summary": self.summary,
            "technologies": self.technologies,
            "difficulty": self.difficulty,
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
    project_columns = {
        column["name"] for column in inspect(db.engine).get_columns("projects")
    }
    with db.engine.begin() as connection:
        if "summary" not in project_columns:
            connection.exec_driver_sql(
                "ALTER TABLE projects ADD COLUMN summary TEXT NOT NULL DEFAULT ''"
            )
        if "technologies" not in project_columns:
            connection.exec_driver_sql(
                "ALTER TABLE projects ADD COLUMN technologies TEXT NOT NULL DEFAULT ''"
            )
        if "difficulty" not in project_columns:
            connection.exec_driver_sql(
                "ALTER TABLE projects ADD COLUMN difficulty "
                "VARCHAR(20) NOT NULL DEFAULT 'Intermediate'"
            )
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


@app.post("/api/projects/smart")
def smart_create_project():
    data = request.get_json(silent=True)
    notes = data.get("notes") if isinstance(data, dict) else None
    if not isinstance(notes, str) or len(notes.strip()) < 20:
        return jsonify({"error": "Notes must be at least 20 characters"}), 400

    try:
        details = extract_project(notes.strip())
    except ModelRefusalError:
        return jsonify({"error": "The model refused to create a project"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    summary = details.summary
    project = Project(
        title=details.title,
        description=summary,
        summary=summary,
        technologies=", ".join(details.technologies),
        likes=0,
        author=Author.query.first(),
    )
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to save the generated project"}), 400

    return jsonify(project.to_dict()), 201


@app.post("/api/projects/git-start")
def start_github_import():
    data = request.get_json(silent=True)
    owner = data.get("owner") if isinstance(data, dict) else None
    repo = data.get("repo") if isinstance(data, dict) else None
    if (
        not isinstance(owner, str)
        or not owner.strip()
        or not isinstance(repo, str)
        or not repo.strip()
    ):
        return jsonify({"error": "A GitHub owner and repository are required"}), 400

    try:
        readme = fetch_readme(owner, repo)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except RepositoryNotFoundError:
        return jsonify({"error": "GitHub repository or README not found"}), 404
    except GitHubUnavailableError:
        return jsonify({"error": "GitHub is unavailable"}), 503

    if len(readme.strip()) < 20:
        return (
            jsonify({"error": "The repository README must be at least 20 characters"}),
            400,
        )

    try:
        session_id, draft = start_github_session(readme)
    except ModelRefusalError:
        return jsonify({"error": "The model refused to create a project draft"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    return jsonify({"session_id": session_id, "draft": draft}), 201


@app.post("/api/projects/git-refine")
def refine_github_import():
    data = request.get_json(silent=True)
    session_id = data.get("session_id") if isinstance(data, dict) else None
    feedback = data.get("feedback") if isinstance(data, dict) else None
    if not isinstance(session_id, str) or get_github_draft(session_id) is None:
        return jsonify({"error": "GitHub import session not found"}), 404
    if not isinstance(feedback, str) or not feedback.strip():
        return jsonify({"error": "Feedback is required"}), 400

    try:
        draft = refine_github_session(session_id, feedback.strip())
    except SessionNotFoundError:
        return jsonify({"error": "GitHub import session not found"}), 404
    except ModelRefusalError:
        return jsonify({"error": "The model refused to refine the project draft"}), 422
    except ProviderUnavailableError:
        return jsonify({"error": "The AI provider is unavailable"}), 503

    return jsonify({"draft": draft}), 200


@app.post("/api/projects/git-commit")
def commit_github_import():
    data = request.get_json(silent=True)
    session_id = data.get("session_id") if isinstance(data, dict) else None
    if not isinstance(session_id, str):
        return jsonify({"error": "GitHub import session not found"}), 404

    draft = get_github_draft(session_id)
    if draft is None:
        return jsonify({"error": "GitHub import session not found"}), 404

    summary = str(draft["summary"])
    project = Project(
        title=str(draft["title"]),
        description=summary,
        summary=summary,
        technologies=", ".join(draft["technologies"]),
        difficulty=str(draft["difficulty"]),
        likes=0,
        author=Author.query.first(),
    )
    db.session.add(project)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Unable to save the imported project"}), 400

    finish_github_session(session_id)
    return jsonify(project.to_dict()), 201


@app.route("/assets/<path:filename>")
def assets(filename):
    assets_directory = Path(app.static_folder) / "assets"
    return send_from_directory(assets_directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
