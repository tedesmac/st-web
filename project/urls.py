"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, re_path

from st_web import views


urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", views.home),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    re_path(f"^files/(?P<id>[^/]+)/(?P<path>.*)$", views.folder, name="files"),
    re_path(f"^raw/(?P<id>[^/]+)/(?P<path>.*)$", views.raw, name="raw"),
    re_path(
        f"^share/(?P<id>[^/]+)/(?P<path>.*)$", views.ShareView.as_view(), name="share"
    ),
]
