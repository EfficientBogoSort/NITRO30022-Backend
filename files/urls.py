from rest_framework.routers import SimpleRouter
from .views import FileViewset

router = SimpleRouter()
router.register('accounts', FileViewset)
urlpatterns = router.urls