"""
Django management command to seed the College ERP database with realistic
dummy data for testing (500+ records across all major models).

INSTALLATION:
1. Inside your `main_app` folder, create this structure if it doesn't exist:
       main_app/management/__init__.py
       main_app/management/commands/__init__.py
       main_app/management/commands/seed_dummy_data.py   <-- put THIS file's content here

2. Run:
       python manage.py seed_dummy_data

   To wipe and reseed:
       python manage.py seed_dummy_data --flush

Default password for EVERY generated user (staff + student): 2989
"""

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from main_app.models import (
    CustomUser, Program, Branch, Semester, Subject, Session,
    Staff, Student, SubjectAllocation,
)

DEFAULT_PASSWORD = "2989"

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Karan", "Aryan", "Dev", "Yash", "Kabir", "Anaya",
    "Diya", "Ira", "Myra", "Aadhya", "Saanvi", "Ananya", "Pari", "Riya",
    "Kiara", "Zara", "Navya", "Aarohi", "Priya", "Neha", "Simran", "Tanvi",
    "Rahul", "Vikram", "Amit", "Suresh", "Rajesh", "Manoj", "Deepak", "Sanjay",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Yadav", "Mishra",
    "Tiwari", "Chauhan", "Rawat", "Bisht", "Negi", "Rana", "Thakur", "Joshi",
    "Pandey", "Dubey", "Saxena", "Agarwal", "Malhotra", "Kapoor", "Chopra",
    "Bhatt", "Nair", "Menon", "Reddy", "Rao", "Iyer", "Das",
]

DEPARTMENTS = [
    "Computer Science", "Electronics", "Mechanical", "Civil",
    "Mathematics", "Physics", "Chemistry", "Management",
]

DESIGNATIONS = [
    "Assistant Professor", "Associate Professor", "Professor",
    "Lecturer", "Senior Lecturer", "HOD",
]

SUBJECT_POOL = [
    "Mathematics", "Physics", "Chemistry", "Programming Fundamentals",
    "Data Structures", "Digital Electronics", "Computer Networks",
    "Database Systems", "Operating Systems", "Software Engineering",
    "Web Development", "Environmental Science", "Engineering Drawing",
    "Basic Electrical Engineering", "Communication Skills",
    "Discrete Mathematics", "Computer Organization",
    "Design and Analysis of Algorithms", "Compiler Design",
    "Artificial Intelligence", "Machine Learning", "Cloud Computing",
    "Cyber Security", "Microprocessors", "Control Systems",
]

# Program definitions: (name, type, duration_years, total_semesters)
PROGRAM_DEFS = [
    ("B.Tech", Program.DEGREE, 4, 8),
    ("BCA", Program.DEGREE, 3, 6),
    ("MCA", Program.DEGREE, 2, 4),
    ("Diploma in Engineering", Program.DIPLOMA, 3, 6),
    ("D.Pharm", Program.DIPLOMA, 2, 4),
]

# Branches per program name
BRANCH_DEFS = {
    "B.Tech": [("Computer Science Engineering", "CSE"), ("Electronics & Communication", "ECE"),
               ("Mechanical Engineering", "ME"), ("Civil Engineering", "CE")],
    "BCA": [("General", "BCA-GEN")],
    "MCA": [("General", "MCA-GEN")],
    "Diploma in Engineering": [("Computer Science", "DCSE"), ("Mechanical", "DME")],
    "D.Pharm": [("General", "DPH-GEN")],
}

name_cycle_counter = [0]


def next_name():
    """Return a unique-ish (first, last) name pair using rotating combos."""
    i = name_cycle_counter[0]
    first = FIRST_NAMES[i % len(FIRST_NAMES)]
    last = LAST_NAMES[(i // len(FIRST_NAMES)) % len(LAST_NAMES)]
    name_cycle_counter[0] += 1
    return first, last


class Command(BaseCommand):
    help = "Seed the database with 500+ dummy records for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete existing seeded data before creating new data'
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write("Flushing existing data...")
            Student.objects.all().delete()
            Staff.objects.all().delete()
            CustomUser.objects.filter(user_type__in=[CustomUser.STAFF, CustomUser.STUDENT]).delete()
            SubjectAllocation.objects.all().delete()
            Subject.objects.all().delete()
            Semester.objects.all().delete()
            Branch.objects.all().delete()
            Program.objects.all().delete()
            Session.objects.all().delete()

        with transaction.atomic():
            programs = self.create_programs()
            branches = self.create_branches(programs)
            semesters = self.create_semesters(branches)
            subjects = self.create_subjects(semesters)
            sessions = self.create_sessions()
            staff_list = self.create_staff(count=20)
            self.create_subject_allocations(staff_list, subjects, sessions)
            self.create_students(semesters, students_per_semester=30, sessions=sessions)

        self.stdout.write(self.style.SUCCESS("Dummy data seeding complete!"))

    # ---------- PROGRAMS ----------
    def create_programs(self):
        self.stdout.write("Creating Programs...")
        programs = {}
        for name, ptype, duration, total_sem in PROGRAM_DEFS:
            program, _ = Program.objects.get_or_create(
                name=name,
                defaults={
                    'program_type': ptype,
                    'duration_years': duration,
                    'total_semesters': total_sem,
                }
            )
            programs[name] = program
        self.stdout.write(f"  -> {len(programs)} programs created")
        return programs

    # ---------- BRANCHES ----------
    def create_branches(self, programs):
        self.stdout.write("Creating Branches...")
        branches = []
        for program_name, branch_defs in BRANCH_DEFS.items():
            program = programs[program_name]
            for branch_name, code in branch_defs:
                branch, _ = Branch.objects.get_or_create(
                    program=program, code=code,
                    defaults={'name': branch_name}
                )
                branches.append(branch)
        self.stdout.write(f"  -> {len(branches)} branches created")
        return branches

    # ---------- SEMESTERS ----------
    def create_semesters(self, branches):
        self.stdout.write("Creating Semesters...")
        semesters = []
        for branch in branches:
            total_sem = branch.program.total_semesters
            for num in range(1, total_sem + 1):
                semester, _ = Semester.objects.get_or_create(
                    program=branch.program, branch=branch, number=num
                )
                semesters.append(semester)
        self.stdout.write(f"  -> {len(semesters)} semesters created")
        return semesters

    # ---------- SUBJECTS ----------
    def create_subjects(self, semesters):
        self.stdout.write("Creating Subjects...")
        subjects = []
        subject_types = [Subject.THEORY, Subject.PRACTICAL, Subject.BOTH]
        for semester in semesters:
            branch_code = semester.branch.code if semester.branch else "GEN"
            for idx in range(1, 4):  # 3 subjects per semester
                subj_type = subject_types[idx % len(subject_types)]
                subj_name = SUBJECT_POOL[(semester.number * 3 + idx) % len(SUBJECT_POOL)]
                code = f"{branch_code}{semester.number}{idx:02d}"

                if subj_type == Subject.THEORY:
                    max_theory, max_practical = 70, 0
                    min_theory, min_practical = 28, 0
                elif subj_type == Subject.PRACTICAL:
                    max_theory, max_practical = 0, 70
                    min_theory, min_practical = 0, 28
                else:
                    max_theory, max_practical = 50, 20
                    min_theory, min_practical = 20, 8

                subject, _ = Subject.objects.get_or_create(
                    semester=semester, code=code,
                    defaults={
                        'name': subj_name,
                        'subject_type': subj_type,
                        'credits': random.choice([2, 3, 4]),
                        'max_theory_marks': max_theory,
                        'max_practical_marks': max_practical,
                        'max_internal_marks': 30,
                        'min_passing_theory_marks': min_theory,
                        'min_passing_practical_marks': min_practical,
                    }
                )
                subjects.append(subject)
        self.stdout.write(f"  -> {len(subjects)} subjects created")
        return subjects

    # ---------- SESSIONS ----------
    def create_sessions(self):
        self.stdout.write("Creating Sessions...")
        sessions = []
        year_pairs = [(2023, 2027), (2024, 2028), (2025, 2029)]
        for start, end in year_pairs:
            session, _ = Session.objects.get_or_create(
                start_year=date(start, 7, 1), end_year=date(end, 6, 30)
            )
            sessions.append(session)
        self.stdout.write(f"  -> {len(sessions)} sessions created")
        return sessions

    # ---------- STAFF ----------
    def create_staff(self, count=20):
        self.stdout.write("Creating Staff...")
        staff_list = []
        for i in range(1, count + 1):
            first, last = next_name()
            email = f"staff{i}.{first.lower()}@college.edu"
            user = CustomUser.objects.create_user(
                email=email,
                password=DEFAULT_PASSWORD,
                user_type=CustomUser.STAFF,
                first_name=first,
                last_name=last,
            )
            user.gender = random.choice(['M', 'F'])
            user.address = f"House No. {random.randint(1,999)}, Sector {random.randint(1,50)}, Faridabad"
            user.save()

            staff = user.staff
            staff.employee_id = f"EMP{i:04d}"
            staff.designation = random.choice(DESIGNATIONS)
            staff.department = random.choice(DEPARTMENTS)
            staff.save()
            staff_list.append(staff)
        self.stdout.write(f"  -> {len(staff_list)} staff created (password: {DEFAULT_PASSWORD})")
        return staff_list

    # ---------- SUBJECT ALLOCATIONS ----------
    def create_subject_allocations(self, staff_list, subjects, sessions):
        self.stdout.write("Creating Subject Allocations...")
        count = 0
        session = sessions[-1]  # allocate current/latest session
        for idx, subject in enumerate(subjects):
            staff = staff_list[idx % len(staff_list)]
            _, created = SubjectAllocation.objects.get_or_create(
                staff=staff, subject=subject, session=session
            )
            if created:
                count += 1
        self.stdout.write(f"  -> {count} subject allocations created")

    # ---------- STUDENTS ----------
    def create_students(self, semesters, students_per_semester, sessions):
        """
        Creates `students_per_semester` students for EVERY semester, all
        placed in the SAME session used for Subject Allocation (the latest
        session) -- this guarantees Take Attendance / Add Result screens
        always have a full class of students to pick from for any subject.
        """
        self.stdout.write("Creating Students...")
        students = []
        primary_session = sessions[-1]  # matches create_subject_allocations()
        counter = 1
        for semester in semesters:
            branch = semester.branch
            program = semester.program
            branch_code = branch.code if branch else "GEN"

            for _ in range(students_per_semester):
                first, last = next_name()
                email = f"student{counter}.{first.lower()}@college.edu"
                user = CustomUser.objects.create_user(
                    email=email,
                    password=DEFAULT_PASSWORD,
                    user_type=CustomUser.STUDENT,
                    first_name=first,
                    last_name=last,
                )
                user.gender = random.choice(['M', 'F'])
                user.address = f"House No. {random.randint(1,999)}, Sector {random.randint(1,50)}, Faridabad"
                user.save()

                student = user.student
                student.roll_number = f"{branch_code}{counter:05d}"
                student.enrollment_number = f"ENR2024{counter:06d}"
                student.program = program
                student.branch = branch
                student.current_semester = semester
                student.session = primary_session
                student.save()
                students.append(student)
                counter += 1

        self.stdout.write(f"  -> {len(students)} students created across {len(semesters)} semesters "
                           f"({students_per_semester} per semester, password: {DEFAULT_PASSWORD})")
        return students