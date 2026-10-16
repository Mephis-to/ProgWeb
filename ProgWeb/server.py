from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

from course_data import CLASSES, COURSES, load_students


PROJECT_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000


def page(title, content):
    template = (PROJECT_DIR / "cursos.html").read_text(encoding="utf-8")
    return (
        template.replace("{{ titulo }}", escape(title))
        .replace("{{ conteudo }}", content)
        .encode("utf-8")
    )


class CourseRequestHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _render(self, path):
        if path == "/estilo.css":
            return 200, (PROJECT_DIR / "estilo.css").read_bytes(), "text/css; charset=utf-8"

        if path == "/":
            items = "".join(
                f'<li><a href="/cursos/{quote(course["slug"], safe="-")}">'
                f'{escape(course["title"])}</a></li>'
                for course in COURSES
            )
            return 200, page("Cursos", f"<h1>Cursos</h1><ul>{items}</ul>"), (
                "text/html; charset=utf-8"
            )

        course_match = re.fullmatch(r"/cursos/([a-z0-9-]+)", path)
        if course_match:
            course = next(
                (item for item in COURSES if item["slug"] == course_match.group(1)),
                None,
            )
            if course is None:
                return self._not_found()
            classes = [
                item for item in CLASSES
                if item["course_slug"] == course["slug"]
            ]
            items = "".join(
                f'<li><a href="/turmas/{quote(course["slug"], safe="-")}/'
                f'{quote(classroom["slug"], safe="-")}">'
                f'{escape(classroom["title"])}</a></li>'
                for classroom in classes
            )
            content = (
                f"<h1>{escape(course['title'])}</h1><h2>Turmas</h2>"
                f"<ul>{items}</ul><p><a href=\"/\">&larr; Voltar aos cursos</a></p>"
            )
            return 200, page(course["title"], content), "text/html; charset=utf-8"

        class_match = re.fullmatch(r"/turmas/([a-z0-9-]+)/([a-z0-9-]+)", path)
        if class_match:
            course_slug, class_slug = class_match.groups()
            course = next((item for item in COURSES if item["slug"] == course_slug), None)
            classroom = next(
                (
                    item for item in CLASSES
                    if item["course_slug"] == course_slug and item["slug"] == class_slug
                ),
                None,
            )
            if course is None or classroom is None:
                return self._not_found()

            rows = "".join(
                f"<tr><td>{student['numero']}</td>"
                f'<td><a href="/alunos/{student["numero"]}">'
                f"{escape(student['nome'])} {escape(student['sobrenome'])}</a></td></tr>"
                for student in load_students()
            )
            content = (
                f"<h1>{escape(course['title'])} — {escape(classroom['title'])}</h1>"
                "<table><thead><tr><th>N.º aluno</th>"
                "<th>Primeiro e último nome</th></tr></thead>"
                f"<tbody>{rows}</tbody></table>"
                f'<p><a href="/cursos/{quote(course_slug, safe="-")}">'
                "&larr; Voltar às turmas</a></p>"
            )
            return 200, page(classroom["title"], content), "text/html; charset=utf-8"

        student_match = re.fullmatch(r"/alunos/([0-9]+)", path)
        if student_match:
            student_number = int(student_match.group(1))
            student = next(
                (item for item in load_students() if item["numero"] == student_number),
                None,
            )
            if student is None:
                return self._not_found()
            full_name = f"{student['nome']} {student['sobrenome']}"
            content = (
                f"<h1>{escape(full_name)}</h1><dl class=\"detalhes-aluno\">"
                f"<dt>Número de aluno</dt><dd>{student['numero']}</dd>"
                f"<dt>Telefone</dt><dd>{escape(student['telefone'])}</dd>"
                f"<dt>Email</dt><dd>{escape(student['email'])}</dd>"
                "</dl>"
                '<p><a href="/turmas/rsi/rsi-2ano">&larr; Voltar à turma</a></p>'
            )
            return 200, page(full_name, content), "text/html; charset=utf-8"

        return self._not_found()

    @staticmethod
    def _not_found():
        return 404, page("Página não encontrada", "<h1>Página não encontrada</h1>"), (
            "text/html; charset=utf-8"
        )

    def _handle_request(self):
        path = urlsplit(self.path).path
        try:
            status, body, content_type = self._render(path)
        except (OSError, ValueError):
            self.log_error("Erro ao carregar ou validar cursos.json")
            self._send(
                500,
                page("Erro do servidor", "<h1>Erro ao carregar os dados</h1>"),
            )
            return
        self._send(status, body, content_type)

    def do_GET(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), CourseRequestHandler)
    print(f"Servidor de cursos iniciado: http://localhost:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado.")
    finally:
        server.server_close()
