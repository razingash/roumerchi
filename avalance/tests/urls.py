from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .sitemaps import StaticViewSitemap, ProfileViewSitemap, TestViewSitemap, SearchTestsSitemap, StaticRockViewSitemap
from .views import *

sitemaps = {
    'static': StaticViewSitemap,
    'stone': StaticRockViewSitemap,
    'profile': ProfileViewSitemap,
    'test': TestViewSitemap,
    'search-test': SearchTestsSitemap,
}

app_name = 'tests'

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('settings/password/', SettingsPasswordPage.as_view(), name='settings_password'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', RenewedLoginPageView.as_view(), name='password_reset_complete'),
    path('', MainPage.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', RegistrationPageView.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('settings/', SettingsBasePage.as_view(), name='settings'),
    path('search-test/', SearchTestsView.as_view(), name='search_test'),
    path('profile/<uuid:profile_uuid>/', ProfileView.as_view(), name='profile'),
    path('create-test/', CreateTest.as_view(), name='create_test'),
    path('create-questions/', CreateTestQuestions.as_view(), name='create_test_questions'),
    path('test/<slug:test_preview>/', TestView.as_view(), name='test'),
    path('change-test/test/<slug:test_preview>/', ChangeTestInfo.as_view(), name='change_test'),
    path('change-questions/test/<slug:test_preview>/', ChangeTestQuestions.as_view(), name='change_questions'),
]
