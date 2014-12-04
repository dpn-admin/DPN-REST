"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from rest_framework import serializers
from django.conf import settings

from dpn.data.models import Node, Transfer, RegistryEntry, PENDING, ACCEPT
from dpn.data.models import Port, Storage, REJECT, Protocol

# Custom Field Serializers
# class RegistryIDField(serializers.RelatedField):
#      def to_representation(self, value):
#         return value.dpn_object_id
#
#      def to_internal_value(self, data):
#

# Model Serializers
class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        exclude = ('id', 'node')

class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        exclude = ('id', 'node')

class NodeSerializer(serializers.ModelSerializer):
    storage = StorageSerializer(source="storage_set", many=True, read_only=True)
    protocols = serializers.SlugRelatedField(
        queryset=Protocol.objects.all(),
        many=True,
        slug_field="name")

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id', 'last_pull_date')
        read_only_fields = ('id', 'name', 'ssh_username',
                            'replicate_from', 'replicate_to',
                            'restore_from', 'restore_to', 'me')


class BasicTransferSerializer(serializers.ModelSerializer):
    node = serializers.SlugRelatedField(slug_field="namespace", read_only=True)
    dpn_object_id = serializers.SlugRelatedField(
                                    source="registry_entry",
                                    slug_field="dpn_object_id",
                                    read_only=True)

    class Meta:
        model = Transfer
        depth = 2
        exclude = ('id', 'error', 'exp_fixity', 'registry_entry')
        read_only_fields = ('link', 'size', 'fixity', 'event_id', 'protocol',
                            "created_on", "updated_on", "valid", "fixity_type")


class CreateTransferSerializer(serializers.ModelSerializer):
    node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    dpn_object_id = serializers.SlugRelatedField(
        queryset=RegistryEntry.objects.all(),
        source="registry_entry",
        slug_field="dpn_object_id")

    class Meta:
        model = Transfer
        depth = 1
        fields = ('node', 'dpn_object_id', 'exp_fixity',
                  'size', 'link')
        read_only_fields = ('event_id',)


class RegistryEntrySerializer(serializers.ModelSerializer):
    first_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    brightening_objects = serializers.SlugRelatedField(
        queryset=RegistryEntry.objects.all(),
        slug_field='dpn_object_id',
        many=True,
        required=False)
    rights_objects = serializers.SlugRelatedField(
        queryset=RegistryEntry.objects.all(),
        slug_field='dpn_object_id',
        many=True,
        required=False)
    replicating_nodes = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field='namespace',
        many=True,
        required=False)

    class Meta:
        model = RegistryEntry
        depth = 1
        exclude = ('created_on', 'updated_on',)