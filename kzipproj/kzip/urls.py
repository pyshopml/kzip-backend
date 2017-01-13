from django.conf.urls import url, include
from rest_framework import routers
from . import views

pub_router = routers.DefaultRouter()
pub_router.register(r'publications', views.PublicationViewSet)

urlpatterns = [
    url(r'^', include(pub_router.urls)),
]


