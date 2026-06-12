# BCA Department Portal

A premium, modern, and feature-rich Web Portal for the Department of Computer Applications (BCA) at National College. This portal streamlines student admissions, upcoming academic and cultural events, dynamic configurations, and administrative dashboard management.

---

## 🚀 Key Features

- **Dynamic Homepage & configurations**: The site settings (welcome message, mission, vision, admission fees, etc.) are managed dynamically from the admin panel database.
- **Online Admission System**: Allows prospective students to register, upload academic credentials (marks sheets, Aadhaar card, TC), and pay their admission fee.
- **Event Registrations**: A calendar of department events/workshops where registered students can sign up, pay fees, and access downloadable tickets.
- **QR-Code Receipt Verification**: Payments generate automated PDF receipts containing a secure verification QR code. Deans/Admins can scan the QR code to verify validity on the fly.
- **Admin Dashboard**: Full CRUD panel for managing syllabus/courses, career opportunities, student projects, photo galleries, downloads, registrations, and payment audits.
- **Robust Authentication**: Separation of user roles with custom session limits and security safeguards for both Students and Administrators.

---

## 🛠️ Tech Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLite (local development), PostgreSQL (production)
- **ORM Integration**: Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend Styling**: Vanilla CSS, Bootstrap 5, and FontAwesome Icons
- **PDF Generation**: ReportLab
- **QR Engine**: python-qrcode
- **Testing**: Unittest framework

---

## 📁 Repository Structure

```text
├── app.py             # Flask application creator & blueprint registration
├── run.py             # Application runner (development entry point)
├── config.py          # Environment configuration variables
├── models.py          # Database schemas (Admin, Student, Faculty, Event, etc.)
├── utils.py           # Helper functions (allowed uploads, PDF generator, QR code builder)
├── init_db.py         # Database initialization and idempotent data seeding script
├── test_app.py        # Automated test cases
├── requirements.txt   # Application dependencies
├── render.yaml        # Render.com Blueprint configuration (deployment)
├── .gitignore         # File patterns excluded from version control
├── routes/            # Module-specific controller blueprints
│   ├── main.py        # Public portal pages
│   ├── student.py     # Student dashboard & registration
│   ├── admission.py   # Fee checkout & application pages
│   ├── event.py       # Event list & registration routes
│   └── admin.py       # Admin controls & reports
└── templates/         # Jinja2 HTML layouts & views
```

---

## 💻 Local Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your local machine.

### 2. Clone and Setup Environment
Navigate to the project root directory and create a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database
Initialize tables and seed default settings (super admin, faculty members, demo events, and syllabus details):
```bash
python init_db.py
```
> [!IMPORTANT]
> The seed script creates a default super admin login:
> - **Username**: `admin`
> - **Password**: `adminpassword`

### 5. Run the Application
```bash
python run.py
```
Access the portal locally at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

---

## 🧪 Running Tests

Ensure all functionalities work correctly before code submission:
```bash
python -m unittest test_app.py
```

---

## ☁️ Deployment (Render.com)

This repository is pre-configured for deployment on **Render** using the Blueprint file `render.yaml`.

1. Commit your changes and push them to GitHub.
2. Link your GitHub repository to Render.
3. Select **Blueprints** on Render and choose this repository.
4. Render will automatically provision:
   - A **PostgreSQL database** (linked via `DATABASE_URL`).
   - A **Flask Web Service** served by `gunicorn`.
   - Run the initial migrations and seed settings automatically using `python init_db.py`.
