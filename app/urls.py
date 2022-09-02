from django.urls import path
from . import views

urlpatterns = [    
    path('collection/', views.collections),
    path('collection/<int:id>', views.collection),
]