#!/usr/bin/env python3
"""Instalador e servidor do Studio Contact."""

import argparse
import base64
import hmac
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import venv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = Path(__file__).resolve().parent

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Studio Contact</title>
<link rel="stylesheet" href="/style.css">
<script src="/app.js" defer></script>
</head>
<body>
<header><a href="/">◈ Studio Contact</a><a href="/admin">Área da equipe ↗</a></header>
<main>
<section>
<span class="tag">IDEIAS QUE CONECTAM</span>
<h1>Uma boa conversa<br>começa aqui.</h1>
<p>Conte sua ideia. Sua mensagem será registrada para nossa equipe.</p>
</section>
<section class="card">
<h2>Vamos conversar</h2>
<form id="contact">
<label>Nome<input name="name" maxlength="100" autocomplete="name" required></label>
<label>E-mail<input name="email" type="email" maxlength="254" autocomplete="email" required></label>
<label>Mensagem<textarea name="message" maxlength="3000" rows="5" required></textarea></label>
<button>Enviar mensagem ↗</button>
<p id="feedback" role="status"></p>
</form>
</section>
</main>
</body>
</html>
"""

ADMIN = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mensagens — Studio Contact</title>
<link rel="stylesheet" href="/style.css">
<script src="/app.js" defer></script>
</head>
<body>
<header><a href="/">◈ Studio Contact</a><a href="/">← Voltar ao site</a></header>
<main>
<section><span class="tag">ÁREA DA EQUIPE</span><h1>Caixa de entrada.</h1>
<p>Consulte as últimas 100 mensagens.</p></section>
<section class="card">
<form id="admin">
<label>Senha da equipe<input name="password" type="password" autocomplete="current-password" required></label>
<button>Consultar mensagens</button>
<p id="feedback" role="status"></p>
</form>
<div id="messages"></div>
</section>
</main>
</body>
</html>
"""

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#f3f5f9;color:#19253b;font-family:system-ui,sans-serif}
header{max-width:1160px;margin:auto;padding:28px;display:flex;justify-content:space-between;gap:20px}
a{color:inherit;text-decoration:none;font-weight:600}
main{max-width:1160px;margin:60px auto;padding:28px;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}
.tag{font-size:12px;letter-spacing:2px;color:#684be0;font-weight:800}
h1{font-size:clamp(36px,4vw,56px);line-height:1.1;letter-spacing:-2px}
h2{margin-top:0}
p{color:#59677c;line-height:1.7}
.card{padding:32px;border-radius:24px;background:white;border:1px solid #e1e5ee;box-shadow:0 20px 60px #23385a09}
label{display:block;margin-top:20px;font-size:14px;font-weight:600}
input,textarea{width:100%;display:block;margin-top:8px;padding:13px;border:1px solid #ccd3df;border-radius:10px;font:inherit;background:#fbfcff;transition:box-shadow .2s,border-color .2s}
textarea{resize:vertical}
input:focus,textarea:focus{outline:none;border-color:#684be0;box-shadow:0 0 0 4px #684be018}
button{width:100%;margin-top:24px;padding:15px;border:0;border-radius:10px;background:#6248dc;color:white;font:inherit;font-weight:600;cursor:pointer;transition:transform .2s,background .2s}
button:hover{background:#4c34bd;transform:translateY(-1px)}
button:disabled{opacity:.6;cursor:wait;transform:none}
button:focus-visible,a:focus-visible{outline:3px solid #9980ff;outline-offset:4px}
#feedback{min-height:24px;font-size:14px}
article{border-top:1px solid #e1e5ee;margin-top:24px;padding-top:12px;overflow-wrap:anywhere}
article p{white-space:pre-wrap}
@media(max-width:760px){main{grid-template-columns:1fr;margin-top:15px;gap:24px}.card{padding:24px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
const form = document.querySelector('form');
const feedback = document.querySelector('#feedback');

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  const admin = form.id === 'admin';
  const data = Object.fromEntries(new FormData(form));

  button.disabled = true;
  feedback.textContent = admin ? 'Consultando…' : 'Enviando…';

  if (admin) document.querySelector('#messages').replaceChildren();

  try {
    const options = admin
      ? {headers: {
          Authorization: 'Basic ' + btoa(
            String.fromCharCode(...new TextEncoder().encode('admin:' + data.password))
          )
        }}
      : {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data)
        };

    const response = await fetch('/api/messages', options);
    const result = await response.json();

    if (!response.ok) throw new Error(result.error || 'Não foi possível concluir.');

    if (admin) {
      feedback.textContent = result.messages.length + ' mensagem(ns) encontrada(s).';

      for (const message of result.messages) {
        const article = document.createElement('article');

        for (const [tag, text] of [
          ['h3', message.name],
          ['p', message.email],
          ['small', new Date(message.created_at).toLocaleString('pt-BR')],
          ['p', message.message]
        ]) {
          const element = document.createElement(tag);
          element.textContent = text;
          article.append(element);
        }

        document.querySelector('#messages').append(article);
      }
    } else {
      feedback.textContent = result.message + ' Protocolo #' + result.id + '.';
    }

    form.reset();
  } catch (error) {
    feedback.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
"""


def install():
    environment = BASE / ".venv"
    if not (environment / "bin/python").exists():
        venv.EnvBuilder(with_pip=True).create(environment)

    subprocess.run(
        [
            str(environment / "bin/python"),
            "-m", "pip", "install", "psycopg[binary]==3.3.2"
        ],
        check=True,
    )

    directory = BASE / "app_teste"
    directory.mkdir(exist_ok=True)

    for name, content in {
        "index.html": PAGE,
        "admin.html": ADMIN,
        "style.css": CSS,
        "app.js": JS,
    }.items():
        target = directory / name
        if target.exists() and not target.with_suffix(target.suffix + ".bak").exists():
            target.with_suffix(target.suffix + ".bak").write_bytes(target.read_bytes())
        target.write_text(content, encoding="utf-8")

    (BASE / "requirements.txt").write_text(
        "psycopg[binary]==3.3.2\n", encoding="utf-8"
    )

    ignore = BASE / ".gitignore"
    existing = ignore.read_text() if ignore.exists() else ""
    entries = [".venv/", ".env", "__pycache__/", "*.bak"]
    missing = [entry for entry in entries if entry not in existing.splitlines()]
    if missing:
        ignore.write_text(existing.rstrip() + "\n" + "\n".join(missing) + "\n")

    print("Instalação concluída.")
    print("Configure DATABASE_URL e ADMIN_PASSWORD antes de iniciar.")
    print("Iniciar: .venv/bin/python py.py")


def database():
    import psycopg

    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Configure DATABASE_URL para um PostgreSQL.")

    return psycopg.connect(
        url,
        connect_timeout=5,
        options="-c statement_timeout=5000",
    )


def migrate():
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(254) NOT NULL,
                message VARCHAR(3000) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def respond(self, status, content, content_type="application/json; charset=utf-8"):
        if not isinstance(content, bytes):
            content = json.dumps(content, ensure_ascii=False).encode()

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; "
            "base-uri 'none'; form-action 'self'"
        )
        self.end_headers()
        self.wfile.write(content)

    def authenticated(self):
        expected = os.environ.get("ADMIN_PASSWORD", "")
        try:
            scheme, encoded = self.headers.get("Authorization", "").split(" ", 1)
            username, password = base64.b64decode(
                encoded, validate=True
            ).decode().split(":", 1)

            return (
                bool(expected)
                and scheme == "Basic"
                and hmac.compare_digest(username.encode(), b"admin")
                and hmac.compare_digest(password.encode(), expected.encode())
            )
        except (ValueError, UnicodeError):
            return False

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/healthz":
            try:
                with database() as connection:
                    connection.execute("SELECT id FROM contact_messages LIMIT 0")
                return self.respond(200, {"status": "ok", "database": "ready"})
            except Exception:
                return self.respond(503, {"status": "unavailable"})

        if path == "/api/messages":
            if not self.authenticated():
                return self.respond(401, {"error": "Credenciais inválidas."})

            try:
                from psycopg.rows import dict_row

                with database() as connection:
                    messages = connection.cursor(row_factory=dict_row).execute("""
                        SELECT id, name, email, message, created_at::text
                        FROM contact_messages
                        ORDER BY id DESC
                        LIMIT 100
                    """).fetchall()

                return self.respond(200, {"messages": messages})
            except Exception:
                return self.respond(503, {"error": "Banco indisponível."})

        routes = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/admin": ("admin.html", "text/html; charset=utf-8"),
            "/style.css": ("style.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }

        if path in routes:
            filename, content_type = routes[path]
            target = BASE / "app_teste" / filename
            if target.is_file():
                return self.respond(200, target.read_bytes(), content_type)

        self.respond(404, {"error": "Página não encontrada."})

    def do_POST(self):
        if self.path != "/api/messages":
            return self.respond(404, {"error": "Página não encontrada."})

        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            return self.respond(403, {"error": "Origem não permitida."})

        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            return self.respond(415, {"error": "Envie JSON."})

        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                return self.respond(413, {"error": "Conteúdo muito grande ou vazio."})

            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError()

            values = [payload.get(key, "") for key in ("name", "email", "message")]
            if not all(isinstance(value, str) for value in values):
                raise ValueError()

            name, email, message = [value.strip() for value in values]

            if not (
                1 <= len(name) <= 100
                and len(email) <= 254
                and re.fullmatch(r"[^\\s@]+@[^\\s@]+\\.[^\\s@]+", email)
                and 1 <= len(message) <= 3000
            ):
                raise ValueError()

        except (ValueError, UnicodeError):
            return self.respond(400, {"error": "Confira nome, e-mail e mensagem."})

        try:
            with database() as connection:
                identifier = connection.execute(
                    """INSERT INTO contact_messages (name, email, message)
                       VALUES (%s, %s, %s) RETURNING id""",
                    (name, email, message),
                ).fetchone()[0]

            self.respond(201, {
                "id": identifier,
                "message": "Mensagem recebida com sucesso.",
            })
        except Exception:
            self.respond(503, {"error": "Não foi possível salvar. Tente novamente."})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--migrate", action="store_true")
    args = parser.parse_args()

    if args.install:
        install()
        return

    if not os.environ.get("ADMIN_PASSWORD"):
        raise SystemExit("Configure ADMIN_PASSWORD antes de iniciar.")

    try:
        migrate()
    except ImportError:
        raise SystemExit(
            "Driver ausente. Execute python3 py.py --install localmente "
            "ou use a imagem PostgreSQL aprovada no Studio."
        )

    if args.migrate:
        print("Tabela preparada.")
        return

    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Servidor iniciado na porta {port}.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()