from django.urls import path
from . import views
from .__init__ import *
from rest_framework.routers import SimpleRouter
from .views import CollectionViewSet
router = SimpleRouter()
router.register('', CollectionViewSet, basename=COLLECTION_URL)

urlpatterns = router.urls

