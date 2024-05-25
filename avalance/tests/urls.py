from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegistrationPageView.as_view(), name='registration'),# join login and registration?
    path('logout/', logout_user, name='logout'),
    path('settings/', SettingsBasePage.as_view(), name='settings'),
    path('settings/password/', SettingsPasswordPage.as_view(), name='settings_password'),
    path('profile/<uuid:profile_uuid>/', ProfileView.as_view(), name='profile'),
    path('search-test/', SearchTestsView.as_view(), name='search_test'),
    path('create-test/', CreateTest.as_view(), name='create_test'),
    path('create-questions/', CreateTestQuestions.as_view(), name='create_test_questions'),
    path('test/<slug:test_preview>/', TestView.as_view(), name='test'),
    path('change-test/test/<slug:test_preview>/', ChangeTestInfo.as_view(), name='change_test'),
    path('change-questions/test/<slug:test_preview>/', ChangeTestQuestions.as_view(), name='change_questions'),
]
