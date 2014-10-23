from rest_framework import serializers

from dpn.data.models import Node, Transfer, PROTOCOL_CHOICES, STATE_CHOICES
from dpn.data.models import RegistryEntry, ACTION_CHOICES

class NodeSerializer(serializers.ModelSerializer):
    port_set = serializers.RelatedField(many=True, read_only=True)
    storage_set = serializers.RelatedField(many=True, read_only=True)
    protocols = serializers.SlugRelatedField(many=True, slug_field="name")

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username',)
        read_only_fields = ('id', 'name', 'ssh_username',
                            'pull_from', 'replicate_to')

class TransferSerializer(serializers.ModelSerializer):

    node = serializers.SlugRelatedField(slug_field="name")

    class Meta:
        model = Transfer
        depth = 1
        exclude = ('id', 'error', 'exp_fixity')
        read_only_fields = ('dpn_object_id', 'link', 'size', 'fixity',
                            'event_id', 'action', 'protocol',)

class RegistryEntrySerializer(serializers.ModelSerializer):
    exclude = ('created_on', 'modified_on')
    class Meta:
        model = RegistryEntry
        depth = 1

# class RestoreSerializer(serializers.)