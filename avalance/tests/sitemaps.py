from django.contrib.sitemaps import Sitemap
from .models import *

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return ['tests:home', 'tests:login', 'tests:registration', 'tests:sitemap']

    def location(self, item):
        return reverse(item)


class StaticRockViewSitemap(Sitemap):
    changefreq = "never"
    priority = 0.0

    def items(self):
        return ['tests:logout', 'tests:settings', 'tests:settings_password', 'tests:create_test', 'tests:create_test_questions',
                'tests:password_reset']

    def location(self, item):
        return reverse(item)



class SearchTestsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self): # kinda overloaded?
        categories = [choice for choice in TestCategories]
        criteria = [choice for choice in CriterionFilters]
        sortings = [choice for choice in SortingFilters]

        combinations = []
        for category in categories:
            for criterion in criteria:
                for sorting in sortings:
                    combinations.append((category, criterion, sorting))

        return combinations

    def location(self, item):
        category, criterion, sorting = item
        url = reverse('tests:search_test')
        url += f'?category={category.name}&criterion={criterion.name}&sorting={sorting.name}'
        return url


class TestViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Test.objects.all().order_by('id')

    def lastmod(self, obj):
        pass


class ProfileViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.4

    def items(self):
        return CustomUser.objects.all().order_by('id')

    def lastmod(self, obj):
        pass

