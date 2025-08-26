from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.view_user_profile, name='view_user_profile'),
    path('account/update/', views.account_update, name='account_update'),
    path("password/change/",
         auth_views.PasswordChangeView.as_view(
            template_name="account/password_change.html",
            success_url="/password/change/done/"), name="password_change"),
    path("password/change/done/",
         auth_views.PasswordChangeDoneView.as_view(
             template_name="account/password_change_done.html"),
         name="password_change_done"),
]
