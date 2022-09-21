from django.urls import path
from . import views
from .__init__ import *

urlpatterns = [
    path(SIGN_UP_URL + '/', views.RegisterView.as_view(), name=SIGN_UP_URL),
    path(LOG_IN_URL + '/', views.LogInView.as_view(), name=LOG_IN_URL),
    path(GET_ME_URL + '/', views.get_user, name=GET_ME_URL),
]