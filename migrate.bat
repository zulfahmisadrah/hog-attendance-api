@echo off
"venv\Scripts\alembic.exe" revision --autogenerate -m "init tables"
"venv\Scripts\alembic.exe" upgrade head
