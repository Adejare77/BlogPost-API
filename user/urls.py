from django.urls import path
from user import views

urlpatterns = [
    path('', views.get_users, name='all_users'),
    path('<uuid:user_id>/', views.get_user_by_id, name='user_profile'),
    path('<uuid:user_id>/disable/', views.disable_user_account, name='disable_account'),
    path('<uuid:user_id>/enable/', views.enable_user_account, name='enable_account'),
]
