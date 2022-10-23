from rest_framework.routers import SimpleRouter
from .views import FileViewset
from .__init__ import *

router = SimpleRouter()
router.register('', FileViewset, basename=FILES_URL)
urlpatterns = router.urls