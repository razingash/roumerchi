from django.db import transaction
from django import forms
from django.db.models import Count, Q, When, Case

from tests.forms import TestQuestionAnswersForm
from tests.models import CustomUser, Test, Respondent, Response, RespondentResult, TestUniqueResult, TestQuestion, \
    TestCriterion, QuestionAnswerChoice, TestCategories, CriterionFilters, SortingFilters


class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)

def custom_exception(expected_return=None):
    def decorator(func: callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CustomException as e:
                print(f"error:{e}")
                if expected_return is None:
                    pass
                else:
                    return expected_return
        return wrapper
    return decorator

def to_int(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        print('error')
    else:
        return value


def get_test_categories():
    return TestCategories.choices


def get_user_id(user_uuid):
    return CustomUser.objects.only('id').filter(uuid=user_uuid)[0].id

def get_profile_info(profile_uuid):
    return CustomUser.objects.filter(uuid=profile_uuid)

def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testcriterion_set', 'testquestion_set', 'testquestion_set__questionanswerchoice_set')
    queryset = queryset.filter(preview_slug=test_slug)
    return queryset


def get_user_tests(user_id):
    return Test.objects.order_by('-id').filter(author_id=user_id)

def get_test_results(test, user):
    respondent = Respondent.objects.prefetch_related('respondentresult_set', 'response_set').filter(user=user, test=test, is_completed=True)
    if respondent.exists():
        respondent = respondent[0]
        if respondent.respondentresult_set.exists():
            unique_result = respondent.respondentresult_set.last().result.result
            responses = respondent.response_set.select_related('answer__criterion')
            results = {'unique_result': unique_result}
            for response in responses:
                criterion = response.answer.criterion.criterion
                if criterion in results:
                    results[criterion] += 1
                else:
                    results[criterion] = 1
            print(results)

            return results
    return False


def get_user_completed_tests(profile_uuid):
    user_id = CustomUser.objects.only('id').get(uuid=profile_uuid).id
    tests = Respondent.objects.select_related('test').order_by('-id').filter(user_id=user_id)
    return tests

def get_user_created_tests(criterion, sorting, category, profile_uuid):
    user_id = CustomUser.objects.only('id').get(uuid=profile_uuid).id
    tests = get_filtered_tests_for_logged_user(criterion=criterion, sorting=sorting, category=category,
                                               user_uuid=profile_uuid)
    tests = tests.filter(author_id=user_id)
    return tests


def get_filtered_tests_for_unlogged_user(criterion, sorting, category, profile_uuid=None):
    pass


def get_filtered_tests_for_logged_user(criterion, sorting, category, user_uuid=None, profile_uuid=None):
    user_id = get_user_id(user_uuid=user_uuid)
    is_completed = Case(When(respondent__user_id=user_id, respondent__is_completed=True, then=True), default=False) # annotation to mark completed tests
    is_underway = Case(When(respondent__user_id=user_id, respondent__is_completed=False, then=True), default=False) # annotation to mark tests in progress
    filters = Q()
    if profile_uuid is not None:
        profile_user_id = get_user_id(user_uuid=profile_uuid)
        filters &= Q(author_id=profile_user_id)
    if criterion is not None:  # make flat view for special cases, if the orm queries will be ?very different?
        if sorting is not None:
            if category is not None:  # criterion, sorting  and category
                filters &= Q(category=category)
                if sorting == 1: # popularity #
                    attempts_num = Count(Case(When(respondent__user_id=user_id, then=1), default=None))
                    tests = Test.objects.annotate(is_completed=is_completed, attempts_num=attempts_num, is_underway=is_underway)
                    if criterion == 1:  # completed
                        filters &= Q(is_completed=True)
                        tests = tests.filter(filters)
                    elif criterion == 2:  # uncopleted
                        tests = tests.exclude(id__in=Respondent.objects.filter(user_id=user_id).values_list('test_id', flat=True)).filter(filters)
                    elif criterion == 3:  # underway
                        filters &= Q(is_underway=True)
                        tests = tests.filter(filters)
                    else:
                        tests = tests.filter(filters)
                    return tests.order_by('-attempts_num')
                else:
                    tests = Test.objects.annotate(is_completed=is_completed, is_underway=is_underway)
                    if criterion == 1:  # completed
                        filters &= Q(is_completed=True)
                        tests = tests.filter(filters)
                    elif criterion == 2:  # uncopleted
                        tests = tests.exclude(id__in=Respondent.objects.filter(user_id=user_id).values_list('test_id', flat=True)).filter(filters)
                    elif criterion == 3:  # underway
                        filters &= Q(is_underway=True)
                        tests = tests.filter(filters)
                    else:
                        tests = tests.filter(filters)
            else:  # criterion and sorting
                tests = Test.objects.annotate(is_completed=is_completed, is_underway=is_underway)
                if criterion == 1:  # completed
                    filters &= Q(is_completed=True)
                    tests = tests.filter(filters)  # check this
                elif criterion == 2:  # uncopleted
                    tests = tests.exclude(id__in=Respondent.objects.filter(user_id=user_id).values_list('test_id', flat=True)).filter(filters)
                elif criterion == 3:  # underway
                    filters &= Q(is_underway=True)
                    tests = tests.filter(filters)
                else:
                    tests = tests.filter(filters)

            if sorting == 3:  # A-z
                tests = tests.order_by('preview_slug')
            elif sorting == 4:  # Z-a
                tests = tests.order_by('-preview_slug')
            else:  # elif sorting == 2: # newness
                tests = tests.order_by('publication_date')
            return tests
        elif category is not None:  # criterion and category
            tests = Test.objects
            if criterion == 1:  # completed
                filters &= Q(attempts_num__gt=0, category=category)
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway, attempts_num=Count('respondent', filter=Q(respondent__user_id=user_id))).filter(filters)
            elif criterion == 2:  # uncopleted
                filters &= Q(category=category)
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).exclude(id__in=Respondent.objects.filter(user_id=user_id).values_list('test_id', flat=True)).filter(filters)
            elif criterion == 3:  # underway
                filters &= Q(is_underway=True)
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters)
            else:
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters)
            return tests
        else:  # only criterions
            tests = Test.objects
            if criterion == 1:  # completed
                filters &= Q(attempts_num__gt=0, is_completed=True)
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway, attempts_num=Count('respondent', exclude=Q(respondent__user_id=user_id))).filter(filters)
            elif criterion == 2:  # uncopleted
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).exclude(id__in=Respondent.objects.filter(user_id=user_id).values_list('test_id', flat=True)).filter(filters)
            elif criterion == 3:  # underway
                filters &= Q(is_underway=True)
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters)
            else:
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters)
            return tests
    elif category is not None:
        filters &= Q(category=category)
        tests = Test.objects
        if sorting is not None:  # category and sorting
            if sorting == 1:  # by popularity with selected category
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway, attempts_num=Count('respondent')).filter(filters).order_by('-attempts_num')
            elif sorting == 3:  # A-z with selected category
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('preview_slug')
            elif sorting == 4:  # Z-a with selected category
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('-preview_slug')
            else:  # elif sorting == 2:  # by newness with selected category
                tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('publication_date')
            return tests
        else:  # only categories
            tests = Test.objects.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters)
            return tests
    elif sorting is not None:  # only sorting
        tests = Test.objects
        if sorting == 1:  # popularity
            tests = tests.annotate(is_completed=is_completed, is_underway=is_underway, attempts_num=Count('respondent')).filter(filters).order_by('-attempts_num')
        elif sorting == 3:  # A-z
            tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('preview_slug')
        elif sorting == 4:  # Z-a
            tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('-preview_slug')
        else:  # elif sorting == 2: # newness
            tests = tests.annotate(is_completed=is_completed, is_underway=is_underway).filter(filters).order_by('publication_date')
        return tests

@custom_exception(expected_return=None)
def get_filtered_tests(criterion, sorting, category, user_uuid=None, profile_uuid=None): # add all validators here
    if criterion is None and sorting is None and category is None and profile_uuid is None:
        visitor_id = get_user_id(user_uuid=user_uuid)
        is_completed = Case(When(respondent__user_id=visitor_id, respondent__is_completed=True, then=True), default=False)
        tests = Test.objects.annotate(is_completed=is_completed).order_by('-id')
        return tests
    elif criterion is None and sorting is None and category is None:
        visitor_id = get_user_id(user_uuid=user_uuid)
        profile_id = get_user_id(user_uuid=profile_uuid)
        is_completed = Case(When(respondent__user_id=visitor_id, respondent__is_completed=True, then=True), default=False)
        tests = Test.objects.annotate(is_completed=is_completed).filter(author_id=profile_id).order_by('-id')
        return tests
    if criterion is not None:
        criterion = to_int(criterion)
        criteries = [choice.value for choice in CriterionFilters]
        if criterion not in criteries:
            criterion = None
    if sorting is not None:
        sorting = to_int(sorting)
        sortings = [choice.value for choice in SortingFilters]
        if sorting not in sortings:
            sorting = None
    if category is not None:
        category = to_int(category)
        categories = [choice.value for choice in TestCategories]
        if category not in categories:
            category = None
    print(criterion, sorting, category, user_uuid, profile_uuid)
    if profile_uuid is not None:
        pass
    if user_uuid is None:
        return get_filtered_tests_for_unlogged_user(criterion=criterion, sorting=sorting, category=category, profile_uuid=profile_uuid)
    elif CustomUser.objects.filter(uuid=user_uuid).exists():
        return get_filtered_tests_for_logged_user(criterion=criterion, sorting=sorting, category=category, user_uuid=user_uuid, profile_uuid=profile_uuid)
    else:
        raise CustomException('something went wrong')


def get_question_answers_formset(user_id):
    answers_amount = Test.objects.prefetch_related('testcriterion_set').filter(author_id=user_id, status=1)
    answers_amount = answers_amount.last().testcriterion_set.count()
    formset = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0,
                                          min_num=answers_amount, max_num=answers_amount)
    return formset

def get_question_answer_counter(user_id):
    question_id = []
    for question in Test.objects.prefetch_related('testquestion_set').filter(author_id=user_id, status=1).last().testquestion_set.all():
        question_id.append(question.id)
    count = QuestionAnswerChoice.objects.filter(question__in=question_id).count()
    return count


def calculate_test_result(test_id, answers): # добавить проверку на неравенство списков вопросов
    #TestQuestion.objects.prefetch_related('question', 'questionanswerchoice_set').filter(test_id=1)
    questions = TestQuestion.objects.prefetch_related('question__testquestion_set__questionanswerchoice_set').filter(test_id=test_id)
    if questions.exists():
        k = 0
        points = 0
        true_answers = []
        criterions = {criterion.criterion: 0 for criterion in TestCriterion.objects.filter(test_id=test_id)}
        for question in questions:
            for possible_answer in question.questionanswerchoice_set.all():
                if possible_answer.answer == answers[k]:
                    points += possible_answer.weight
                    true_answers.append(possible_answer)
                    criterions[possible_answer.criterion.criterion] += 1
                    k += 1
                    break
        print(criterions)
        result = TestUniqueResult.objects.filter(test_id=test_id, points_min__lte=points, points_max__gte=points)
        if result.exists():
            return result[0], true_answers, criterions
    raise Exception('something get wrong')

@transaction.atomic
def create_new_test_respondent(sender_id, test_id, answers):
    sender_id, test_id = int(sender_id), int(test_id)
    print(answers)
    sender_id = 1
    if Test.objects.filter(id=test_id).exists():
        if CustomUser.objects.filter(id=sender_id).exists(): # for logged users
            result, answers, criterions = calculate_test_result(test_id=test_id, answers=answers)
            if Respondent.objects.filter(user_id=sender_id, test_id=test_id).exists(): # update test results
                print('updating')
                obj = Respondent.objects.prefetch_related('respondentresult_set',
                                                          'response_set').filter(user_id=sender_id, test_id=test_id)[0]
                for i in range(len(answers)):
                    obj.response_set.all()[i].answer = answers[i]

                obj.respondentresult_set.all().update(result=result)

                Response.objects.bulk_update(obj.response_set.all(), ['answer'])
                return result.result, criterions
            else: # create new attempt
                print('new attempt')
                respondent = Respondent.objects.create(user_id=sender_id, test_id=test_id)
                RespondentResult.objects.create(respondent=respondent, result=result)
                Response.objects.bulk_create([Response(respondent=respondent, answer=answer) for answer in answers])

                return result.result, criterions
        else: # for guests
            pass
    raise CustomException('something went wrong')


@custom_exception(expected_return=0)
def validate_paginator_get_attribute(page_number):
    try:
        page_number = int(page_number or 1) - 1
    except ValueError:
        raise CustomException(f'An invalid get attribute was passed during pagination:  {page_number}')
    page_number = 0 if page_number < 0 else page_number
    return page_number

