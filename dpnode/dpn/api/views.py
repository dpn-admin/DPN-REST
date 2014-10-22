from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions

from dpn.api.serializers import RegistryEntrySerializer, TransferSerializer
from dpn.api.serializers import NodeSerializer
from dpn.data.models import RegistryEntry, Node, Transfer, UserProfile

# List Views
class RegistryListView(generics.ListCreateAPIView):
    """
    Registry Entries for DPN Objects.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    queryset = RegistryEntry.objects.all()
    paginate_by = 20
    serializer_class = RegistryEntrySerializer

class NodeListView(generics.ListCreateAPIView):
    """
    Nodes in the DPN Network.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    queryset = Node.objects.all()
    paginate_by = 20
    serializer_class = NodeSerializer

class TransferListView(generics.ListAPIView):
    """
    Transfer actions between DPN nodes.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)

    queryset = Transfer.objects.none() # as required by model permissions
    paginate_by = 20
    serializer_class = TransferSerializer
    filter_fields = ("action", "status")

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return Transfer.objects.filter(node=profile.node)

# Detail Views
class RegistryDetailView(generics.RetrieveAPIView):
    """
    Registry Entry details.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RegistryEntrySerializer
    model = RegistryEntry
    lookup_field = "dpn_object_id"

class NodeDetailView(generics.RetrieveUpdateAPIView):
    """
    Node details.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    model = Node
    serializer_class = NodeSerializer

class TransferDetailView(generics.RetrieveUpdateAPIView):
    """
    Details about a specific Transfer Action.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    lookup_field = "event_id"
    model = Transfer
    serializer_class = TransferSerializer

# # services views
# class RestoreView(generics.APIView):
#     pass