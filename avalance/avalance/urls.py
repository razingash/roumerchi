"""
URL configuration for avalance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from avalance.settings import base
from tests.views import page_forbidden_error

handler403 = page_forbidden_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('roumerchi/', include('tests.urls', namespace='tests'))
]

if base.IS_IN_PRODUCTION:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
else:
    from django.views.static import serve as mediaserve
    urlpatterns += [
        re_path(f'^{base.STATIC_URL.lstrip("/")}(?P<path>.*)$', mediaserve, {'document_root': base.STATIC_ROOT}),
    ]
