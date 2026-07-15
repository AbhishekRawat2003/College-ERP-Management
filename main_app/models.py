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
    start_year = models.DateField()
    end_year = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_year"]

    def __str__(self):
        return f"{self.start_year} - {self.end_year}"


class CustomUser(AbstractUser):
    # FIX: choice keys must be strings to match the CharField below —
    # with int keys (1, 2, 3) `user_type == '1'` never matched, so the
    # post_save signal that creates Admin/Staff/Student records never fired.
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
    # FIX: ImageField/TextField without blank=True force these on every
    # signup (e.g. superuser creation), which realistically breaks onboarding.
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
    # FIX: OneToOneField(primary_key=True) instead of a separate surrogate
    # id + unique FK — this is a strict 1:1 relationship, no need for both.
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="admin"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.admin)


class Branch(models.Model):
    # FIX: OneToOneField(...) -> CharField(...). OneToOneField needs a
    # related model as its first positional arg; these are plain text fields.
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # NOTE: removed session FK from Branch — a branch/department shouldn't
    # be tied to a single academic session. If you need "branch offered in
    # session X", model that as its own M2M / through table.

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)  # FIX: same OneToOneField bug
    # FIX: renamed branch_id -> branch. Django FK fields should be named
    # after the relation, not the column; Django auto-creates `branch_id`
    # as the actual DB column. The old name made `course.branch_id` return
    # a Branch *instance*, which is confusing and error-prone.
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} ({self.code})"


class Book(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)  # FIX: same OneToOneField bug
    author = models.CharField(max_length=200)
    # FIX: PositiveIntegerField -> CharField. ISBNs can have leading zeros
    # and hyphens; storing as an int silently corrupts real ISBNs.
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
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
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
    # FIX: student_id was a free-text CharField — replaced with a real FK.
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # FIX: `models.ForeignKey(book,)` referenced an undefined lowercase
    # `book`, had no on_delete, and was followed by an invalid `//` comment
    # (Python needs `#`). Also dropped the separate `isbn` field — it
    # duplicated data already reachable via `book.isbn`.
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issued_date = models.DateField(auto_now_add=True)  # FIX: auto_now -> auto_now_add
    # (auto_now would silently overwrite issued_date on every future save)
    expiry_date = models.DateField(default=default_expiry)
    # FIX: added — original model had no way to record a book being returned.
    returned_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # FIX: prevents the same book being "issued" twice to the same
        # student on the same day.
        unique_together = ("student", "book", "issued_date")

    def __str__(self):
        # FIX: original referenced undefined globals and tried str + int concat.
        return f"{self.student} - {self.book}"


class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    admin = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="staff"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # FIX: removed stray `// add branch_id` line — invalid syntax that
    # would crash on import. If you want branch on Subject, derive it via
    # `subject.course.branch`, since Subject already links to Course.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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
        # FIX: prevents duplicate attendance rows for the same student/session.
        unique_together = ("student", "attendance")

    def __str__(self):
        return f"{self.student} - {self.attendance}"


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # FIX: CharField(60) -> DateField, so date filtering/sorting actually works.
    date = models.DateField()
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.date}"


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()  # FIX: CharField(60) -> DateField
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
    is_read = models.BooleanField(default=False)  # FIX: added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.staff)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # FIX: added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Drop this if multiple attempts per student/subject are intentional.
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student} - {self.subject}"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    # FIX: compare against string values ('1'/'2'/'3'), matching the
    # CharField choices — the original compared against ints and never fired.
    if created:
        if instance.user_type == CustomUser.HOD:
            Admin.objects.create(admin=instance)
        elif instance.user_type == CustomUser.STAFF:
            Staff.objects.create(admin=instance)
        elif instance.user_type == CustomUser.STUDENT:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # FIX: same string-comparison fix; also guard with hasattr since the
    # related profile may not exist yet (e.g. superusers created without
    # a matching user_type, or the very first save before create runs).
    if instance.user_type == CustomUser.HOD and hasattr(instance, "admin"):
        instance.admin.save()
    elif instance.user_type == CustomUser.STAFF and hasattr(instance, "staff"):
        instance.staff.save()
    elif instance.user_type == CustomUser.STUDENT and hasattr(instance, "student"):
        instance.student.save()