"""
URL configuration for prodef project.

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
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import render
from django.conf.urls import handler404, handler500


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)

handler404 = "prodef.urls.custom_404"
handler500 = "prodef.urls.custom_500"


urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"), name='home'),
    path('faq/', TemplateView.as_view(template_name="faq.html"), name='faq'),
    path('404/', TemplateView.as_view(template_name="404.html"), name='404'),
    path('500/', TemplateView.as_view(template_name="500.html"), name='500'),
    path('legal_notice/', TemplateView.as_view(
        template_name="legal_notice.html"), name='legal_notice'),
    path('privacy_policy/', TemplateView.as_view(
        template_name="privacy_policy.html"), name='privacy_policy'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog_posts.urls')),
    path('rewards/', include('rewards.urls')),
    path('tasks/', include('tasks.urls')),
    path('profiles/', include('profiles.urls')),
]
