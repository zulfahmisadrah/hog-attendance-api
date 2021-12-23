Neo Presensi API

REST API of Neo Presensi Web Application. Neo Presensi is a Multi-Face Recognition based Student Attendance System using Histogram of Oriented Gradients (HOG).

Crate Python Virtual Environment
```
python -m venv venv
```

Install dependencies
```
pip install -r requirements.txt
```

Crate migration migration
```
alembic revision --autogenerate -m "init tables"
```

run migration
```
alembic upgrade head
```

run app
```
python main.py
```