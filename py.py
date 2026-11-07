
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

# Configurações
BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app_teste"
PORT = 8000

# Criar pasta
APP_DIR.mkdir(parents=True, exist_ok=True)

# Página estática
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Meu App Teste</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            font-family: Arial, sans-serif;
            background: #f5f6f8;
        }
        main {
            background: white;
            padding: 50px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 8px 30px #00000010;
        }
        h1 { color: #171717; }
        p { color: #666; }
        button {
            padding: 12px 24px;
            border: 0;
            border-radius: 8px;
            background: #171717;
            color: white;
            cursor: pointer;
        }
        button:hover { background: #444; }
    </style>
</head>
<body>
    <main>
        <h1>Meu App de Teste</h1>
        <p>Aplicação estática funcionando!</p>
        <button onclick="alert('Tudo funcionando!')">
            Testar aplicação
        </button>
    </main>
</body>
</html>
"""

# Criar arquivo
index = APP_DIR / "index.html"
index.write_text(HTML, encoding="utf-8")

print("Aplicação criada com sucesso!")
print(f"Pasta: {APP_DIR}")
print(f"Arquivo: {index}")

# Iniciar servidor
handler = partial(
    SimpleHTTPRequestHandler,
    directory=str(APP_DIR)
)

server = ThreadingHTTPServer(("127.0.0.1", PORT), handler)

print(f"\nServidor: http://localhost:{PORT}")
print("Pressione CTRL+C para encerrar.\n")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    server.server_close()
