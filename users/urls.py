from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.RegisterView.as_view()),
    path('login/', views.LogInView.as_view()),
    path('getMe/', views.get_user),
]