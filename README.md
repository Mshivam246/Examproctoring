# Online Examination System With AI Proctoring (Django + MySQL)

This project is a starter implementation of an online exam platform with AI-assisted proctoring checks.

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Django
- Database: MySQL
- Proctoring: Webcam + behavior monitoring + person/noise checks

## Features Included

- User authentication (login/logout)
- Exam listing dashboard
- Exam attempt page with questions and choices
- Automatic score calculation on submit
- AI proctoring event logging:
  - tab switch detection
  - window blur detection
  - fullscreen exit detection
  - no person / multiple person detection (TensorFlow.js COCO-SSD)
  - high noise detection (Web Audio API)
- Admin panel to manage exams, questions, choices, submissions, and proctor events

## Project Structure

- `online_exam/` Django project settings and root URL config
- `exams/` exam app (models, views, urls, admin, migrations)
- `templates/` HTML templates
- `static/` CSS and JavaScript assets

## Local Setup

### 1) Install the tools you need

Before the project can run, you need three things on your computer:

- Python
- MySQL Server
- A terminal or command prompt

If MySQL is not installed yet, download and install MySQL Server from the official MySQL website. During installation, note the password you create for the MySQL root user. You will need it later.

After installation, make sure the MySQL service is running.

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

This creates an isolated Python environment for the project, so its packages do not affect other projects on your computer.

### 3) Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4) Create the configuration file

```powershell
copy .env.example .env
```

Open the `.env` file and fill in your MySQL details.

You should understand these values:

- `DB_NAME`: the name of the database that will store the exam data
- `DB_USER`: the MySQL username, usually `root` on a local setup
- `DB_PASSWORD`: the MySQL password you created during installation
- `DB_HOST`: the computer where MySQL is running, usually `127.0.0.1` for your own machine
- `DB_PORT`: the MySQL port, usually `3306`

Example:

```ini
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=online_exam_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5) Create the MySQL database

Open MySQL Workbench or the MySQL command line and run this command:

```sql
CREATE DATABASE online_exam_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

This creates the empty database where Django will store users, exams, questions, answers, and proctoring logs.

### 6) Run the database migrations

```powershell
python manage.py migrate
```

This tells Django to create all the required tables inside MySQL.

### 7) Create an admin user

```powershell
python manage.py createsuperuser
```

This creates the first administrator account. You will use it to log in to the admin panel and manage exams.

### 8) Start the server

```powershell
python manage.py runserver
```

### 9) Open the app in your browser

- `http://127.0.0.1:8000/accounts/login/`
- `http://127.0.0.1:8000/admin/`

### 10) Confirm MySQL is connected correctly

If the project starts without database errors, the MySQL connection is working.

If you see a database error, check these items first:

- MySQL Server is installed and running
- The database name in `.env` matches the one you created
- The MySQL username and password are correct
- Port `3306` is open and not being used by another service

## Deployment

This project now includes a production-ready Django setup for platforms like Render.

### Quick deploy on Render

1. Push this repository to GitHub.
2. In Render, create a new `Web Service` from the repository.
3. Render can detect `render.yaml`, or you can set these manually:

```text
Build Command: bash build.sh
Start Command: gunicorn online_exam.wsgi:application
```

4. Set environment variables in Render:

```ini
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=False
ALLOWED_HOSTS=your-service-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-service-name.onrender.com
USE_SQLITE=True
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=replace-with-a-strong-password
```

### Database options

- `USE_SQLITE=True`: easiest deployment path for demos and small projects
- `DATABASE_URL=...`: recommended for hosted databases
- MySQL variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) still work for existing local MySQL setups

Example hosted MySQL URL:

```ini
DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/DB_NAME
```

If your host requires TLS, also set:

```ini
DB_SSL_REQUIRE=True
```

### Automatic admin setup on Render Free

Render free web services do not provide shell access, so this project now runs:

```text
python manage.py bootstrap_admin
```

during the build after migrations.

If these environment variables are set, the deploy will automatically create or update the admin account:

```ini
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=replace-with-a-strong-password
```

Then log in at:

```text
https://your-service-name.onrender.com/admin/
```

## Notes

- Browser permission for camera and microphone is required for proctoring checks.
- AI checks run client-side in the exam page and send suspicious activity events to the backend.
- For production, add stronger identity verification, secure browser mode, encrypted media recording storage, and advanced anti-cheat models.
