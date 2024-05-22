
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, FormView

from tests.forms import LoginCustomUserForm, RegisterCustomUserForm, TestForm, CriterionFormSet, \
    UniqueResultFormSet, TestCriterionFormSet, TestUniqueResultFormSet, TestQuestionFormSet, \
    TestQuestionAnswersFormSet
from tests.models import CustomUser, Test
from tests.services import get_profile_info, get_test_info_by_slug, create_new_test_respondent, custom_exception, \
    get_user_tests, get_user_completed_tests, validate_paginator_get_attribute
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
    form_class = TestForm

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


class ChangeTestInfo(FormView, LoginRequiredMixin, DataMixin):
    template_name = 'tests/change_test.html'
    form_class = TestForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            test_obj = self.get_object()

            if self.request.method == 'GET':
                criterions_forms = TestCriterionFormSet(instance=test_obj)
                results_forms = TestUniqueResultFormSet(instance=test_obj)
            else:
                criterions_forms = TestCriterionFormSet(self.request.POST, instance=test_obj)
                results_forms = TestUniqueResultFormSet(self.request.POST, instance=test_obj)
            mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, results_forms=results_forms,
                                        criterions_forms=criterions_forms, preview_slug=self.kwargs['test_preview'])
            return context | mix

    def form_valid(self, form):
        context = self.get_context_data()
        criterion_formset = context['criterions_forms']
        unique_result_formset = context['results_forms']
        if form.is_valid() and criterion_formset.is_valid() and unique_result_formset.is_valid():
            form.save()
            criterion_formset.save()
            unique_result_formset.save()
            return redirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        test_instance = Test.objects.only('id', 'preview', 'category', 'description').get(preview_slug=self.kwargs['test_preview'])
        kwargs['instance'] = test_instance
        return kwargs

    def get_object(self):
        test_preview = self.kwargs['test_preview']
        return get_object_or_404(Test, preview_slug=test_preview)

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})


class ChangeTestQuestions(FormView, LoginRequiredMixin, DataMixin):
    template_name = 'tests/change_test_questions.html'
    form_class = TestForm
    paginate_by = 1

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            test_obj = self.get_object()
            page_number = self.request.GET.get('page')

            if self.request.method == 'GET':
                question_formset = TestQuestionFormSet(instance=test_obj, prefix='question')
            else:
                question_formset = TestQuestionFormSet(self.request.POST, instance=test_obj, prefix='question')

            question_paginator = Paginator(question_formset, self.paginate_by)
            question_page_obj = question_paginator.get_page(page_number)

            page_number = validate_paginator_get_attribute(page_number)
            try:
                instance = test_obj.testquestion_set.all()[page_number]
            except IndexError:
                answer_formset = []
            else:
                if self.request.method == 'GET':
                    answer_formset = [TestQuestionAnswersFormSet(instance=instance, prefix=f'answer_{instance.id}')]
                else:
                    answer_formset = [TestQuestionAnswersFormSet(self.request.POST, instance=instance,
                                      prefix=f'answer_{instance.id}')]

            mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, preview_slug=self.kwargs['test_preview'],
                                        answers_forms=answer_formset, question_page_obj=question_page_obj,
                                        questions_forms=question_page_obj.object_list, question_management_form=question_formset.management_form)
            return context | mix

    def form_valid(self, form):
        context = self.get_context_data()
        answers_formsets = context['answers_forms']
        # questions_formset = context['question_page_obj'].paginator.object_list
        #page_number = self.request.GET.get('page')

        question_form = context['questions_forms'][0]

        if context['questions_forms'][0].is_valid():
            context['questions_forms'][0].save()
        else:
            print(f'error: {form.errors}')

        if question_form.is_valid():
            question_form.save()
            for answers_formset in answers_formsets:
                if answers_formset.is_valid():
                    print(answers_formset.queryset[0].__dict__)
                    answers_formset.save()
                else:
                    print(f'error {answers_formset.errors}')

            return redirect(self.get_success_url())
        else:
            print(f'error: {question_form.is_valid()}, {question_form.errors}')

        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        test_instance = Test.objects.get(preview_slug=self.kwargs['test_preview']) # .prefetch_related('testquestion_set')
        kwargs['instance'] = test_instance
        return kwargs

    def get_object(self):
        test_preview = self.kwargs['test_preview']
        return get_object_or_404(Test, preview_slug=test_preview)

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})



def logout_user(request):
    logout(request)
    return redirect('search_test')
