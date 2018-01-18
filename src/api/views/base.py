from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework import viewsets


class TokenRequiredModelViewSet(viewsets.ModelViewSet):
    """Generic base class all API CBV ViewSets should implement."""

    # authentication and permission config
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # filtering
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)

