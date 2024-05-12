import json

from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView

from tests.forms import LoginCustomUserForm, RegisterCustomUserForm
from tests.models import CustomUser, Test
from tests.services import get_profile_info, get_test_info_by_slug, create_new_test_respondent, custom_exception
from tests.utils import DataMixin


# Create your views here.

class RegistrationPageView(CreateView, DataMixin):
    form_class = RegisterCustomUserForm
    template_name = 'tests/register.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        mix = self.get_user_context(title='Registration')
        return context | mix

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('search_test')


class LoginPageView(LoginView, DataMixin):
    template_name = 'tests/login.html'
    form_class = LoginCustomUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        mix = self.get_user_context(title='Login')
        return context | mix

    def get_success_url(self):
        user_id = self.request.user.id
        return reverse_lazy('profile', kwargs={'profile_id': user_id})

class ProfileView(DetailView, DataMixin):
    model = CustomUser
    template_name = 'tests\profile.html'
    context_object_name = 'user'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        queryset = get_profile_info(profile_id=profile_id)
        return get_object_or_404(queryset)


class SearchTestsView(DataMixin, ListView):
    model = Test
    ordering = ['-id']
    template_name = 'tests/search_test.html'
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='tests', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='tests')
        return context | mix

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class TestView(DetailView, DataMixin):
    model = Test
    template_name = 'tests/test.html'
    context_object_name = 'test'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = context.get('test').id
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        test_slug = self.kwargs.get('test_preview')
        queryset = get_test_info_by_slug(test_slug=test_slug)
        return get_object_or_404(queryset)

    @custom_exception
    def post(self, request, *args, **kwargs):
        print(request.POST)
        request_type = request.POST.get('request_type')
        sender_id = request.POST.get('sender_id')
        test_id = request.POST.get('test_id')
        selected_answers = request.POST.getlist('selected_answers[]')
        if request_type == 'new_walkthrough':
            if sender_id is not None:
                result, criterions = create_new_test_respondent(sender_id=sender_id, test_id=test_id, answers=selected_answers)
                return JsonResponse({'status': 200, 'message': result, 'criterions': criterions})
        return JsonResponse({'message': 'something get wrong'})


def logout_user(request):
    logout(request)
    return redirect('search_test')
