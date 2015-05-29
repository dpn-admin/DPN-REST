"""
    I can picture in my mind a world without war, a world without hate. And I
    can picture us attacking that world, because they'd never expect it.
        - JACK HANDY
"""
from django.conf import settings

import django_filters
from rest_framework import generics, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import IsAuthenticated

from dpn.api.serializers import BagSerializer, NodeSerializer
from dpn.api.serializers import BasicReplicationSerializer
from dpn.api.serializers import CreateReplicationSerializer
from dpn.api.serializers import BasicRestoreSerializer, CreateRestoreSerializer

from dpn.api.permissions import IsNodeUser, IsBagOwner
from dpn.data.models import Bag, Node, UserProfile
from dpn.data.models import ReplicationTransfer, RestoreTransfer

# Custom View Filters

class BagFilter(django_filters.FilterSet):
    before = django_filters.DateTimeFilter(
        name="updated_at",
        lookup_type='lt',
        # NOTE only works when explicitly set even if default is set.
        # Be sure to include format with no milliseconds, or datetimes
        # without milliseconds will not parse correctly.
        input_formats=[settings.DPN_DATE_FORMAT, "%Y-%m-%dT%H:%M:%SZ"]
    )
    after = django_filters.DateTimeFilter(
        name="updated_at",
        lookup_type='gt',
        input_formats=[settings.DPN_DATE_FORMAT, "%Y-%m-%dT%H:%M:%SZ"]
    )
    admin_node = django_filters.CharFilter(name="admin_node__namespace")

    class Meta:
        model = Bag
        fields = ['before', 'after', 'admin_node', 'bag_type',]


class ReplicationTransferFilterSet(django_filters.FilterSet):
    bag = django_filters.CharFilter(name='bag__uuid')
    to_node = django_filters.CharFilter(name="to_node__namespace")
    from_node = django_filters.CharFilter(name="from_node__namespace")

    class Meta:
        model = ReplicationTransfer
        fields = ["bag", "to_node", "from_node", "status"]


class RestoreTransferFilterSet(django_filters.FilterSet):
    bag = django_filters.CharFilter(name='bag__uuid')
    to_node = django_filters.CharFilter(name="to_node__namespace")

    class Meta:
        model = RestoreTransfer
        fields = ["bag", "to_node", "status"]

# class NodeMemberFilterBackend(filters.BaseFilterBackend):
#     """
#     Filter that only allows users to see transfers for their own node.
#     """
#     def filter_queryset(self, request, queryset, view):
#         if request.user.is_superuser: # Do not apply to superusers
#             return queryset
#         return queryset.filter(node=request.user.profile.node)

# List Views
class BagListView(generics.ListCreateAPIView):
    """
    Returns a paged list of Registry Entries Registry Entries for DPN Objects.

    GET Restricted to authenticated users
    POST Restricted to api_admins
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsBagOwner)
    queryset = Bag.objects.all().order_by('-updated_at')
    serializer_class = BagSerializer
    # NOTE DjangoFilterBackend needs to be set even though it is in default.
    filter_backends = (filters.OrderingFilter, filters.DjangoFilterBackend)
    filter_class = BagFilter
    #ordering_fields = ('updated_at',)


class NodeListView(generics.ListCreateAPIView):
    """
    Returns a paged list of Nodes in the DPN network and their configurations.

    GET restricted to authenticated users.
    POST restricted to api_admins
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)
    queryset = Node.objects.all()
    filter_fields = ('replicate_to', 'replicate_from',)
    serializer_class = NodeSerializer

class ReplicationTransferListView(generics.ListCreateAPIView):
    """
    Returns a paged list of transfers from this node to others.

    GET restricted to authenticated users.

    POST restricted to api_admins.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)

    queryset = ReplicationTransfer.objects.all().order_by('-updated_at')
    filter_backends = (filters.OrderingFilter, filters.DjangoFilterBackend)
    filter_class = ReplicationTransferFilterSet
    #ordering_fields = ('created_on', 'updated_on')

    def get_serializer_class(self):
        try:
            if self.request.user.has_perm('data.add_transfer') \
                    and self.request.method == 'POST':
                return CreateReplicationSerializer
        except AttributeError: # in case no logged in context
            pass
        return BasicReplicationSerializer


class RestoreTransferListView(generics.ListCreateAPIView):
    """
    Returns a paged list of restore requests from this node to others.

    GET restricted to authenticated users.

    POST restricted to api_admins.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)

    queryset = RestoreTransfer.objects.all().order_by('-updated_at')
    filter_backends = (filters.OrderingFilter, filters.DjangoFilterBackend)
    filter_class = RestoreTransferFilterSet
    #ordering_fields = ('updated_at')

    def get_serializer_class(self):
        try:
            if self.request.user.has_perm('data.add_transfer') \
                    and self.request.method == 'POST':
                return CreateRestoreSerializer
        except AttributeError: # in case no logged in context
            pass
        return BasicRestoreSerializer


# Detail Views
class BagDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about an individual bag.

    GET restricted to authenticated users.
    PUT restricted to api_admins
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,IsBagOwner)
    serializer_class = BagSerializer
    model = Bag
    lookup_field = "uuid"
    queryset = Bag.objects.all()


class NodeDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about an individual node.

    GET restricted to authenticated users.
    PUT restricted to api_admins.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)
    model = Node
    serializer_class = NodeSerializer
    lookup_field = "namespace"
    queryset = Node.objects.all()


class ReplicationTransferDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about a specific Transfer.

    GET restricted to authenticated users.

    PUT restricted to api_users belonging to the transfer_to node.
    Superusers have no node restriction.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsNodeUser,)
    lookup_field = "replication_id"
    model = ReplicationTransfer
    serializer_class = BasicReplicationSerializer
    queryset = ReplicationTransfer.objects.all()


class RestoreTransferDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about a specific Restore request.

    GET restricted to authenticated users.

    PUT restricted to api_users belonging to the restore_from node.
    Superusers have no node restriction.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsNodeUser,)
    lookup_field = "restore_id"
    model = RestoreTransfer
    serializer_class = BasicRestoreSerializer
    queryset = RestoreTransfer.objects.all()
