from django.contrib import admin
from .models import (
    CustomUser, Admin, Program, Branch, Semester, Session,
    Staff, Student, Subject, SubjectAllocation, Book, Library,
    IssuedBook, EnrollmentHistory, Attendance, AttendanceReport,
    LeaveReportStaff, LeaveReportStudent, FeedbackStaff, FeedbackStudent,
    NotificationStaff, NotificationStudent, StudentResult,
)

admin.site.register(CustomUser)
admin.site.register(Admin)
admin.site.register(Program)
admin.site.register(Branch)
admin.site.register(Semester)
admin.site.register(Session)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(SubjectAllocation)
admin.site.register(Book)
admin.site.register(Library)
admin.site.register(IssuedBook)
admin.site.register(EnrollmentHistory)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(LeaveReportStaff)
admin.site.register(LeaveReportStudent)
admin.site.register(FeedbackStaff)
admin.site.register(FeedbackStudent)
admin.site.register(NotificationStaff)
admin.site.register(NotificationStudent)
admin.site.register(StudentResult)