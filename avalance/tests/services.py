from django.db import transaction

from tests.models import CustomUser, Test, Respondent, Response, RespondentResult, TestUniqueResult, TestQuestion


def get_profile_info(profile_id):
    return CustomUser.objects.filter(id=profile_id)


def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testresult_set', 'testquestion_set', 'testquestion_set__question',
                                             'testquestion_set__questionanswerchoice_set')
    queryset = queryset.filter(preview_slug=test_slug).select_related()
    return queryset



def calculate_test_result(test_id, answers):
    #TestQuestion.objects.prefetch_related('question', 'questionanswerchoice_set').filter(test_id=1)
    questions = TestQuestion.objects.prefetch_related('question__testquestion_set__questionanswerchoice_set').filter(test_id=test_id)
    if questions.exists():
        k = 0
        points = 0
        true_answers = []
        for question in questions:
            for possible_answer in question.questionanswerchoice_set.all():
                if possible_answer == answers[0]:
                    points += possible_answer.weight
                    k += 1
                    true_answers.append(possible_answer.answer)
        result = TestUniqueResult.objects.filter(test_id=test_id, points_min__lte=points, points_max__gte=points)
        if result.exists():
            return [result[0], true_answers]
    raise Exception('something get wrong')

@transaction.atomic
def create_new_test_respondent(sender_id, test_id, answers):
    sender_id, test_id = int(sender_id), int(test_id)
    print(answers)
    sender_id = 5
    if Test.objects.filter(id=test_id).exists():
        if CustomUser.objects.filter(id=sender_id).exists(): # for logged users
            test_result = calculate_test_result(test_id=test_id, answers=answers)
            result, answers = test_result[0], test_result[1]
            RespondentResult.objects.create(respondent_id=sender_id, result=result)
            Respondent.objects.create(user_id=sender_id, test_id=test_id)
            Response.objects.bulk_create([Response(respondent_id=sender_id, answer=answer) for answer in answers])
            return result.result
        else: # for guests
            pass
    return False
