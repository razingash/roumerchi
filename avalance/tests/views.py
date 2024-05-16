import json

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, FormView

from tests.forms import LoginCustomUserForm, RegisterCustomUserForm, CreateTestForm, CreateTestCriterionForm, \
    CreateTestUniqueResultForm, CriterionFormSet, UniqueResultFormSet
from tests.models import CustomUser, Test, TestCriterion, TestUniqueResult
from tests.services import get_profile_info, get_test_info_by_slug, create_new_test_respondent, custom_exception, \
    get_user_tests, get_user_completed_tests
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
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})

class ProfileView(DetailView, DataMixin):
    model = CustomUser
    template_name = 'tests/profile_user_tests.html'
    context_object_name = 'user'
    paginate_by = 100

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            tests = get_user_tests(user_id=self.request.user.id)

            paginator = Paginator(tests, self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid, tests=page_obj)
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        profile_uuid = self.kwargs.get('profile_uuid')
        queryset = get_profile_info(profile_uuid=profile_uuid)
        return get_object_or_404(queryset)


class ProfileCTestsView(DetailView, LoginRequiredMixin, DataMixin):
    model = CustomUser
    template_name = 'tests/profile_completed_tests.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.uuid == self.kwargs.get('profile_uuid'):
                tests = get_user_completed_tests(self.request.user.id)

                paginator = Paginator(tests, self.paginate_by)
                page_number = self.request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid, tests=page_obj)
            else:
                raise Exception('rebuild')
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        profile_uuid = self.kwargs.get('profile_uuid')
        queryset = get_profile_info(profile_uuid=profile_uuid)
        return get_object_or_404(queryset)


class ProfileUTestsView(DetailView, LoginRequiredMixin, DataMixin):
    model = CustomUser
    template_name = 'tests/base_profile.html'
    context_object_name = 'user'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs.get('profile_uuid'))
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid)
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        profile_uuid = self.kwargs.get('profile_uuid')
        queryset = get_profile_info(profile_uuid=profile_uuid)
        return get_object_or_404(queryset)


class SearchTestsView(DataMixin, ListView):
    model = Test
    ordering = ['-id']
    template_name = 'tests/search_test.html'
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='tests', user_uuid=self.request.user.uuid)
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
            mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid)
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


class CreateTest(FormView, LoginRequiredMixin, DataMixin):
    template_name = 'tests/create_test.html'
    form_class = CreateTestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, formset=CriterionFormSet(),
                                        formset2=UniqueResultFormSet())
            return context | mix

    def form_valid(self, form):
        parent_form = form.save(commit=False)
        parent_form.author = self.request.user
        parent_form.save()

        criterion_formsets = CriterionFormSet(self.request.POST, instance=parent_form)
        unique_result_fromsets = UniqueResultFormSet(self.request.POST, instance=parent_form)
        if criterion_formsets.is_valid() and unique_result_fromsets.is_valid():
            for formset in criterion_formsets:
                formset.save()
            for formset in unique_result_fromsets:
                formset.save()
            return super().form_valid(form)

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})



class ChangeTest(FormView, LoginRequiredMixin, DataMixin):
    template_name = 'tests/change_test.html'
    form_class = CreateTestForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            test_preview = self.kwargs['test_preview']
            #test_id = Test.objects.only('id').get(preview_slug=test_preview)
            #criterions_forms = [CreateTestCriterionForm(instance=criterion) for criterion in TestCriterion.objects.filter(test_id=test_id)]
            #results_forms = [CreateTestUniqueResultForm(instance=result) for result in TestUniqueResult.objects.filter(test_id=test_id)]
            test_instance = Test.objects.prefetch_related('testcriterion_set', 'testuniqueresult_set').get(preview_slug=test_preview)
            criterions_forms = [CreateTestCriterionForm(instance=criterion) for criterion in test_instance.testcriterion_set.all()]
            results_forms = [CreateTestUniqueResultForm(instance=result) for result in test_instance.testuniqueresult_set.all()]

            mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, criterions_forms=criterions_forms, results_forms=results_forms)

            return context | mix

    def form_valid(self, form):
        test_instance = form.save(commit=False)
        test_instance.author = self.request.user
        test_instance.save()

        post_data = self.request.POST
        print(post_data)
        for prefix in post_data.keys():
            if prefix.startswith('criterion'):
                criterion_formset = CreateTestCriterionForm(prefix=prefix, instance=test_instance, data=post_data)
                if criterion_formset.is_valid():
                    criterion_formset.save()
                else:
                    print("Criterion formset errors:", criterion_formset.errors)

            if prefix.startswith('result'):
                unique_result_formset = CreateTestUniqueResultForm(prefix=prefix, instance=test_instance, data=post_data)
                if unique_result_formset.is_valid():
                    unique_result_formset.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        test_instance = Test.objects.only('id', 'preview', 'category', 'description').get(preview_slug=self.kwargs['test_preview'])
        kwargs['instance'] = test_instance
        return kwargs

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})


def logout_user(request):
    logout(request)
    return redirect('search_test')
