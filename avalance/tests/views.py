import json

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from tests.models import CustomUser, Test
from tests.services import get_profile_info, get_test_info_by_slug
from tests.utils import DataMixin


# Create your views here.

class ProfileView(DetailView, DataMixin):
    model = CustomUser
    template_name = 'tests\profile.html'
    context_object_name = 'user'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('profile_id')

        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('profile_id')
        queryset = get_profile_info(profile_id=profile_id)
        return get_object_or_404(queryset)


class SearchTestsView(DataMixin, ListView):
    model = Test
    ordering = ['-id']
    template_name = 'tests/search_test.html'
    context_object_name = 'tests'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='tests', user_id=self.request.user.id)
        else:
            mix = self.get_user_context(title='tests')
        return context | mix

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class TestView(DetailView, DataMixin):
    model = Test
    template_name = 'tests/test.html'
    context_object_name = 'test'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = context.get('test').id
        if self.request.user.is_authenticated:
            mix = self.get_user_context(title='Profile')
        else:
            mix = self.get_user_context(title='Profile')
        return context | mix

    def get_object(self, queryset=None):
        test_slug = self.kwargs.get('test_preview')
        queryset = get_test_info_by_slug(test_slug=test_slug)
        return get_object_or_404(queryset)

