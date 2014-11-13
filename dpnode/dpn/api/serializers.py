"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from rest_framework import serializers
from django.conf import settings

from dpn.data.models import Node, Transfer, RegistryEntry, PENDING, ACCEPT, \
    REJECT


class NodeSerializer(serializers.ModelSerializer):
    help = "List of important IP numbers and ports that need access."
    port_set = serializers.RelatedField(many=True, read_only=True,
                                        help_text=help)
    help = "list of storage locations and descriptions used by node."
    storage_set = serializers.RelatedField(many=True, read_only=True,
                                           help_text=help)
    help = "List of transfer protocols this node supports."
    protocols = serializers.SlugRelatedField(many=True, slug_field="name",
                                             help_text=help)

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id')
        read_only_fields = ('id', 'name', 'ssh_username',
                            'replicate_from', 'replicate_to',
                            'restore_from', 'restore_to', 'me')


class BasicTransferSerializer(serializers.ModelSerializer):
    node = serializers.SlugRelatedField(source="node", slug_field="namespace",
                                        read_only=True)
    dpn_object_id = serializers.SlugRelatedField(source="registry_entry",
                                                 slug_field="dpn_object_id",
                                                 read_only=True)
    status = serializers.ChoiceField(choices=(
        (PENDING, "Pending"),
        (ACCEPT, "Accept"),
        (REJECT, "Reject")
    ))

    class Meta:
        model = Transfer
        depth = 1
        exclude = ('id', 'error', 'exp_fixity', 'registry_entry')
        read_only_fields = ('link', 'size', 'fixity', 'event_id', 'protocol',
                            "created_on", "updated_on", "valid")


class CreateTransferSerializer(serializers.ModelSerializer):
    node = serializers.SlugRelatedField(slug_field="namespace")
    dpn_object_id = serializers.SlugRelatedField(source="registry_entry",
                                                 slug_field="dpn_object_id")

    class Meta:
        model = Transfer
        depth = 1
        fields = ('node', 'dpn_object_id', 'exp_fixity', 'size', 'link')
        read_only_fields = ('event_id',)


class RegistryEntrySerializer(serializers.ModelSerializer):
    exclude = ('created_on', 'updated_on', 'published')
    first_node = serializers.SlugRelatedField(slug_field="namespace")
    last_fixity_date = serializers.DateTimeField(
        format=settings.DPN_DATE_FORMAT)
    brightening_objects = serializers.SlugRelatedField(
        slug_field='dpn_object_id', many=True, required=False)
    rights_objects = serializers.SlugRelatedField(slug_field='dpn_object_id',
                                                  many=True, required=False)
    replicating_nodes = serializers.SlugRelatedField(slug_field='namespace',
                                                     many=True, required=False)

    class Meta:
        model = RegistryEntry
        depth = 1
        exclude = ('created_on', 'updated_on', 'published')