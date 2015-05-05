"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from django.utils import timezone
from rest_framework import serializers

from dpn.data.models import Node, ReplicationTransfer, RestoreTransfer
from dpn.data.models import Bag, Fixity, Storage, Protocol, FixityAlgorithm


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        exclude = ('id', 'node',)


class FixitySerializer(serializers.ModelSerializer):

    sha256 = serializers.CharField(source='digest', required=True)

    class Meta:
        model = Fixity
        fields = ('sha256',)

    # Django REST framework doesn't like this kind of serialization,
    # so we have to do some tricks to make it work.
    def create(self, validated_data):
        data = {}
        data['digest'] = validated_data.pop('sha256')
        data['algorithm'] = FixityAlgorithm.objects.filter(name='sha256').first()
        return Fixity.objects.create(**data)

    def update(self, instance, validated_data):
        instance.digest = validated_data.pop('sha256')
        instance.algorithm = Fixity.Algorithm.objects.filter(name='sha256').first()
        instance.save()
        return instance


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
    fixity_algorithms = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        read_only=True)

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id', 'last_pull_date',)
        read_only_fields = ('id', 'name', 'ssh_username',)

class BagUuidField(serializers.Field):
    def to_representation(self, obj):
        return obj.bag.uuid

    def to_internal_value(self, data):
        return Bag.objects.filter(uuid=data).first()

    def get_attribute(self, data):
        return data

class BasicReplicationSerializer(serializers.ModelSerializer):
    from_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    to_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    uuid = serializers.CharField(source='bag.uuid', required=False)
    fixity_algorithm = serializers.CharField(source='fixity_algorithm.name', required=False)

    class Meta:
        model = ReplicationTransfer
        depth = 2
        exclude = ('id', 'bag',)
        read_only_fields = ('replication_id', 'from_node', 'to_node', 'uuid',
                            'fixity_nonce', 'fixity_accept', 'status',
                            'link', 'protocol', 'created_at', 'updated_at',)


class CreateReplicationSerializer(serializers.ModelSerializer):
    to_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    from_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    uuid = BagUuidField()
    fixity_algorithm = serializers.SlugRelatedField(
        queryset=FixityAlgorithm.objects.all(),
        slug_field="name")

    class Meta:
        model = ReplicationTransfer
        depth = 1
        fields = ('from_node', 'to_node', 'fixity_algorithm',
                  'fixity_nonce', 'protocol', 'link', 'uuid',)
        read_only_fields = ('replication_id',)

    def create(self, validated_data):
        validated_data['bag'] = validated_data.pop('uuid')
        return ReplicationTransfer.objects.create(**validated_data)


class BasicRestoreSerializer(serializers.ModelSerializer):
    from_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    to_node = serializers.SlugRelatedField(
        slug_field="namespace",
        read_only=True)
    uuid = serializers.CharField(source='bag.uuid')

    class Meta:
        model = RestoreTransfer
        depth = 2
        exclude = ('id', 'bag')
        read_only_fields = ('restore_id', 'from_node', 'to_node', 'uuid',
                            'status', 'link', 'protocol', 'created_at',
                            'updated_at',)


class CreateRestoreSerializer(serializers.ModelSerializer):
    to_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    from_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    uuid = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field="uuid")

    class Meta:
        model = RestoreTransfer
        depth = 1
        fields = ('from_node', 'to_node', 'uuid', 'protocol', 'link')
        read_only_fields = ('restore_id',)


class FixityReadOnlySerializer(serializers.ModelSerializer):
    algorithm = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True)

    class Meta:
        model = Fixity
        read_only_fields = ('algorithm', 'digest', 'created_at')
        exclude = ('bag')


class BagSerializer(serializers.ModelSerializer):
    ingest_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    interpretive = serializers.SlugRelatedField(
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
        fixities = validated_data.pop('fixities')
        if fixities is None or len(fixities) != 1:
            raise serializers.ValidationError("Bag must have exactly one fixity value when created.")
        bag = Bag.objects.create(**validated_data)
        fixity_data = {}
        # Digest *should* be in the 'sha256' key, but when running tests,
        # we create key 'sha256' and we receive key 'digest'. Not sure
        # WTF is up with that.
        if 'digest' in fixities[0]:
            fixity_data['digest'] = fixities[0].pop('digest')
        if 'sha256' in fixities[0]:
            fixity_data['digest'] = fixities[0].pop('sha256')
        fixity_data['algorithm'] = FixityAlgorithm.objects.filter(name='sha256').first()
        Fixity.objects.create(bag=bag, **fixity_data)
        return bag
