from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from tests.models import TestCriterion, Test, TestStatuses, TestUniqueResult, QuestionAnswerChoice, TestQuestion


class Command(BaseCommand):
    def handle(self, *args, **options):
        custom_user = get_user_model()
        users_to_create = [
            custom_user(username='user1', password='root', email='testmail1@gmail.com'),
            custom_user(username='user2', password='root', email='testmail2@gmail.com'),
            custom_user(username='user3', password='root', email='testmail3@gmail.com'),
            custom_user(username='user4', password='root', email='testmail4@gmail.com'),
            custom_user(username='user5', password='root', email='testmail5@gmail.com'),
        ]
        custom_user.objects.bulk_create(users_to_create, ignore_conflicts=True)

        users = custom_user.objects.all()
        test_description = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit.\n Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien. Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus. Nullam accumsan lorem in dui. Cras ultricies mi eu turpis hendrerit fringilla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; In ac dui quis mi consectetuer lacinia. Nam pretium turpis et arcu. Duis arcu tortor, suscipit eget, imperdiet nec, imperdiet iaculis, ipsum. Sed aliquam ultrices mauris. Integer ante arcu, accumsan a, consectetuer eget, posuere ut, mauris. Praesent adipiscing. Phasellus ullamcorper ipsum rutrum nunc. Nunc nonummy metus. Vestibulum volutpat pretium libero. Cras id dui. Aenean ut eros et nisl sagittis vestibulum. Nullam nulla eros, ultricies sit amet, nonummy id, imperdiet feugiat, pede. Sed lectus. Donec mollis hendrerit risus. Phasellus nec sem in justo pellentesque facilisis. Etiam imperdiet imperdiet orci. Nunc nec neque. Phasellus leo dolor, tempus non, auctor et, hendrerit quis, nisi. Curabitur ligula sapien, tincidunt non, euismod vitae, posuere imperdiet, leo. Maecenas malesuada. Praesent congue erat at massa. Sed cursus turpis vitae tortor. Donec posuere vulputate arcu. Phasellus accumsan cursus velit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed aliquam, nisi quis porttitor congue, elit erat euismod orci, ac placerat dolor lectus quis orci. Phasellus consectetuer vestibulum elit. Aenean tellus metus, bibendum sed, posuere ac, mattis non, nunc. Vestibulum fringilla pede sit amet augue. In turpis. Pellentesque posuere. Praesent turpis. Aenean posuere, tortor sed cursus feugiat, nunc augue blandit nunc, eu sollicitudin urna dolor sagittis lacus. Donec elit libero, sodales nec, volutpat a, suscipit non, turpis. Nullam sagittis. Suspendisse pulvinar, augue ac venenatis condimentum, sem libero volutpat nibh, nec pellentesque velit pede quis nunc. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Fusce id purus. Ut varius tincidunt libero. Phasellus dolor. Maecenas vestibulum mollis"
        counter = 0

        answers_to_create = []
        unique_results_to_create = []

        for i in range(4):
            for k in range(30):
                counter += 1
                test = Test.objects.create(author=users[i], category=(i + 1), status=TestStatuses.VISIBLE,
                                           preview=f"preview for test {counter} by {users[i].username}",
                                           description=f'description for test_{counter}' + test_description,
                                           questions_amount=15)
                criterion1 = TestCriterion.objects.create(test=test, criterion=f'criterion 1 for test {counter}',
                                                          result=f'result 1 for test {counter}')
                criterion2 = TestCriterion.objects.create(test=test, criterion=f'criterion 2 for test {counter}',
                                                          result=f'result 2 for test {counter}')
                unique_results_to_create.extend([
                    TestUniqueResult(test=test, points_min=0, points_max=10,
                                     result=f'result for the case from 0 to 10 for test {counter}'),
                    TestUniqueResult(test=test, points_min=11, points_max=22,
                                     result=f'result for the case from 11 to 22 for test {counter}'),
                    TestUniqueResult(test=test, points_min=23, points_max=32,
                                     result=f'result for the case from 23 to 32 for test {counter}'),
                    TestUniqueResult(test=test, points_min=32, points_max=40,
                                     result=f'result for the case from 32 to 40 for test {counter}')
                ])
                for f in range(15):
                    q = TestQuestion.objects.create(question=f"Question number {f} for test_{counter}", test=test)

                    answers_to_create.extend([
                        QuestionAnswerChoice(question=q, answer=True, weight=1, criterion=criterion1),
                        QuestionAnswerChoice(question=q, answer=False, weight=0, criterion=criterion2)
                    ])

        TestUniqueResult.objects.bulk_create(unique_results_to_create)
        QuestionAnswerChoice.objects.bulk_create(answers_to_create)
