from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegistrationPageView.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('profile/<uuid:profile_uuid>/', ProfileView.as_view(), name='profile'),
    path('search_test/', SearchTestsView.as_view(), name='search_test'),
    path('test/<slug:test_preview>/', TestView.as_view(), name='test'),
    path('create_test/', CreateTest.as_view(), name='new_test')
]
