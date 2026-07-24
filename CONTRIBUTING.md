# Contributing to EduMa (College ERP Management)

Thank you for considering a contribution to EduMa! Whether it's a typo fix, a bug report, or a full feature, every contribution helps make this project more useful for institutions and developers. Please read this guide before opening an issue or pull request — it saves everyone time and keeps the project healthy.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Guidelines](#coding-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)

---

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it. Please report unacceptable behavior to the maintainer listed in the README.

---

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/College-ERP-Management.git
   cd College-ERP-Management
   ```
3. Add the upstream repository so you can keep your fork in sync:
   ```bash
   git remote add upstream https://github.com/AbhishekRawat2003/College-ERP-Management.git
   ```
4. Follow the [Development Setup](#development-setup) section to get the project running locally.

---

## How to Contribute

- **Bug fixes** — always welcome, small or large.
- **New features** — please open an issue first to discuss scope before investing time in a large PR.
- **Documentation** — README improvements, code comments, or this file itself.
- **Tests** — coverage for views, forms, and models is especially appreciated.
- **Templates/UI** — improvements to existing templates, as long as they follow the existing pattern (see [Coding Guidelines](#coding-guidelines)).

---

## Reporting Bugs

Before opening a bug report, please:

1. Search [existing issues](../../issues) to avoid duplicates.
2. Confirm the bug is reproducible on the latest `main` branch.

A good bug report includes:

- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Error traceback** (if any) — paste the full traceback, not just the last line
- Your environment: OS, Python version, Django version
- Screenshots, if the bug is UI-related

---

## Suggesting Features

Open an issue describing:

- The problem the feature solves
- Your proposed approach (if you have one)
- Any alternatives you considered

This helps avoid duplicate effort and lets maintainers weigh in before code is written.

---

## Development Setup

### Prerequisites
- Python 3.11+
- Git

### Setup

```bash
git clone https://github.com/<your-username>/College-ERP-Management.git
cd College-ERP-Management

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
```

### Seed test data (recommended for development)

```bash
python manage.py seed_dummy_data
```

This populates the database with realistic Programs, Branches, Semesters, Subjects, Staff, Subject Allocations, and Students — much faster than creating records by hand through the UI. Use `--flush` to wipe and regenerate:

```bash
python manage.py seed_dummy_data --flush
```

### Run the server

```bash
python manage.py runserver
```

---

## Project Structure

A quick orientation before you start editing:

```
main_app/
├── models.py            # Program, Branch, Semester, Subject, SubjectAllocation,
│                         # Staff, Student, Session, Attendance, StudentResult, etc.
├── forms.py              # All Django forms
├── hod_views.py           # Admin/HOD-side views
├── staff_views.py         # Staff-side views
├── student_views.py       # Student-side views
├── urls.py                # URL routing
├── EmailBackend.py         # Custom email-based auth backend
├── management/commands/
│   └── seed_dummy_data.py  # Test data seeder
└── templates/
    ├── hod_template/       # Admin/HOD templates
    ├── staff_template/     # Staff templates
    └── student_template/   # Student templates
```

The academic hierarchy is **Program → Branch → Semester → Subject**. Keep this in mind when adding new features — most academic data hangs off a `Semester`, which belongs to a `Program` + `Branch` pair.

---

## Coding Guidelines

- **Follow existing patterns.** Most `add_*`/`edit_*` templates render generically via `main_app/form_template.html` — don't hardcode form fields into a template unless there's a specific reason (e.g. custom JS behavior).
- **Model primary keys.** Several models (`Staff`, `Student`, `Admin`) use a `OneToOneField(..., primary_key=True)` to `CustomUser` instead of Django's default `id`. Always use `.pk` (not `.id`) when you need the primary key generically, since these models don't have an `id` field.
- **Use `admin_id`/`pk` in lookups**, not `id`, for `Staff`/`Student`/`Admin` — e.g. `get_object_or_404(Student, admin_id=student_id)`.
- **View functions must always return an `HttpResponse`.** Never `return None` or bare `return` from a view or an `except` block — Django will raise a 500 error.
- **PEP 8** for Python code — 4-space indentation, no tabs.
- **Templates** — keep Bootstrap/AdminLTE class conventions consistent with existing templates.
- **No secrets in code.** Never commit API keys, passwords, or `.env` files.

---

## Commit Message Guidelines

Use clear, descriptive commit messages. Prefixing with a type is encouraged:

```
feat: add semester-wise attendance summary
fix: resolve NoReverseMatch on staff deletion
docs: update README seeding instructions
refactor: simplify subject allocation queryset
```

---

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes, following the [Coding Guidelines](#coding-guidelines).
3. Test your changes locally (see [Testing](#testing)).
4. Commit and push:
   ```bash
   git add .
   git commit -m "feat: describe your change"
   git push origin feature/your-feature-name
   ```
5. Open a Pull Request against `main`, describing:
   - What the PR changes and why
   - How you tested it
   - Any related issue number (e.g. `Closes #12`)
6. Be responsive to review feedback — small follow-up commits are fine, no need to force-push unless requested.

PRs that touch models should include the corresponding migration file.

---

## Testing

Before submitting a PR:

- Run the app locally and manually verify the affected flow (HOD/Staff/Student, whichever your change touches).
- If you added a model field, confirm `python manage.py makemigrations` produces a clean migration with no unexpected prompts.
- If you touched a view that's reachable from the sidebar, click through the corresponding sidebar links to make sure nothing 500s.
- Prefer adding an automated test (Django `TestCase`) for new view/form logic where practical — the project doesn't yet have full test coverage, so any addition helps.

---

Thanks again for contributing to EduMa! 🎓