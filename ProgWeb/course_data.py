import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
STUDENTS_PATH = PROJECT_DIR / "cursos.json"

COURSES = ({"slug": "rsi", "title": "RSI"},)
CLASSES = (
    {
        "course_slug": "rsi",
        "slug": "rsi-2ano",
        "title": "Turma do segundo ano",
        "year": 2,
    },
)


def load_students():
    with STUDENTS_PATH.open(encoding="utf-8") as students_file:
        students = json.load(students_file)

    if not isinstance(students, list):
        raise ValueError("cursos.json tem de conter uma lista de alunos")

    required_fields = {"numero", "nome", "sobrenome", "telefone", "email"}
    for student in students:
        if not isinstance(student, dict) or not required_fields.issubset(student):
            raise ValueError("Cada aluno tem de conter os campos definidos em cursos.json")
        if isinstance(student["numero"], bool) or not isinstance(student["numero"], int):
            raise ValueError("O número de cada aluno tem de ser numérico")
        if not all(isinstance(student[field], str) for field in required_fields - {"numero"}):
            raise ValueError("Os dados textuais de cada aluno têm de ser texto")

    return sorted(
        students,
        key=lambda student: (student["nome"].casefold(), student["sobrenome"].casefold()),
    )
