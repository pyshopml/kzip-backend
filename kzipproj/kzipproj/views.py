from collections import OrderedDict

from django.urls import NoReverseMatch
from django.core.urlresolvers import RegexURLResolver
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ApiRoot(APIView):
    """
    Returns all registered API endpoints.
    """
    permission_classes = (AllowAny,)
    urlpatterns = None
    app_namespace = None

    def get(self, request, format=None):
        assert self.urlpatterns is not None, "Provide urlpatterns argument if you want to use this view!"
        assert self.app_namespace is not None, "Provide app_namespace argument if you want to use this view!"

        def api_url(namespace, name):
            try:
                return reverse('%s:%s' % (namespace, name), request=request, format=format)
            except NoReverseMatch:
                return None

        def parse_urlpatterns(urlpatterns, namespace):
            data = OrderedDict()

            for urlpattern in urlpatterns:
                if urlpattern == 'api_root':
                    continue

                if isinstance(urlpattern, RegexURLResolver):
                    data[urlpattern.namespace] = parse_urlpatterns(urlpattern.url_patterns, urlpattern.namespace)
                else:
                    data[urlpattern.name] = api_url(namespace, urlpattern.name)

            return data

        data = parse_urlpatterns(self.urlpatterns, self.app_namespace)

        return Response(data)
