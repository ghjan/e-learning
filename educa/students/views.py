from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin
from courses.models import Course
from .forms import CourseEnrollForm


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    # This method is called when valid form data has been POSTed.
    # It should return an HttpResponse.
    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView, self).get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if course:
            if 'module_id' in self.kwargs:
                # get current module
                context['module'] = course.modules.get(id=self.kwargs['module_id'])
            else:
                # get first module
                context['module'] = course.modules.all()[0]
        return context


import json
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import *


@csrf_exempt
def studentCourseDetail(request, pk, module_id):
    queryset = Course.objects.filter(id=pk, students__in=[request.user])
    course = module = None
    if queryset:
        course = queryset.get()
        if course:
            if module_id:
                module = course.modules.get(id=module_id)
            else:
                module = course.modules.all()[0]
    if course:
        # course = str(course)
        course = convert_obj_to_dicts(course)
        print("course:{}".format(course))
    if module:
        # module = str(module)
        module = convert_obj_to_dicts(module)
        print("module:{}".format(module))
    return HttpResponse({'course': course, 'module': module
                         }, content_type='application/json')
