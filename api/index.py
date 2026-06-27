import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/")
    def error_page():
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    @app.get("/{path:path}")
    def catch_all(path: str):
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
