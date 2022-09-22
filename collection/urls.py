from django.urls import path
from . import views
from .__init__ import *

urlpatterns = [
    path('', views.new_collection),
]