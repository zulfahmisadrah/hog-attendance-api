@echo off
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-config=logging.yml --log-level=debug
