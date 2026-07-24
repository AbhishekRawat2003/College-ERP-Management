import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from . import forms, models
from datetime import date


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(allocations__staff=staff).distinct()
    total_subject = subjects.count()

    # Students taught by this staff = students whose current_semester matches
    # any semester this staff has an allocated subject in
    semesters = subjects.values_list('semester', flat=True).distinct()
    total_students = Student.objects.filter(current_semester__in=semesters).count()

    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    attendance_list_qs = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list_qs.count()

    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)

    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.first_name) + ' ' + str(staff.admin.last_name) + ' (' + str(staff.department) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, "staff_template/erpnext_staff_home.html", context)

def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(allocations__staff=staff).distinct()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }
    return render(request, 'staff_template/staff_take_attendance.html', context)


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(allocations__staff=staff).distinct()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }
    return render(request, 'staff_template/staff_update_attendance.html', context)




@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            current_semester=subject.semester, session=session)
        student_data = []
        for student in students:
            data = {
                "id": student.admin.id,
                "name": student.admin.last_name + " " + student.admin.first_name
            }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return HttpResponse(json.dumps([]), content_type='application/json', safe=False)




@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        attendance = Attendance(session=session, subject=subject, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, admin_id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return HttpResponse("Error: " + str(e))

    return HttpResponse("OK")




@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)



def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffPasswordForm(request.POST or None)
    context = {'staff': staff, 'form': form, 'page_title': 'My Profile'}
    if request.method == 'POST':
        if form.is_valid():
            password = form.cleaned_data.get('password')
            admin = staff.admin
            admin.set_password(password)
            admin.save()
            messages.success(request, "Password Updated! Please login again.")
            return redirect(reverse('user_login'))
        else:
            messages.error(request, "Invalid Data Provided")
    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)




def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(allocations__staff=staff).distinct()
    sessions = Session.objects.all()
    context = {
        'page_title': 'Result Upload',
        'subjects': subjects,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            session_id = request.POST.get('session')
            internal_marks = request.POST.get('internal_marks_obtained') or 0
            theory_marks = request.POST.get('theory_marks_obtained') or 0
            practical_marks = request.POST.get('practical_marks_obtained') or 0

            student = get_object_or_404(Student, admin_id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            session = get_object_or_404(Session, id=session_id)

            data, created = StudentResult.objects.update_or_create(
                student=student, subject=subject, session=session,
                defaults={
                    'internal_marks_obtained': internal_marks,
                    'theory_marks_obtained': theory_marks,
                    'practical_marks_obtained': practical_marks,
                }
            )
            messages.success(request, "Scores Saved" if created else "Scores Updated")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form: " + str(e))
    return render(request, "staff_template/staff_add_result.html", context)



@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        session_id = request.POST.get('session')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        result = StudentResult.objects.get(student=student, subject=subject, session=session)
        result_data = {
            'internal_marks_obtained': result.internal_marks_obtained,
            'theory_marks_obtained': result.theory_marks_obtained,
            'practical_marks_obtained': result.practical_marks_obtained,
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')

#library
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']


        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category )
        books.save()
        alert = True
        return render(request, "staff_template/add_book.html", {'alert':alert})
    context = {
        'page_title': "Add Book"
    }
    return render(request, "staff_template/add_book.html",context)



def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student = form.cleaned_data.get('student')
            obj.book = form.cleaned_data.get('book')
            obj.save()
            alert = True
            return render(request, "staff_template/issue_book.html", {'obj': obj, 'alert': alert})
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/issue_book.html", {'form': form})


def view_issued_book(request):
    issuedBooks = IssuedBook.objects.select_related('student', 'book').all()
    details = []
    for issued in issuedBooks:
        days = (date.today() - issued.issued_date).days
        fine = 0
        if days > 14:
            fine = (days - 14) * 5
        details.append((
            issued.book.name,
            issued.book.isbn,
            issued.issued_date,
            issued.expiry_date,
            fine
        ))
    return render(request, "staff_template/view_issued_book.html", {'issuedBooks': issuedBooks, 'details': details})


