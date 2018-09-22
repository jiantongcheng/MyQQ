"""MyQQ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from useradmin import views as useradmin_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', useradmin_views.login),
    url(r'^register$', useradmin_views.register),
    url(r'register/check_user_name$', useradmin_views.register_check),
    url(r'^logout$', useradmin_views.logout),
    url(r'^login$', useradmin_views.login),
]
