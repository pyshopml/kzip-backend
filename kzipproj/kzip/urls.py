from django.conf.urls import url, include
from rest_framework import routers
from . import views

pub_router = routers.DefaultRouter()
pub_router.register(r'publications', views.PublicationViewSet)
urlpatterns = pub_router.urls

# urlpatterns = [
#     url(r'^', include(pub_router.urls, namespace='kzip')),
# ]


