from django.db import transaction

from tests.models import CustomUser, Test, Respondent, Response, RespondentResult, TestUniqueResult, TestQuestion, \
    TestCriterion


class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)

def custom_exception(func: callable):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except CustomException as e:
            return Response({"error": f"{e}"}, status=400)
    return wrapper


def get_profile_info(profile_uuid):
    return CustomUser.objects.filter(uuid=profile_uuid)


def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testcriterion_set', 'testquestion_set', 'testquestion_set__question',
                                             'testquestion_set__questionanswerchoice_set')
    queryset = queryset.filter(preview_slug=test_slug).select_related()
    return queryset


def get_user_tests(user_id):
    return Test.objects.order_by('-id').filter(author_id=user_id)

def get_user_completed_tests(user_id):
    tests = Respondent.objects.select_related('test').order_by('-id').filter(user_id=user_id)
    return tests

def get_user_uncompleted_tests():
    pass


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

