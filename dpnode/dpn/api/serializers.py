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
                            'pull_from', 'replicate_to')

class TransferSerializer(serializers.ModelSerializer):

    node = serializers.SlugRelatedField(slug_field="name")

    class Meta:
        model = Transfer
        depth = 1
        exclude = ('id', 'error', 'exp_fixity')
        read_only_fields = ('dpn_object_id', 'link', 'size', 'fixity',
                            'event_id', 'protocol',)

class RegistryEntrySerializer(serializers.ModelSerializer):

    exclude = ('created_on', 'updated_on', 'published')
    first_node = serializers.SlugRelatedField(slug_field="namespace")

    class Meta:
        model = RegistryEntry
        depth = 1
