from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    """Academic session / batch, e.g. 2025-2029."""

    start_year = models.DateField()
    end_year = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_year"]

    def __str__(self):
        return f"{self.start_year} - {self.end_year}"


class CustomUser(AbstractUser):
    HOD = "1"
    STAFF = "2"
    STUDENT = "3"
    USER_TYPE = (
        (HOD, "HOD"),
        (STAFF, "Staff"),
        (STUDENT, "Student"),
    )
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=1, choices=USER_TYPE, default=HOD)
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    address = models.TextField(blank=True)
    fcm_token = models.TextField(blank=True, default="")  # For Firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class Admin(models.Model):
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="admin"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.admin)


# NEW: Program replaces the old "Course" concept at the top of the academic
# hierarchy — B.Tech, BCA, MCA, MBA, D.Pharm, Diploma, Polytechnic, etc.
# Program is what Branch, Semester and Student now hang off of.
class Program(models.Model):
    DEGREE = "D"
    DIPLOMA = "P"
    PROGRAM_TYPE = (
        (DEGREE, "Degree"),
        (DIPLOMA, "Diploma"),
    )

    name = models.CharField(max_length=120)  # e.g. "B.Tech", "BCA", "D.Pharm"
    program_type = models.CharField(max_length=1, choices=PROGRAM_TYPE, default=DEGREE)
    duration_years = models.PositiveSmallIntegerField()
    total_semesters = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Branch(models.Model):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="branches",blank=True, null= True
    )
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("program", "code")

    def __str__(self):
        return f"{self.name} ({self.code})"

class Semester(models.Model):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="semesters"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=True, blank=True, related_name="semesters"
    )
    number = models.PositiveSmallIntegerField()  # 1, 2, 3 ...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("program", "branch", "number")
        ordering = ["program", "branch", "number"]

    def __str__(self):
        branch_part = f" - {self.branch.code}" if self.branch_id else ""
        return f"{self.program.name}{branch_part} Sem {self.number}"


class Book(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=17, unique=True)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} [{self.isbn}]"


class Student(models.Model):
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="student"
    )
    roll_number = models.CharField(max_length=30, unique=True)
    enrollment_number = models.CharField(max_length=30, unique=True)
    program = models.ForeignKey(
        Program, on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )
    current_semester = models.ForeignKey(
        Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name="current_students"
    )
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.last_name}, {self.admin.first_name}"


class Library(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)


def default_expiry():
    return (datetime.today() + timedelta(days=14)).date()


class IssuedBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issued_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(default=default_expiry)
    returned_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "book", "issued_date")

    def __str__(self):
        return f"{self.student} - {self.book}"



class Staff(models.Model):
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="staff"
    )
    employee_id = models.CharField(max_length=30, unique=True,null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"



class Subject(models.Model):
    THEORY = "T"
    PRACTICAL = "P"
    BOTH = "B"
    SUBJECT_TYPE = (
        (THEORY, "Theory"),
        (PRACTICAL, "Practical"),
        (BOTH, "Theory + Practical"),
    )

    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="subjects"
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    subject_type = models.CharField(max_length=1, choices=SUBJECT_TYPE, default=THEORY)
    credits = models.PositiveSmallIntegerField(default=0)
    max_theory_marks = models.PositiveSmallIntegerField(default=0)
    max_practical_marks = models.PositiveSmallIntegerField(default=0)
    max_internal_marks = models.PositiveSmallIntegerField(default=0)
    min_passing_theory_marks = models.PositiveSmallIntegerField(default=0)
    min_passing_practical_marks = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"



class SubjectAllocation(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="allocations")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="allocations")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="allocations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("staff", "subject", "session")

    def __str__(self):
        return f"{self.staff} -> {self.subject} ({self.session})"


class EnrollmentHistory(models.Model):
    ACTIVE = "A"
    PROMOTED = "P"
    BACKLOG = "B"
    DROPPED = "D"
    STATUS = (
        (ACTIVE, "Active"),
        (PROMOTED, "Promoted"),
        (BACKLOG, "Backlog"),
        (DROPPED, "Dropped"),
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollment_history"
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS, default=ACTIVE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "session", "semester")
        verbose_name_plural = "Enrollment histories"

    def __str__(self):
        return f"{self.student} - {self.semester} ({self.get_status_display()})"


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("subject", "date")  # one attendance session per subject/day

    def __str__(self):
        return f"{self.subject} - {self.date}"


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "attendance")

    def __str__(self):
        return f"{self.student} - {self.attendance}"


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.date}"


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff} - {self.date}"


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.staff)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.staff)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)


# UPDATE: StudentResult now scoped by SubjectAllocation (subject + session +
# staff together) rather than just Subject, and split test/exam marks into
# the internal/theory/practical fields that match Subject's max-marks
# fields. Kept simple field names for now — this is the table flagged
# earlier as the "future" Marks/Result module.
class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    internal_marks_obtained = models.FloatField(default=0)
    theory_marks_obtained = models.FloatField(default=0)
    practical_marks_obtained = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "session")

    def __str__(self):
        return f"{self.student} - {self.subject}"

    @property
    def total_obtained(self):
        return (
            self.internal_marks_obtained
            + self.theory_marks_obtained
            + self.practical_marks_obtained
        )


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == CustomUser.HOD:
            Admin.objects.create(admin=instance)
        elif instance.user_type == CustomUser.STAFF:
            Staff.objects.create(admin=instance)
        elif instance.user_type == CustomUser.STUDENT:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == CustomUser.HOD and hasattr(instance, "admin"):
        instance.admin.save()
    elif instance.user_type == CustomUser.STAFF and hasattr(instance, "staff"):
        instance.staff.save()
    elif instance.user_type == CustomUser.STUDENT and hasattr(instance, "student"):
        instance.student.save()