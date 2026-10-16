from pathlib import Path
import sys

from flask import Flask, abort, redirect, render_template, send_from_directory, url_for


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from course_data import CLASSES, COURSES, load_students


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    return render_template("cursos_index.html", courses=COURSES)


@app.route("/cursos/<slug>")
def course_page(slug):
    course = next((item for item in COURSES if item["slug"] == slug), None)
    if course is None:
        abort(404)

    classes = [
        classroom for classroom in CLASSES
        if classroom["course_slug"] == course["slug"]
    ]
    return render_template("curso.html", course=course, classes=classes)


@app.route("/turmas/<course_slug>/<class_slug>")
def class_page(course_slug, class_slug):
    classroom = next(
        (
            item for item in CLASSES
            if item["course_slug"] == course_slug and item["slug"] == class_slug
        ),
        None,
    )
    course = next((item for item in COURSES if item["slug"] == course_slug), None)
    if classroom is None or course is None:
        abort(404)

    classroom = {
        **classroom,
        "course_title": course["title"],
        "course_slug": course["slug"],
        "class_title": classroom["title"],
        "class_slug": classroom["slug"],
    }
    return render_template(
        "ListaAlunosT.html",
        classroom=classroom,
        students=load_students(),
    )


@app.route("/alunos/<int:student_number>")
def student_page(student_number):
    student = next(
        (item for item in load_students() if item["numero"] == student_number),
        None,
    )
    if student is None:
        abort(404)

    classroom = next(
        (item for item in CLASSES if item["course_slug"] == "rsi"),
        None,
    )
    if classroom is None:
        abort(404)
    student = {
        **student,
        "class_title": classroom["title"],
        "class_slug": classroom["slug"],
        "course_slug": classroom["course_slug"],
        "full_name": f"{student['nome']} {student['sobrenome']}",
    }
    return render_template("aluno.html", student=student)


@app.route("/ListaAlunos")
def legacy_student_list():
    return redirect(
        url_for("class_page", course_slug="rsi", class_slug="rsi-2ano"),
        code=302,
    )


@app.route("/estilo.css")
def course_stylesheet():
    return send_from_directory(PROJECT_ROOT, "estilo.css")


@app.route("/favicon.ico")
def favicon():
    favicon_path = Path(app.static_folder) / "images" / "favicon.ico"
    if not favicon_path.is_file():
        abort(404)
    return send_from_directory(favicon_path.parent, favicon_path.name)
