from django.db import transaction
from django import forms
from tests.forms import TestQuestionAnswersForm
from tests.models import CustomUser, Test, Respondent, Response, RespondentResult, TestUniqueResult, TestQuestion, \
    TestCriterion, QuestionAnswerChoice, TestCategories


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
    return CustomUser.objects.only('id').filter(uuid=user_uuid).id

def get_profile_info(profile_uuid):
    return CustomUser.objects.filter(uuid=profile_uuid)

def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testcriterion_set', 'testquestion_set', 'testquestion_set__questionanswerchoice_set')
    queryset = queryset.filter(preview_slug=test_slug)
    return queryset


def get_user_tests(user_id):
    return Test.objects.order_by('-id').filter(author_id=user_id)

def get_user_completed_tests(profile_uuid):
    user_id = CustomUser.objects.only('id').get(uuid=profile_uuid).id
    tests = Respondent.objects.select_related('test').order_by('-id').filter(user_id=user_id)
    return tests

def get_user_created_tests(profile_uuid):
    user_id = CustomUser.objects.only('id').get(uuid=profile_uuid).id
    tests = Test.objects.order_by('-id').filter(author_id=user_id)
    return tests


def get_user_uncompleted_tests():
    pass

@custom_exception(expected_return=None)
def get_filtered_tests(criterion, sorting, category, user_uuid=None): # add a check for emptiness
    if criterion is not None:
        criterion = to_int(criterion)
    if sorting is not None:
        sorting = to_int(sorting)
    if category is not None:
        category = to_int(category)

    if user_uuid is None:
        pass
    elif CustomUser.objects.filter(uuid=user_uuid).exists():
        user_id = get_user_id(user_uuid=user_uuid)
        if criterion is not None: # make flat view for special cases, if the orm queries will be ?very different?
            if sorting is not None:
                if category is not None:
                    pass
                else:
                    pass
            elif category is not None:
                pass
            else:
                if criterion == 1:  # completed
                    tests = [i.test for i in Respondent.objects.select_related('test').order_by('-id').filter(user_id=user_id)]
                elif criterion == 2:  # uncopleted
                    tests = [i.test for i in Respondent.objects.select_related('test').order_by('-id').exclude(user_id=user_id)]
                elif criterion == 3:  # underway
                    pass  # not now
                else:
                    raise custom_exception('change this error')
        elif category is not None:
            if sorting is not None:
                pass
            else:
                pass
        elif sorting is not None:
            pass

    raise custom_exception('something went wrong')


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
                RespondentResult.objects.create(respondent_id=sender_id, result=result)
                Respondent.objects.create(user_id=sender_id, test_id=test_id)
                Response.objects.bulk_create([Response(respondent_id=sender_id, answer=answer) for answer in answers])
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

