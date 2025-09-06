from . import views
from django.urls import path

urlpatterns = [
     path('', views.user_task_overview, name='user_task_overview'),
     path('task_details/<int:task_id>/',
          views.view_task_details,
          name='view_task_details'),
     path('add_task/', views.add_task, name='add_task'),
     path("<int:task_id>/delete/", views.delete_task, name="delete_task"),
     path('<int:task_id>/pay/', views.pay_task_fee, name='pay_task_fee'),
     path('<int:task_id>/pay/success/',
          views.pay_task_fee_success, name='pay_task_fee_success'),
     path("pay-all/", views.pay_all_fees, name="pay_all_fees"),
     path("pay-all/success/",
          views.pay_all_fees_success, name="pay_all_fees_success"),

]
