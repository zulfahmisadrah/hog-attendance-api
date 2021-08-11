@echo off
"E:\Projects\Python\hog-attendance-api\venv\Scripts\alembic.exe" revision --autogenerate -m "init tables"
"E:\Projects\Python\hog-attendance-api\venv\Scripts\alembic.exe" upgrade head
