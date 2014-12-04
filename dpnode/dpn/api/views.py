"""
    I can picture in my mind a world without war, a world without hate. And I
    can picture us attacking that world, because they'd never expect it.
        - JACK HANDY
"""

import django_filters
from rest_framework import generics, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import IsAuthenticated

from dpn.api.serializers import RegistryEntrySerializer, BasicTransferSerializer
from dpn.api.serializers import NodeSerializer, CreateTransferSerializer
from dpn.api.permissions import IsNodeUser
from dpn.data.models import RegistryEntry, Node, Transfer, UserProfile

# Custom View Filters

class RegistryFilter(django_filters.FilterSet):
    before = django_filters.DateTimeFilter(
        name="last_modified_date",
        lookup_type='lt'
    )
    after = django_filters.DateTimeFilter(
        name="last_modified_date",
        lookup_type='gt'
    )
    first_node = django_filters.CharFilter(name="first_node__namespace")
    class Meta:
        model = RegistryEntry
        fields = ['before', 'after', 'first_node', 'object_type']

class TransferFilterSet(django_filters.FilterSet):
    dpn_object_id = django_filters.CharFilter(
        name='registry_entry__dpn_object_id'
    )
    node = django_filters.CharFilter(name="node__namespace")
    class Meta:
        model = Transfer
        fields = ["dpn_object_id", "status", "fixity", "valid", "node"]

class NodeMemberFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see transfers for their own node.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser: # Do not apply to superusers
            return queryset
        return queryset.filter(node=request.user.profile.node)

# List Views
class RegistryListView(generics.ListCreateAPIView):
    """
    Returns a paged list of Registry Entries Registry Entries for DPN Objects.

    GET Restricted to authenticated users
    POST Restricted to api_admins
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)
    queryset = RegistryEntry.objects.all()
    serializer_class = RegistryEntrySerializer
    filter_class = RegistryFilter
    ordering_fields = ('last_modified_date')

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

class TransferListView(generics.ListCreateAPIView):
    """
    Returns a paged list of transfers from this node to others.

    GET restricted to authenticated users with transfer list automatically
    filtered to the users node. Superusers have no filter applied.

    POST restricted to api_admins.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)

    queryset = Transfer.objects.all()
    filter_backends = (NodeMemberFilterBackend, filters.OrderingFilter,
                       filters.DjangoFilterBackend)
    filter_class = TransferFilterSet
    ordering_fields = ('created_on', 'updated_on')

    def get_serializer_class(self):
        try:
            if self.request.user.has_perm('data.add_transfer') \
                    and self.request.method == 'POST':
                return CreateTransferSerializer
        except AttributeError: # in case no logged in context
            pass
        return BasicTransferSerializer

# Detail Views
class RegistryDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about an individual registry entry.

    GET restricted to authenticated users.
    PUT restricted to api_admins
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions,)
    serializer_class = RegistryEntrySerializer
    model = RegistryEntry
    lookup_field = "dpn_object_id"
    queryset = RegistryEntry.objects.all()


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

class TransferDetailView(generics.RetrieveUpdateAPIView):
    """
    Returns details about a specific Transfer.

    GET restricted to authenticated users belonging to the same node as the
     Transfer.  Superusers can see all Transfers.

    PUT restricted to api_users belonging to the transfer node.  Superusers have
    no node restriction.

    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions, IsNodeUser)
    lookup_field = "event_id"
    model = Transfer
    serializer_class = BasicTransferSerializer
    queryset = Transfer.objects.all()