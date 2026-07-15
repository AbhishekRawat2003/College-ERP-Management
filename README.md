<div align="center">

# 🎓 EduMa — College ERP Management System

### A Full-Stack Enterprise Resource Planning Solution for Educational Institutions

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Framework-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

**EduMa** streamlines everything a college needs to run day-to-day — student records, staff operations, attendance, results, leave management, and feedback — inside one clean, role-based platform.

[Live Demo](https://syncx.pythonanywhere.com) • [Report Bug](../../issues) • [Request Feature](../../issues)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Core Data Models](#-core-data-models)
- [Authentication Flow](#-authentication-flow)
- [Getting Started](#-getting-started)
- [Demo Credentials](#-demo-credentials)
- [Screenshots](#-screenshots)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [Support the Project](#-support-the-project)
- [License](#-license)
- [Contact](#-contact--support)

---

## 🎯 About

**EduMa (College ERP)** is a comprehensive, open-source ERP system built with **Python and Django** for schools, colleges, and universities. It brings students, staff, and administrators onto a single unified platform — replacing scattered spreadsheets and manual paperwork with structured, role-based digital workflows.

### ✨ Why EduMa?

| | |
|---|---|
| 🚀 **Modern Stack** | Built on Django for stability, security, and rapid development |
| 👥 **Multi-Role Architecture** | Dedicated portals for Admin, Staff, and Students |
| 🔒 **Secure by Design** | Role-based access control + Google reCAPTCHA authentication |
| 📊 **Data-Driven** | Visual dashboards for attendance, results, and performance |
| 📱 **Responsive** | Fully usable across desktop, tablet, and mobile |
| 🌍 **Open Source** | MIT licensed — free to use, modify, and contribute to |

---

## 🚀 Features

### 👨‍💼 Admin (HOD) Dashboard
- 📈 Analytics overview — student/staff performance, course & subject stats
- 👥 Full CRUD for staff members
- 🎓 Full CRUD for student records
- 📚 Course management
- 📖 Subject management & staff-subject assignment
- 📅 Academic session/term management
- ✅ Attendance monitoring across all classes
- 💬 Feedback review from students & staff
- 🏖️ Leave request approval/rejection

### 👨‍🏫 Staff Portal
- 📊 Performance dashboard for assigned subjects
- ✏️ Mark and update student attendance
- 📝 Enter and revise examination results
- 🏖️ Apply for personal leave
- 💭 Send feedback directly to admin

### 🎓 Student Portal
- 📊 Personal dashboard — attendance, results, leave status at a glance
- 📅 Attendance history tracking
- 🎯 View examination results/grades
- 🏖️ Submit leave requests
- 💬 Send feedback to HOD

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Backend** | Python, Django Framework |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Database** | SQLite (development), PostgreSQL (production-ready) |
| **Authentication** | Django Auth (custom email backend) + Google reCAPTCHA |
| **Deployment** | PythonAnywhere / Procfile-based hosting |

---

## 🗂 Project Structure

```
College-ERP/
│
├── college_management_system/      # Django project configuration
│   ├── settings.py                 # App settings, database, static files
│   ├── urls.py                     # Root URL dispatcher
│   └── wsgi.py                     # WSGI entry point for deployment
│
├── main_app/                       # Core Django application
│   ├── migrations/                 # Database migration files
│   ├── templates/
│   │   └── main_app/
│   │       ├── admin_templates/    # HOD/Admin views
│   │       ├── staff_templates/    # Staff views
│   │       └── student_templates/  # Student views
│   ├── static/                     # App-level static files
│   ├── models.py                   # All database models
│   ├── views.py                    # Role-based view logic
│   ├── forms.py                    # Django forms
│   ├── urls.py                     # App-level URL routes
│   └── EmailBackend.py             # Custom email authentication backend
│
├── media/                          # User-uploaded files (profile photos)
├── Showcase/                       # README screenshots
├── reports_and_resource/           # Supporting documents
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── college-erp.yml                 # Conda environment definition
├── Procfile                        # Deployment config (PythonAnywhere)
├── db.sqlite3                      # Development database
└── README.md
```

---

## 🧠 Core Data Models

The system revolves around **three user roles**, each with a distinct login, dashboard, and permission scope:

| Role | Description | Key Capabilities |
|---|---|---|
| **HODAdmin** | Head of Department / Administrator | Full CRUD on staff, students, courses, subjects, sessions; views all attendance & results; manages leave approvals & feedback |
| **Staff** | Teaching faculty | Marks attendance, enters results, applies for leave, sends feedback to admin |
| **Student** | Enrolled student | Views own attendance & results, applies for leave, sends feedback |

**Key models** (`main_app/models.py`):

| Model | Purpose |
|---|---|
| `CustomUser` | Extended Django user with `user_type` (1 = Admin, 2 = Staff, 3 = Student) |
| `AdminHOD` | Admin profile linked to `CustomUser` |
| `Staffs` | Staff profile with department/address info |
| `Students` | Student profile linked to course, session & profile picture |
| `Courses` | Academic course (e.g. B.Sc Computer Science) |
| `Subjects` | Subject under a course, assigned to a staff member |
| `SessionYearModel` | Academic year/session tracking |
| `Attendance` | Attendance session record per subject per date |
| `AttendanceReport` | Individual student attendance status per session |
| `LeaveReportStaff` / `LeaveReportStudent` | Leave request records |
| `FeedbackStaffs` / `FeedbackStudent` | Feedback messages sent to admin |
| `StudentResult` | Exam marks per student per subject |

---

## 🔐 Authentication Flow

EduMa uses a **custom authentication backend** (`EmailBackend.py`) that allows users to log in with **email instead of username**. Post-login redirection is driven by `user_type`, routing each user straight to their correct dashboard (Admin / Staff / Student).

> ⚠️ If you modify authentication logic, make sure the `user_type`-based routing stays intact — it's what keeps each role confined to its own portal.

---

## 📥 Getting Started

### Prerequisites
- ✅ [Git](https://git-scm.com/)
- ✅ [Python 3.x](https://www.python.org/downloads/)
- ✅ [pip](https://pip.pypa.io/en/stable/installing/)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AbhishekRawat2003/College-ERP-Management.git
cd College-ERP-Management
```

### 2️⃣ Set Up a Virtual Environment

**Option A — Conda (recommended)**
```bash
conda env create -f college-erp.yml
conda activate Django-env
```

**Option B — venv**

Windows:
```bash
python -m venv venv
source venv/scripts/activate
```

macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Linux:
```bash
virtualenv .
source bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Settings
Open `settings.py` and update:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```
> ⚠️ **Security Note:** Never use `ALLOWED_HOSTS = ['*']` in production!

### 5️⃣ Set Up the Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6️⃣ Run the Development Server
```bash
# Windows
python manage.py runserver

# macOS/Linux
python3 manage.py runserver
```

🎉 Visit **http://127.0.0.1:8000** in your browser.

---

## 🔑 Demo Credentials

| Role | Email | Password |
|---|---|---|
| 👨‍🎓 **Student** | `studentone@student.com` | `studentone` |
| 👨‍🏫 **Staff** | `staffone@staff.com` | `staffone` |

---

## 📸 Screenshots

<div align="center">
<img src="Showcase/Screenshot_04.png" width="45%" />
<img src="Showcase/Screenshot_03.png" width="45%" />
<img src="Showcase/Screenshot_01.png" width="45%" />
<img src="Showcase/Screenshot_02.png" width="45%" />
</div>

---

## 🗺️ Roadmap

### ✅ Completed
- [x] Multi-role authentication system
- [x] Complete CRUD for all entities
- [x] Attendance management system
- [x] Result management (Class-Based Views)
- [x] Leave application workflow
- [x] Feedback system
- [x] Email notifications
- [x] Google reCAPTCHA integration
- [x] Profile management for all roles
- [x] Dynamic dashboard analytics
- [x] Responsive design
- [x] Password reset functionality

### 🔜 Planned
- [ ] SMS notifications
- [ ] Advanced reporting & analytics
- [ ] Online examination module
- [ ] Library management system
- [ ] Fee management integration
- [ ] Timetable generator
- [ ] Parent portal

---

## 🤝 Contributing

Contributions are what make open source great. Any help — big or small — is genuinely appreciated!

1. Fork the project
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines before opening an issue or PR.

---

## 💖 Support the Project

If EduMa helped you, consider:

- ⭐ Starring this repository
- 🐛 Reporting bugs you encounter
- 💡 Suggesting new features via issues
- 📢 Sharing it with other developers
- 👨‍💻 Contributing code

---

## 📄 License

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 📞 Contact & Support

- 📧 **Email:** abhirawthdr@gmail.com
- 🐛 **Issues:** [GitHub Issues](../../issues)
- 💬 **Discussions:** [GitHub Discussions](../../discussions)

<div align="center">

**Made with ❤️ by [Abhishek Rawat](https://github.com/AbhishekRawat2003)**

*If this project helped you, consider giving it a ⭐!*

</div>