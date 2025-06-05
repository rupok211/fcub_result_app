# FCUB Result Management System

A web-based result management system built with **Flask** and **SQLite**, designed for First Capital University of Bangladesh. It allows students to check their results and admins to manage result data securely.

---

## Features

- Student result viewing by ID and batch
- Admin login system with session management
- Add/Edit/Delete student results and subjects
- Password hashing for secure admin authentication
- Validation for subject names and grades
- Auto-creates default admin if not present

---

Tech Stack

Backend:** Python 3, Flask, SQLAlchemy
Database:** SQLite
Frontend:** HTML5, CSS3 (Jinja2 templates)
Security:** Werkzeug for password hashing

---

## Directory Structure

```
fcub-result-system/
│
├── app.py                  # Main Flask app
├── database.py             # Models and DB setup
├── templates/              # HTML templates
│   ├── home.html
│   ├── admin_login.html
│   ├── admin_result.html
│   ├── admin_manage_results.html
│   ├── admin_add_edit_result.html
│   ├── view_result.html
│   └── student_result.html  
└── fcub_results.db         # SQLite database 
```

---

## Getting Started (Local Development)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/fcub-result-system.git
   cd fcub-result-system
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask flask_sqlalchemy werkzeug
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   ```
   http://localhost:5000
   ```

---

## Default Admin Login

> Admin user is created automatically on first run.

- **Username:** ``  
- **Password:** ``

> Change the password after first login!

---

## Validation Rules

- Subject names: Letters, numbers, spaces only
- Grades must be one of: `A+`, `A`, `A-`, `B+`, `B`, `C`, `D`, `F`

---

## Deployment (PythonAnywhere Example)

1. Upload your files via PythonAnywhere or GitHub.
2. Open a Bash console and install packages:
   ```bash
   pip3.10 install --user flask flask_sqlalchemy werkzeug
   ```
3. Ensure `fcub_results.db` is writable.
4. Set the **WSGI configuration file** to point to `app.py`.
5. Reload the web app from the PythonAnywhere dashboard.






