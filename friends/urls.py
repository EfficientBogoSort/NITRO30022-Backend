from django.urls import path
from . import views
from .__init__ import *
from rest_framework.routers import SimpleRouter
from .views import FriendViewSet
router = SimpleRouter()
router.register('', FriendViewSet, basename=FRIENDS_URL)

urlpatterns = router.urls

