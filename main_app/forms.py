from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *
from . import models


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    # def clean_email(self, *args, **kwargs):
    #     formEmail = self.cleaned_data['email'].lower()
    #     if self.instance.pk is None:  # Insert
    #         if CustomUser.objects.filter(email=formEmail).exists():
    #             raise forms.ValidationError(
    #                 "The given email is already registered")
    #     else:  # Update
    #         dbEmail = self.Meta.model.objects.get(
    #             id=self.instance.pk).admin.email.lower()
    #         if dbEmail != formEmail:  # There has been changes
    #             if CustomUser.objects.filter(email=formEmail).exists():
    #                 raise forms.ValidationError("The given email is already registered")

    #     return formEmail

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                pk=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")
    
        return formEmail
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'address' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['roll_number','enrollment_number','program','branch','current_semester','session',]


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['employee_id','designation','department']


# class CourseForm(FormSettings):
#     def __init__(self, *args, **kwargs):
#         super(CourseForm, self).__init__(*args, **kwargs)

#     class Meta:
#         fields = ['name']
#         model = Course


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = [
            'semester',
            'code',
            'name',
            'subject_type',
            'credits',
            'max_theory_marks',
            'max_practical_marks',
            'max_internal_marks',
            'min_passing_theory_marks',
            'min_passing_practical_marks',]


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields +["roll_number",
            'enrollment_number',
            'program',
            'branch',
            'current_semester',
            'session',] 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields+[ 
            'employee_id',
            'designation',
            'department',]


class EditResultForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = [
            'student',
            'subject',
            'session',
            'internal_marks_obtained',
            'theory_marks_obtained',
            'practical_marks_obtained',
            ]

#todos
# class TodoForm(forms.ModelForm):
#     class Meta:
#         model=Todo
#         fields=["title","is_finished"]

#issue book

class IssueBookForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        label="Book"
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Student"
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class":"form-control"})




class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['program','name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'program_type', 'duration_years','total_semesters',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class SemesterForm(FormSettings):

    class Meta:
        model = Semester
        fields = [
            "program",
            "branch",
            "number",
        ]

class SubjectAllocationForm(FormSettings):

    class Meta:
        model = SubjectAllocation
        fields = [
            "staff",
            "subject",
            "session",
        ]
class SubjectAllocationForm(FormSettings):

    class Meta:
        model = SubjectAllocation
        fields = [
            "staff",
            "subject",
            "session",
        ]