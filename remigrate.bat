@echo off
"venv\Scripts\alembic.exe" downgrade base
"venv\Scripts\alembic.exe" upgrade head
