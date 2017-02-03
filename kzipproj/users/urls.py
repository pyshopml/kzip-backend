from django.conf.urls import url, include
# from rest_framework import routers
from rest_framework import routers

from .views import *

urlpatterns = [
    url(r'^account/register/$', UserCreate.as_view(), name='register'),
    url(r'^account/activate/$', ActivationView.as_view(), name='activation'),
    url(r'^password/reset/$', PasswordReset.as_view(), name='password_reset'),
    url(r'^password/reset/confirm/$',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # url(r'^user/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

router = routers.DefaultRouter()
router.register(r'users', UserDetail)
urlpatterns += router.urls
