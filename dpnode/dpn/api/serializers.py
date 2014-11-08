"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from rest_framework import serializers

from dpn.data.models import Node, Transfer, RegistryEntry

class NodeSerializer(serializers.ModelSerializer):

    port_set = serializers.RelatedField(many=True, read_only=True)
    storage_set = serializers.RelatedField(many=True, read_only=True)
    protocols = serializers.SlugRelatedField(many=True, slug_field="name")

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id')
        read_only_fields = ('id', 'name', 'ssh_username',
                            'replicate_from', 'replicate_to',
                            'restore_from', 'restore_to', 'me')

class TransferSerializer(serializers.ModelSerializer):

    node = serializers.SlugRelatedField(slug_field="name")
    dpn_object_id = serializers.SerializerMethodField('get_dpn_object_id')

    class Meta:
        model = Transfer
        depth = 2
        exclude = ('id', 'error', 'exp_fixity', 'registry_entry')
        read_only_fields = ('link', 'size', 'fixity',
                            'event_id', 'protocol',)

    def get_dpn_object_id(self, obj):
        return obj.registry_entry.dpn_object_id


class RegistryEntrySerializer(serializers.ModelSerializer):

    exclude = ('created_on', 'updated_on', 'published')
    first_node = serializers.SlugRelatedField(slug_field="namespace")

    class Meta:
        model = RegistryEntry
        depth = 1
