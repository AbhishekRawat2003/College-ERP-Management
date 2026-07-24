from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, Session, StudentResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['subject'].queryset = Subject.objects.filter(allocations__staff=staff).distinct()
        context = {
            'form': resultForm,
            'page_title': "Edit Student's Result"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Edit Student's Result"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                session = form.cleaned_data.get('session')
                internal_marks = form.cleaned_data.get('internal_marks_obtained')
                theory_marks = form.cleaned_data.get('theory_marks_obtained')
                practical_marks = form.cleaned_data.get('practical_marks_obtained')

                result, created = StudentResult.objects.update_or_create(
                    student=student, subject=subject, session=session,
                    defaults={
                        'internal_marks_obtained': internal_marks,
                        'theory_marks_obtained': theory_marks,
                        'practical_marks_obtained': practical_marks,
                    }
                )
                messages.success(request, "Result Updated")
                return redirect(reverse('edit_student_result'))
            except Exception as e:
                messages.warning(request, "Result Could Not Be Updated: " + str(e))
        else:
            messages.warning(request, "Result Could Not Be Updated")
        return render(request, "staff_template/edit_student_result.html", context)