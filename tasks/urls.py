from . import views
from django.urls import path

urlpatterns = [
    path('', views.user_task_overview, name='user_task_overview'),
    path('task_details/<int:task_id>/',
         views.view_task_details,
         name='view_task_details'),
    path('add_task/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/pay/', views.pay_task_fee, name='pay_task_fee'),
    path('tasks/<int:task_id>/pay/success/',
         views.pay_task_fee_success, name='pay_task_fee_success'),
    path("tasks/pay-all/", views.pay_all_fees, name="pay_all_fees"),
    path("tasks/pay-all/success/",
         views.pay_all_fees_success, name="pay_all_fees_success"),
    path('change_plan/', views.change_plan, name='subscription_change'),
    path('cancel_plan/', views.cancel_plan, name='subscription_cancel'),
    path('resume_plan/', views.resume_plan, name='subscription_resume'),
]
