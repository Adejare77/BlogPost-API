from django.urls import path
from core.authentication import views

urlpatterns = [
    path('login/', views.EmailTokenObtainPairView.as_view(), name='login'),
    path('register/', views.register_view, name='sign-up'),
    path('logout/', views.logout_view, name='logout')
]
