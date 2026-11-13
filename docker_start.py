"""Container entrypoint: migrations before Gunicorn; no installer at runtime."""
import os
import subprocess
import sys

if os.environ.get("MIGRATE_ON_START", "true").lower() == "true":
    import psycopg
    print("[studio:migrate] starting", flush=True)
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
            if not connection.execute("SELECT pg_try_advisory_lock(736281406)").fetchone()[0]:
                raise RuntimeError("Migration already running")
            subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=True, timeout=180)
    except Exception:
        print("[studio:migrate] failed; application was not started", flush=True)
        raise SystemExit(1)
    print("[studio:migrate] completed", flush=True)
os.execv(sys.executable, [sys.executable, "-m", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-"])
