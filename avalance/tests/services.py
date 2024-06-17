import uuid

from django.db import transaction
from django import forms
from django.db.models import Count, Q, When, Case, Max

from notifications import admin_notification
from tests.exceptions import CustomException, log_and_notify_decorator
from tests.forms import TestQuestionAnswersForm
from tests.models import CustomUser, Test, Respondent, Response, RespondentResult, TestUniqueResult, TestQuestion, \
    TestCriterion, QuestionAnswerChoice, TestCategories, CriterionFilters, SortingFilters, Guest, GuestRespondent, \
    GuestResponse, GuestRespondentResult



@log_and_notify_decorator(expected_return=0)
def to_int(value):
    try:
        value = int(value)
    except (ValueError, TypeError) as e:
        raise CustomException(f'error in to_int(): {e}')
    else:
        return value


def get_test_categories():
    return TestCategories.choices

@log_and_notify_decorator(expected_return=None)
def get_user_id(user_uuid):
    user = CustomUser.objects.only('id').filter(uuid=user_uuid).first().id
    if user:
        return user
    else:
        raise CustomException(f'Impossible error in get_user_id(): {user_uuid}')

def get_guest(guest__uuid): # don't check this because it should be possible
    try:
        guest__uuid = uuid.UUID(str(guest__uuid))
    except (ValueError, TypeError) as e:
        print(f'error: {e}')
        return None
    else:
        if Guest.objects.filter(uuid=guest__uuid).exists():
            return Guest.objects.only('id', 'uuid').get(uuid=guest__uuid)
        else:
            guest = Guest.objects.only('id', 'uuid').create(uuid=guest__uuid)
            return guest

def is_test_ready(test_slug):
    test = Test.objects.filter(preview_slug=test_slug, status=1)
    if test.exists():
        if test.last().questions_amount > 14:
            return True
    return False


def get_profile_info(profile_uuid):
    return CustomUser.objects.filter(uuid=profile_uuid)

def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testcriterion_set', 'testquestion_set', 'testquestion_set__questionanswerchoice_set')
    queryset = queryset.only('id', 'preview', 'description', 'status', 'questions_amount', 'grade', 'reputation')
    queryset = queryset.filter(preview_slug=test_slug)
    return queryset

def get_permission_for_creating_test(user):
    permission = Test.objects.filter(author=user, status__in=[1, 2])
    if permission.exists(): # redirect to changing test page
        return False
    return True

def get_permission_for_creating_test_questions(user):
    permission = Test.objects.filter(author=user, status__in=[1, 2])
    if permission.exists() and permission.last().questions_amount < 150: # redirect to create test questions  page
        return True
    return False

def get_permission_for_test(test):
    if test.status != 3:
        return False
    return True


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

def get_test_results_for_guest(test, guest_uuid):
    if guest_uuid is None:
        return None
    try:
        guest_uuid = uuid.UUID(guest_uuid)
    except ValueError:
        return None
    guest = get_guest(guest__uuid=guest_uuid)
    respondent = GuestRespondent.objects.prefetch_related('guestrespondentresult_set', 'guestresponse_set')
    respondent = respondent.filter(guest=guest, test=test, is_completed=True)
    if respondent.exists():
        respondent = respondent[0]
        if respondent.guestrespondentresult_set.exists():
            unique_result = respondent.guestrespondentresult_set.last().result.result
            responses = respondent.guestresponse_set.select_related('answer__criterion')
            results = {'unique_result': unique_result}
            for response in responses:
                criterion = response.answer.criterion.criterion
                if criterion in results:
                    results[criterion] += 1
                else:
                    results[criterion] = 1

            return results
    return False


def get_user_completed_tests(profile_uuid):
    user_id = get_user_id(user_uuid=profile_uuid)
    tests = Respondent.objects.select_related('test').order_by('-id').filter(user_id=user_id)
    return tests

def get_user_created_tests(criterion, sorting, category, profile_uuid):
    user_id = get_user_id(user_uuid=profile_uuid)
    tests = get_filtered_tests_for_visitor(criterion=criterion, sorting=sorting, category=category,
                                           visitor_uuid=profile_uuid, is_guest=False)
    tests = tests.filter(author_id=user_id)
    return tests


def get_filtered_tests_for_visitor(criterion, sorting, category, is_guest: bool, visitor_uuid=None, profile_uuid=None):
    """In case of duplicates that may occur in the future if storing incomplete attempts to take a test in the
    database, try to use distinct(), or modify is_complete"""
    if is_guest: # for guests
        visitor_id = get_guest(guest__uuid=visitor_uuid)
        if visitor_id is not None:
            visitor_id = visitor_id.id

        is_test_completed = 'guestrespondent__guest_id'
        model = GuestRespondent
        resp = 'guestrespondent'
        filter_by_visitor = 'guest_id'
    else: # for users
        visitor_id = get_user_id(user_uuid=visitor_uuid)
        is_test_completed = 'respondent__user_id'
        model = Respondent
        resp = 'respondent'
        filter_by_visitor = 'user_id'

    test_visitor_contact = {is_test_completed: visitor_id}
    model_filter = {filter_by_visitor: visitor_id}
    filters = Q()
    filters &= Q(status=3)
    is_completed = Max(Case(When(**test_visitor_contact, then=True), default=False))  # annotation to mark completed tests

    if visitor_id is None:
        is_completed = Case(default=False)

    if criterion is None and sorting is None and category is None and profile_uuid is None:
        tests = Test.objects.annotate(is_completed=is_completed).filter(filters).order_by('-id')
        return tests

    if profile_uuid is not None:
        profile_user_id = get_user_id(user_uuid=profile_uuid)
        filters &= Q(author_id=profile_user_id)

    if criterion is None and sorting is None and category is None:
        tests = Test.objects.annotate(is_completed=is_completed).filter(filters).order_by('-id')
        return tests

    if criterion is not None:
        if sorting is not None:
            if category is not None:  # criterion, sorting  and category
                filters &= Q(category=category)
                if sorting == 1:  # popularity #
                    attempts_num = Count(Case(When(**test_visitor_contact, then=1), default=None))
                    tests = Test.objects.annotate(is_completed=is_completed, attempts_num=attempts_num)
                    if criterion == 1:  # completed
                        filters &= Q(is_completed=True)
                        tests = tests.filter(filters)
                    elif criterion == 2:  # uncopleted
                        tests = tests.exclude(
                            id__in=model.objects.filter(**model_filter).values_list('test_id', flat=True)).filter(filters)
                    else:
                        tests = tests.filter(filters)
                    return tests.order_by('-attempts_num')
                else:
                    tests = Test.objects.annotate(is_completed=is_completed)
                    if criterion == 1:  # completed
                        filters &= Q(is_completed=True)
                        tests = tests.filter(filters)
                    elif criterion == 2:  # uncopleted
                        tests = tests.exclude(
                            id__in=model.objects.filter(**model_filter).values_list('test_id', flat=True)).filter(filters)
                    else:
                        tests = tests.filter(filters)
            else:  # criterion and sorting
                tests = Test.objects.annotate(is_completed=is_completed)
                if criterion == 1:  # completed
                    filters &= Q(is_completed=True)
                    tests = tests.filter(filters)  # check this
                elif criterion == 2:  # uncopleted
                    tests = tests.exclude(
                        id__in=model.objects.filter(**model_filter).values_list('test_id', flat=True)).filter(filters)
                else:
                    tests = tests.filter(filters)

            if sorting == 3:  # A-z
                tests = tests.order_by('preview_slug')
            elif sorting == 4:  # Z-a
                tests = tests.order_by('-preview_slug')
            else:  # elif sorting == 2: # newness
                tests = tests.order_by('-publication_date')
            return tests
        elif category is not None:  # criterion and category
            tests = Test.objects
            if criterion == 1:  # completed
                filters &= Q(attempts_num__gt=0, category=category)
                tests = tests.annotate(is_completed=is_completed,
                                       attempts_num=Count(resp, filter=Q(**test_visitor_contact))).filter(filters)
            elif criterion == 2:  # uncopleted
                filters &= Q(category=category)
                tests = tests.annotate(is_completed=is_completed).exclude(
                    id__in=model.objects.filter(**model_filter).values_list('test_id', flat=True)).filter(filters)
            else:
                tests = tests.annotate(is_completed=is_completed).filter(filters)
            return tests
        else:  # only criterions
            tests = Test.objects
            if criterion == 1:  # completed
                filters &= Q(attempts_num__gt=0, is_completed=True)
                tests = tests.annotate(is_completed=is_completed,
                                       attempts_num=Count(resp, exclude=Q(**test_visitor_contact))).filter(filters)
            elif criterion == 2:  # uncopleted
                tests = tests.annotate(is_completed=is_completed).exclude(
                    id__in=model.objects.filter(**model_filter).values_list('test_id', flat=True)).filter(filters)
            else:
                tests = tests.annotate(is_completed=is_completed).filter(filters)
            return tests
    elif category is not None:
        filters &= Q(category=category)
        tests = Test.objects
        if sorting is not None:  # category and sorting
            if sorting == 1:  # by popularity with selected category
                tests = tests.annotate(is_completed=is_completed, attempts_num=Count(resp)).filter(
                    filters).order_by('-attempts_num')
            elif sorting == 3:  # A-z with selected category
                tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('preview_slug')
            elif sorting == 4:  # Z-a with selected category
                tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('-preview_slug')
            else:  # elif sorting == 2:  # by newness with selected category
                tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('-publication_date')
            return tests
        else:  # only categories
            tests = Test.objects.annotate(is_completed=is_completed).filter(filters).order_by('-id')
            return tests
    elif sorting is not None:  # only sorting
        tests = Test.objects
        if sorting == 1:  # popularity
            tests = tests.annotate(is_completed=is_completed, attempts_num=Count(resp)).filter(
                filters).order_by('-attempts_num')
        elif sorting == 3:  # A-z
            tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('preview_slug')
        elif sorting == 4:  # Z-a
            tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('-preview_slug')
        else:  # elif sorting == 2: # newness
            tests = tests.annotate(is_completed=is_completed).filter(filters).order_by('-publication_date')
        return tests

@log_and_notify_decorator(expected_return=lambda *args, **kwargs: get_filtered_tests_for_visitor(kwargs['criterion'], kwargs['sorting'], kwargs['category'], kwargs['is_guest']))
def get_filtered_tests(criterion, sorting, category, is_guest: bool, visitor_uuid=None, profile_uuid=None): # add all validators here
    if visitor_uuid is not None and is_guest:
        try:
            visitor_uuid = uuid.UUID(visitor_uuid)
        except ValueError:
            print('value error') # вызвать кастомную ошибку и в expected_return впихнуть функцию с атрибутами функции без visitor
    if visitor_uuid is None:
        print('visitor_uuid is none') # вызвать кастомную ошибку и в expected_return впихнуть функцию с атрибутами функции без visitor

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
    #print(criterion, sorting, category, visitor_uuid, profile_uuid)
    if is_guest:
        return get_filtered_tests_for_visitor(criterion=criterion, sorting=sorting, category=category,
                                              is_guest=is_guest, visitor_uuid=visitor_uuid,
                                              profile_uuid=profile_uuid).only('id', 'category', 'preview', 'preview_slug')
    else:
        if CustomUser.objects.filter(uuid=visitor_uuid).exists():
            return get_filtered_tests_for_visitor(criterion=criterion, sorting=sorting, category=category,
                                                  profile_uuid=profile_uuid, visitor_uuid=visitor_uuid,
                                                  is_guest=is_guest).only('id', 'category', 'preview', 'preview_slug')
        raise CustomException('something went wrong', error_type=5)

@log_and_notify_decorator(expected_return=None)
def get_question_answers_formset(user_id):
    answers_amount = Test.objects.prefetch_related('testcriterion_set').filter(author_id=user_id, status=1)
    try:
        answers_amount = answers_amount.last().testcriterion_set.count()
    except AttributeError as e:
        raise CustomException(f'Yellow Exception in get_question_answers_formset(). someone tried to create questions without test: {e}')
    formset = forms.inlineformset_factory(TestQuestion, QuestionAnswerChoice, form=TestQuestionAnswersForm, extra=0,
                                          min_num=answers_amount, max_num=answers_amount)
    return formset

def get_question_answer_counter(user_id):
    question_id = []
    for question in Test.objects.prefetch_related('testquestion_set').filter(author_id=user_id, status=1).last().testquestion_set.all():
        question_id.append(question.id)
    count = QuestionAnswerChoice.objects.filter(question__in=question_id).count()
    return count


def calculate_test_result(test_id, answers):
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
    raise CustomException('Yellow Erorr: something get wrong, probably test was generated incorrectly')

def create_new_test_respondent(sender_id, test_id, result, answers: list, is_guest: bool): # both users and guests
    if is_guest: # for guest
        respondent_model, result_model, response_model = GuestRespondent, GuestRespondentResult, GuestResponse
        prefetch_response, prefetch_result = 'guestresponse_set', 'guestrespondentresult_set'
        filter_by_sender = 'guest_id'
        respondent_field = 'guest_respondent'
    else: # for user
        respondent_model, result_model, response_model = Respondent, RespondentResult, Response
        prefetch_response, prefetch_result = 'response_set', 'respondentresult_set'
        filter_by_sender = 'user_id'
        respondent_field = 'respondent'
    model_filter = {filter_by_sender: sender_id}

    if respondent_model.objects.filter(**model_filter, test_id=test_id).exists():  # update test results
        print('updating user')
        obj = respondent_model.objects.prefetch_related(prefetch_result, prefetch_response).get(**model_filter, test_id=test_id)

        related_response_set = getattr(obj, prefetch_response)
        related_respondent_result_set = getattr(obj, prefetch_result)
        responses = related_response_set.all()
        for i in range(len(answers)):
            responses[i].answer = answers[i]

        related_respondent_result_set.all().update(result=result)
        response_model.objects.bulk_update(responses, ['answer'])

        return result.result
    else:  # create new attempt
        print('new user respondent')
        respondent = respondent_model.objects.create(**model_filter, test_id=test_id)
        create_kwargs = {respondent_field: respondent}
        result_model.objects.create(**create_kwargs, result=result)
        response_model.objects.bulk_create([response_model(**create_kwargs, answer=answer) for answer in answers])

        return result.result

@transaction.atomic
@log_and_notify_decorator(result_1=None, result2=None)
def create_new_test_walkthrough(sender_uuid, test_id, answers, is_guest: bool):
    if type(answers) is not list:
        raise CustomException('Red error: answers in create_new_test_respondent() must be list instance', error_type=3)
    if type(is_guest) is not bool:
        is_guest = False
    if is_guest: # for guests
        sender_id = get_guest(guest__uuid=sender_uuid).id
    else: # for users
        sender_id = get_user_id(user_uuid=sender_uuid)
    if sender_id is None:
        result, answers, criterions = calculate_test_result(test_id=test_id, answers=answers)
        return None, criterions
        #raise CustomException(f'somehow, is_guest: {is_guest} completed test without uuid')
    sender_id, test_id = to_int(sender_id), to_int(test_id)
    print(answers)
    if Test.objects.filter(id=test_id).exists(): # both for guest and user
        result, answers, criterions = calculate_test_result(test_id=test_id, answers=answers)
        test_result = create_new_test_respondent(sender_id=sender_id, test_id=test_id, is_guest=is_guest, result=result,
                                                 answers=answers)
        print(test_result)
        return test_result, criterions

    raise CustomException("test doesn't exist")


@log_and_notify_decorator(expected_return=0)
def validate_paginator_get_attribute(page_number):
    try:
        page_number = int(page_number or 1) - 1
    except ValueError:
        raise CustomException(f'An invalid get attribute was passed during pagination:  {page_number}')
    page_number = 0 if page_number < 0 else page_number
    return page_number

def unique_result_points_validation(points, criterions_amount):
    points.sort()
    final_points = []
    if points[0] != 0:
        points[0] = 0

    k = 0
    while k < len(points) - 1:
        minimum = points[k]
        maximum = points[k + 1]

        if k > 0 and minimum <= final_points[-1][-1]:
            minimum = final_points[-1][-1] + 1
            if maximum <= minimum:
                if minimum - maximum == 1:
                    maximum += 1
                else:
                    maximum += minimum
        elif minimum > maximum:
            maximum += minimum
        elif minimum <= maximum:
            maximum += minimum

        final_points.append([minimum, maximum])
        k += 1

    if len(final_points) < criterions_amount:
        raise CustomException('Yellow ValidationError: test created by user was incorrectly generated - questions != criterions')
    elif len(final_points) >= criterions_amount:
        final_points = final_points[:criterions_amount]
    final_points[-1][-1] = 32767

    return final_points

def validate_test_questions(test):
    questions = TestQuestion.objects.prefetch_related('question__testquestion_set__questionanswerchoice_set').filter(test=test)
    if questions.exists():
        questions_weight = []
        for i, question in enumerate(questions):
            questions_weight.append(list())
            for answer_to_question in question.questionanswerchoice_set.all():
                questions_weight[i].append(answer_to_question.weight)
        if test.questions_amount != questions.count:
            test.questions_amount = questions.count()
            test.save()
        return questions_weight
    else:
        raise CustomException('Yellow ValidationError: test created by user was incorrectly generated - questions != criterions')

@log_and_notify_decorator(expected_return=False)
def validate_test_created_by_user(test_id, author):
    test = Test.objects.prefetch_related('testuniqueresult_set', 'testcriterion_set').filter(id=test_id, author=author,
                                                                                             status=1)
    if not test.exists():
        raise CustomException(f"Yellow Error: test with id {test_id} and author_id {author.id} wasn't found")
    test = test.last()
    #answers points validation
    unique_results = test.testuniqueresult_set.all()
    criterions_amount = test.testcriterion_set.count()
    points = []
    for unique_result in unique_results:
        points.extend([unique_result.points_min, unique_result.points_max])

    unique_result_points_validation(points, criterions_amount) # validated_results_points

    # results points validation
    validate_test_questions(test=test) # validated_questions
    test.status = 2
    test.save()
    admin_notification(message=f"USER - {author.username}\nWANTS verification confirmation for test [ {test.preview} ]\nwith id {test.id}")

    return test
