from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

admin.site.register(Test)
admin.site.register(TestCriterion)
admin.site.register(TestUniqueResult)

