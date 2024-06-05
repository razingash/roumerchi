
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, FormView

from tests.forms import LoginCustomUserForm, RegisterCustomUserForm, TestForm, CriterionFormSet, \
    UniqueResultFormSet, TestCriterionFormSet, TestUniqueResultFormSet, TestQuestionFormSet, \
    TestQuestionAnswersFormSet, ChangeCustomUserPasswordForm, ChangeCustomUserForm
from tests.models import CustomUser, Test, TestCriterion, SortingFilters, CriterionFilters
from tests.services import get_profile_info, get_test_info_by_slug, create_new_test_walkthrough, \
    validate_paginator_get_attribute, get_question_answers_formset, get_test_categories, get_filtered_tests, \
    get_test_results, get_test_results_for_guest, custom_exception, CustomException
from tests.utils import DataMixin


# Create your views here.

def page_forbidden_error(request, exception):
    return HttpResponseForbidden('<h1>try more</h1>')

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
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Login', user_uuid=self.request.user.uuid)
        else:
            mix = self.get_user_context(title='Login')
        return context | mix

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})


class SettingsBasePage(LoginRequiredMixin, DataMixin, FormView):
    template_name = 'tests/settings.html'
    form_class = ChangeCustomUserForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='settings', user_uuid=self.request.user.uuid)
            context.update(mix)
            return context | mix

    def form_valid(self, form):
        print('form valid')
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})


class SettingsPasswordPage(LoginRequiredMixin, PasswordChangeView, DataMixin):
    template_name = 'tests/password_reset.html'
    form_class = ChangeCustomUserPasswordForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='password updating', user_uuid=self.request.user.uuid)
            return context | mix

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})



class ProfileView(DetailView, DataMixin):
    model = CustomUser
    template_name = 'tests/profile.html'
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        modified_get = self.request.GET.copy()
        if 'page' in modified_get:
            del modified_get['page']

        criterion = self.request.GET.get('criterion_type')
        sorting = self.request.GET.get('sorting_type')
        category = self.request.GET.get('category_type')
        profile_uuid = self.kwargs.get('profile_uuid')

        criterions = CriterionFilters.choices
        sortings = SortingFilters.choices
        categories = get_test_categories()

        if self.request.user.is_authenticated:
            tests = get_filtered_tests(criterion=criterion, sorting=sorting, category=category, is_guest=False,
                                       profile_uuid=profile_uuid, visitor_uuid=self.request.user.uuid)
        else:
            tests = get_filtered_tests(criterion=criterion, sorting=sorting, category=category,
                                       profile_uuid=profile_uuid, is_guest=True)

        paginator = Paginator(tests, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid, tests=page_obj,
                                        categories=categories, sortings=sortings, criterions=criterions,
                                        modified_get=modified_get)
        else:
            mix = self.get_user_context(title='Profile', categories=categories, sortings=sortings, criterions=criterions,
                                        modified_get=modified_get, tests=tests)
        return context | mix

    def get_object(self, queryset=None):
        profile_uuid = self.kwargs.get('profile_uuid')
        queryset = get_profile_info(profile_uuid=profile_uuid)
        return get_object_or_404(queryset)

    def post(self, request, *args, **kwargs):
        if request.POST.get('request_type') == 'advanced_search':
            return JsonResponse({'message': 'all good'})
        else:
            return JsonResponse({'message': 'mistake'})


class SearchTestsView(ListView, DataMixin):
    model = Test
    template_name = 'tests/search_test.html'
    context_object_name = 'tests'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        modified_get = self.request.GET.copy()
        if 'page' in modified_get:
            del modified_get['page']

        categories = get_test_categories()
        criterions = CriterionFilters.choices
        sortings = SortingFilters.choices

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='tests', user_uuid=self.request.user.uuid, categories=categories,
                                        sortings=sortings, criterions=criterions, modified_get=modified_get)
        else:
            mix = self.get_user_context(title='tests', categories=categories, sortings=sortings, criterions=criterions,
                                        modified_get=modified_get)
        combined_context = context | mix
        return combined_context

    def get_queryset(self, underway_tests=None):
        criterion = self.request.GET.get('criterion_type')
        sorting = self.request.GET.get('sorting_type')
        category = self.request.GET.get('category_type')
        #underway_tests = self.request.POST.getlist('underway_tests[]')
        print(criterion, sorting, category)
        if self.request.user.is_authenticated:
            user_uuid = self.request.user.uuid
            queryset = get_filtered_tests(criterion=criterion, sorting=sorting, category=category, is_guest=False,
                                          visitor_uuid=user_uuid)
        else:
            guest_uuid = self.request.GET.get('gu')
            queryset = get_filtered_tests(criterion=criterion, sorting=sorting, category=category, is_guest=True,
                                          visitor_uuid=guest_uuid)
        return queryset

    def post(self, request, *args, **kwargs):
        if request.POST.get('request_type') == 'advanced_search':
            #underway_tests = request.POST.getlist('underway_tests[]')
            return JsonResponse({'message': 'all good'})
        else:
            return JsonResponse({'message': 'mistake'})


class TestView(DetailView, DataMixin):
    model = Test
    template_name = 'tests/test.html'
    context_object_name = 'test'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            test_results = get_test_results(test=self.object, user=self.request.user)
            mix = self.get_user_context(title='Profile', user_uuid=self.request.user.uuid, test_results=test_results)
        else:
            guest_uuid = self.request.GET.get('gu')
            test_results = get_test_results_for_guest(test=self.object, guest_uuid=guest_uuid)
            mix = self.get_user_context(title='Profile', test_results=test_results)
        return context | mix

    def get_object(self, queryset=None):
        test_slug = self.kwargs.get('test_preview')
        queryset = get_test_info_by_slug(test_slug=test_slug)
        return get_object_or_404(queryset)

    def post(self, request, *args, **kwargs):
        request_type = request.POST.get('request_type')
        sender_uuid = request.POST.get('sender_uuid')
        test_id = request.POST.get('test_id')
        selected_answers = request.POST.getlist('selected_answers[]')
        if request_type == 'new_walkthrough':
            if sender_uuid is not None:
                if self.request.user.is_authenticated:
                    test_result, criterions = create_new_test_walkthrough(sender_uuid=sender_uuid, test_id=test_id,
                                                                          answers=selected_answers, is_guest=False)
                    if 'result_1' in criterions and 'result_2' in criterions:
                        return JsonResponse({'status': 400, 'message': test_result, 'criterions': criterions})
                    return JsonResponse({'status': 200, 'message': test_result, 'criterions': criterions})
                else:
                    test_result, criterions = create_new_test_walkthrough(sender_uuid=sender_uuid, test_id=test_id,
                                                                          answers=selected_answers, is_guest=True)
                    if 'result_1' in criterions and 'result_2' in criterions:
                        return JsonResponse({'status': 400, 'message': test_result, 'criterions': criterions})
                    return JsonResponse({'status': 200, 'message': test_result, 'criterions': criterions})
        return JsonResponse({'message': 'something get wrong'})


class CreateTest(LoginRequiredMixin, FormView, DataMixin):
    template_name = 'tests/create_test.html'
    form_class = TestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.method == 'GET':
                criterion_formset = CriterionFormSet()
                unique_result_formset = UniqueResultFormSet()
            else:
                criterion_formset = CriterionFormSet(self.request.POST)
                unique_result_formset = UniqueResultFormSet(self.request.POST)
            mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, formset=criterion_formset,
                                        formset2=unique_result_formset)
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


class CreateTestQuestions(LoginRequiredMixin, FormView, DataMixin):
    template_name = 'tests/create_test_questions.html'
    form_class = TestQuestionFormSet

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            answers_formset = get_question_answers_formset(self.request.user.id)
            if answers_formset is None:
                return redirect(reverse_lazy('profile', kwargs={'profile_uuid': self.request.user.uuid}))
            context = self.get_context_data(answers_formset=answers_formset)
            return self.render_to_response(context)
        raise CustomException('Green Error: in CreateTestQuestions someone tried to gain access without authorization', error_type=1)

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            answers_formset = get_question_answers_formset(self.request.user.id)
            if answers_formset is None:
                return redirect(reverse_lazy('profile', kwargs={'profile_uuid': self.request.user.uuid}))
            context = self.get_context_data(answers_formset=answers_formset)
            return self.render_to_response(context)
        raise CustomException('Black Error: in CreateTestQuestions someone tried POST request without authorization', error_type=4)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answers_formset = context.get('answers_formset')
        if self.request.method == 'GET':
            question_formset = TestQuestionFormSet()
            answer_formset = answers_formset()
        else:
            question_formset = TestQuestionFormSet(self.request.POST)
            answer_formset = answers_formset(self.request.POST)
        mix = self.get_user_context(title='new test', user_uuid=self.request.user.uuid, formset=question_formset,
                                    formset2=answer_formset)
        return context | mix

    def form_valid(self, form):
        context = self.get_context_data()

        question_formset = context['formset']
        answer_formset = context['formset2']
        test_instance = Test.objects.get(author_id=self.request.user.id, status=1)
        criterions = TestCriterion.objects.filter(test=test_instance)
        question_formset.instance = test_instance

        if question_formset.is_valid() and answer_formset.is_valid():
            for question_form in question_formset:
                question = question_form.save(commit=False)
                question.save()
                for i, answer_form in enumerate(answer_formset):
                    if answer_form.has_changed():
                        answer = answer_form.save(commit=False)
                        answer.question = question
                        answer.criterion = criterions[i]
                        answer.save()
            return redirect(self.get_success_url())
        else:
            print(question_formset.errors)
            print(answer_formset.errors)
        return self.render_to_response(self.get_context_data(form=question_formset, formset2=answer_formset))

    def get_success_url(self):
        user_uuid = self.request.user.uuid
        return reverse_lazy('profile', kwargs={'profile_uuid': user_uuid})


class ChangeTestInfo(LoginRequiredMixin, FormView, DataMixin):
    template_name = 'tests/change_test.html'
    form_class = TestForm

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            test_obj = self.get_object()
            if self.request.user == test_obj.author:
                context = self.get_context_data(test_obj=test_obj)
                return self.render_to_response(context)
            raise CustomException('Green Error: in ChangeTestInfo someone tried to gain access without authorization', error_type=1)
        raise CustomException('Green Error: in ChangeTestInfo someone tried to gain access without authorization', error_type=1)

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            test_obj = self.get_object()
            if self.request.user == test_obj.author:
                context = self.get_context_data(test_obj=test_obj)
                return self.render_to_response(context)
            raise CustomException(f'Black Error: in ChangeTestInfo user: {self.request.user.uuid} tried POST without being the author', error_type=4)
        raise CustomException('Black Error: in ChangeTestInfo someone tried POST request without authorization', error_type=4)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            test_obj = context.get('test_obj')

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


class ChangeTestQuestions(LoginRequiredMixin, FormView, DataMixin):
    template_name = 'tests/change_test_questions.html'
    form_class = TestForm
    paginate_by = 1

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            test_obj = self.get_object()
            if self.request.user == test_obj.author:
                context = self.get_context_data(test_obj=test_obj)
                return self.render_to_response(context)
            raise CustomException('Green Error: in ChangeTestQuestions someone tried to gain access without authorization', error_type=1)
        raise CustomException('Green Error: in ChangeTestQuestions someone tried to gain access without authorization', error_type=1)

    @custom_exception(expected_return=page_forbidden_error(request=None, exception=None))
    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            test_obj = self.get_object()
            if self.request.user == test_obj.author:
                context = self.get_context_data(test_obj=test_obj)
                return self.render_to_response(context)
            raise CustomException(f'Black Error: in ChangeTestQuestions user: {self.request.user.uuid} tried POST without being the author', error_type=4)
        raise CustomException('Black Error: in ChangeTestQuestions someone tried POST request without authorization', error_type=4)

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
