Neo Presensi API

REST API of Neo Presensi Web Application. Neo Presensi is a Multi-Face Recognition based Student Attendance System using Histogram of Oriented Gradients (HOG).

Go to root project dir
```
cd /var/www/neoattendance_api
```

Crate Python Virtual Environment
```
python -m venv venv
```

Activate venv

Windows
```
.\venv\Scripts\activate
```
Linux
```
source venv/bin/activate
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

Production
start
```
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log
```
stop
```
pkill gunicorn
```