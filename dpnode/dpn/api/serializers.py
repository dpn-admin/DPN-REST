"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from django.utils import timezone
from rest_framework import serializers

from dpn.data.models import Node, ReplicationTransfer, RestoreTransfer
from dpn.data.models import Bag, Fixity, Storage, Protocol


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        exclude = ('id', 'node',)


class FixitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixity
        exclude = ('id', 'bag',)


class NodeSerializer(serializers.ModelSerializer):
    storage = StorageSerializer(source="storage_set", many=True, read_only=True)
    protocols = serializers.SlugRelatedField(
        queryset=Protocol.objects.all(),
        many=True,
        slug_field="name")
    replicate_from = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        read_only=True)
    replicate_to = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        read_only=True)
    restore_from = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        read_only=True)
    restore_to = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        read_only=True)

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id', 'last_pull_date',)
        read_only_fields = ('id', 'name', 'ssh_username',)


class BasicReplicationSerializer(serializers.ModelSerializer):
    from_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    to_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    bag = serializers.SlugRelatedField(
         slug_field="uuid",
         read_only=True)

    class Meta:
        model = ReplicationTransfer
        depth = 2
        exclude = ('id',)
        read_only_fields = ('replication_id', 'from_node', 'to_node', 'bag',
                            'fixity_nonce', 'fixity_accept', 'status',
                            'link', 'protocol', 'created_at', 'updated_at',)


class CreateReplicationSerializer(serializers.ModelSerializer):
    to_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    from_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    bag = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field="uuid")

    class Meta:
        model = ReplicationTransfer
        depth = 1
        fields = ('from_node', 'to_node', 'fixity_algorithm',
                  'fixity_nonce', 'protocol', 'link', 'bag')
        read_only_fields = ('replication_id',)


class BasicRestoreSerializer(serializers.ModelSerializer):
    from_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    to_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    bag = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field="uuid")

    class Meta:
        model = RestoreTransfer
        depth = 2
        exclude = ('id',)
        read_only_fields = ('restore_id', 'from_node', 'to_node', 'bag',
                            'status', 'link', 'protocol', 'created_at',
                            'updated_at',)


class CreateRestoreSerializer(serializers.ModelSerializer):
    to_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    from_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    bag = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field="uuid")

    class Meta:
        model = RestoreTransfer
        depth = 1
        fields = ('from_node', 'to_node', 'bag', 'protocol', 'link')
        read_only_fields = ('restore_id',)


class FixityReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixity
        read_only_fields = ('algorithm', 'digest', 'created_at')
        exclude = ('bag')


class BagSerializer(serializers.ModelSerializer):
    original_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    brightening = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field='uuid',
        many=True,
        required=False)
    rights = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field='uuid',
        many=True,
        required=False)
    replicating_nodes = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field='namespace',
        many=True,
        required=False)
    admin_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field='namespace')
    fixities = FixitySerializer(required=True, many=True)


    class Meta:
        model = Bag
        depth = 1

    # Should we even allow this??
    # Until we specify what can be updated, this allows only
    # some fields to change.
    def update(self, instance, validated_data):
        instance.local_id = validated_data.get('local_id', instance.local_id)
        instance.size = validated_data.get('size', instance.size)
        instance.first_version_uuid = validated_data.get(
            'first_version_uuid', instance.first_version_uuid)
        instance.version = validated_data.get('version', instance.version)
        instance.admin_node = validated_data.get('admin_node', instance.admin_node)
        instance.bag_type = validated_data.get('bag_type', instance.bag_type)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


    def create(self, validated_data):
        fixity_data = validated_data.pop('fixities')
        if fixity_data is None or len(fixity_data) != 1:
            raise serializers.ValidationError("Bag must have exactly one fixity value when created.")
        bag = Bag.objects.create(**validated_data)
        Fixity.objects.create(bag=bag, **fixity_data[0])
        return bag
