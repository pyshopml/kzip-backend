
from django.conf.urls import url, include
from rest_framework import routers

from .views import UserCreate, UserDetail

router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^register/$', UserCreate.as_view(), name='register'),
    url(r'^user/(?P<pk>[0-9]+)/$', UserDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]
