from tests.models import CustomUser, Test


def get_profile_info(profile_id):
    return CustomUser.objects.filter(id=profile_id)


#def get_test_info_by_slug(test_slug):
#    return Test.objects.filter(preview_slug=test_slug)


def get_test_info_by_slug(test_slug):
    queryset = Test.objects.prefetch_related('testresult_set', 'testquestion_set', 'testquestion_set__question',
                                             'testquestion_set__questionanswerchoice_set')
    queryset = queryset.filter(preview_slug=test_slug).select_related()
    return queryset



