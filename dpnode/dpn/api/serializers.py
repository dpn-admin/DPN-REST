"""
    Yeah, well, that's just, like, your opinion, man.

            - The Dude
"""
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from dpn.data.models import Node, ReplicationTransfer, RestoreTransfer
from dpn.data.models import Bag, Fixity, Storage, Protocol, FixityAlgorithm, Node
from dpn.api.permissions import user_is_superuser


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        exclude = ('id', 'node',)


# Original design was to support multiple fixities on a bag.
# One at ingest, then one each time we do a scheduled fixity check.
# So the fixities property was a list. That's changed. Now it's
# a hash in which key is the name of the digest algorithm, and value
# is the actual digest. This is not quite how it's modeled in the
# database, so we have a custom serializer.
class FixitySerializer(serializers.ModelSerializer):

    # We have to specify first.digest instead of just digest,
    # because we're serializing a relation, not a property.
    # This actually calles first().digest. And yes, that means
    # we serialize only the first digest value. While the underlying
    # DB schema supports multiple digests, the assumption at launch
    # is that will only ever be one per bag.
    #
    # Another problem here is that when we run Django tests, we
    # get an error saying the sha256 field is missing even when
    # we supply. This problem doesn't affect real-world requests,
    # only requests coming from the Django tests. So we have
    # required=False, even though it should be true. The bag
    # serializer's custom create method enforces the sha256
    # requirement.
    #
    # All of this trouble stems from the JSON serialization
    # requirements straying too far from the DB schema.
    sha256 = serializers.CharField(source='first.digest', required=False)

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


# Local admin is the only user who can update a node
# through the API, and even then, he can update only
# the last_pull_date. All other updated must be done
# through the admin UI.
class NodeSerializer(serializers.ModelSerializer):
    storage = StorageSerializer(source="storage_set", many=True, read_only=True)
    protocols = serializers.SlugRelatedField(
        queryset=Protocol.objects.all(),
        many=True,
        required=False,
        slug_field="name")
    replicate_from = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        required=False,
        read_only=True)
    replicate_to = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        required=False,
        read_only=True)
    restore_from = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        required=False,
        read_only=True)
    restore_to = serializers.SlugRelatedField(
        slug_field="namespace",
        many=True,
        required=False,
        read_only=True)
    fixity_algorithms = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        required=False,
        read_only=True)

    class Meta:
        model = Node
        depth = 1
        exclude = ('ssh_username', 'id',)
        read_only_fields = ('id', 'name', 'ssh_username', 'storage',
                            'protocols', 'replicate_to', 'replicate_from',
                            'restore_to', 'restore_from', 'fixity_algorithms',)

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
                            'fixity_nonce', 'fixity_accept',
                            'link', 'protocol', 'created_at', 'updated_at',)

    # We have a custom update method because some ignorant clients
    # (including our own) may send JSON that includes related fields like
    # the fixity algorithm. Django Rest Framework will blow up on this
    # because it does not handle nested updated by default. In any case,
    # clients should only ever be allowed to update status, bag_valid and
    # fixity_value. If they send us any other data, we throw it out.
    def update(self, instance, validated_data):
        was_already_confirmed = instance.status == "Confirmed"
        instance.status = validated_data.get('status', instance.status)
        instance.bag_valid = validated_data.get('bag_valid', instance.bag_valid)
        instance.fixity_value = validated_data.get('fixity_value', instance.fixity_value)
        if instance.updated_at > validated_data.get('updated_at', instance.updated_at):
            return ValidationError(detail="The updated_at timestamp on the object you submitted is earlier than this system's timestamp for the same object. Your record is out of date and this system will not update the record.")
        if instance.status.lower() == "confirmed" and not was_already_confirmed and not user_is_superuser(self.context):
            raise PermissionDenied("Only the local admin can set replication status to 'Confirmed'")
        if instance.status.lower() == "stored" and not instance.fixity_accept:
            raise PermissionDenied("You cannot mark a bag as stored if this server did not previously confirm its fixity value.")
        instance.save()
        return instance


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
                  'fixity_nonce', 'protocol', 'link', 'uuid',
                  'replication_id', 'created_at', 'updated_at',
                  'status', 'replication_id',)

    def create(self, validated_data):
        if not user_is_superuser(self.context):
            raise PermissionDenied("Only the admin user can create replication requests on this node.")
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
        fields = ('restore_id', 'from_node', 'to_node', 'uuid',
                  'status', 'link', 'protocol', 'created_at',
                  'updated_at',)
        read_only_fields = ('restore_id', 'from_node', 'to_node', 'uuid',
                            'created_at', 'updated_at',)

    # Users can update only these three fields on the restoration request.
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.protocol = validated_data.get('protocol', instance.protocol)
        instance.link = validated_data.get('link', instance.link)
        if instance.updated_at > validated_data.get('updated_at', instance.updated_at):
            return ValidationError(detail="The updated_at timestamp on the object you submitted is earlier than this system's timestamp for the same object. Your record is out of date and this system will not update the record.")
        if instance.status.lower() == "finished" and not user_is_superuser(self.context):
            raise PermissionDenied("Only the local admin can set replication status to 'Finished'")
        instance.save()
        return instance


class CreateRestoreSerializer(serializers.ModelSerializer):
    to_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    from_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace")
    uuid = BagUuidField()

    class Meta:
        model = RestoreTransfer
        depth = 1
        fields = ('from_node', 'to_node', 'uuid', 'protocol',
                  'link', 'status', 'restore_id', 'created_at',
                  'updated_at',)
        read_only_fields = ('restore_id', 'created_at', 'updated_at',)

    def create(self, validated_data):
        if 'uuid' in validated_data:
            validated_data['bag'] = validated_data.pop('uuid')
        if not user_is_superuser(self.context):
            raise PermissionDenied("Only the admin user can create restore requests on this node.")
        return RestoreTransfer.objects.create(**validated_data)


class BagSerializer(serializers.ModelSerializer):
    ingest_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field="namespace",
        allow_null=True)
    interpretive = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field='uuid',
        many=True,
        required=False,
        allow_null=True)
    rights = serializers.SlugRelatedField(
        queryset=Bag.objects.all(),
        slug_field='uuid',
        many=True,
        required=False,
        allow_null=True)
    replicating_nodes = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field='namespace',
        many=True,
        required=False,
        allow_null=True)
    admin_node = serializers.SlugRelatedField(
        queryset=Node.objects.all(),
        slug_field='namespace',
        allow_null=True)
    fixities = FixitySerializer(required=True, many=False)


    class Meta:
        model = Bag
        depth = 1

    def _extract_relations(self, validated_data):
        fixities = None
        rights = None
        interpretive = None
        replicating_nodes = None
        if 'rights' in validated_data:
            rights = validated_data.pop('rights')
        if 'interpretive' in validated_data:
            interpretive = validated_data.pop('interpretive')
        if 'fixities' in validated_data:
            fixities = validated_data.pop('fixities')
            if 'first' in fixities:
                fixities = fixities['first']
        if 'replicating_nodes' in validated_data:
            replicating_nodes = validated_data.pop('replicating_nodes')
        return fixities, rights, interpretive, replicating_nodes

    def _assign_relations(self, bag, rights, interpretive, replicating_nodes):
        if rights:
            for rights_uuid in rights:
                rights_bag = Bag.objects.filter(uuid=rights_uuid).first()
                if rights_bag is None:
                    raise ObjectDoesNotExist("Rights bag {0} does not exist".format(rights_uuid))
                if not rights_bag in bag.rights.all():
                    bag.rights.add(rights_bag)

        if interpretive:
            for interpretive_uuid in interpretive:
                interpretive_bag = Bag.objects.filter(uuid=interpretive_uuid).first()
                if interpretive_bag is None:
                    raise ObjectDoesNotExist("Interpretive bag {0} does not exist".format(interpretive_uuid))
                if not interpretive_bag in bag.interpretive.all():
                    bag.interpretive.add(interpretive_bag)

        if replicating_nodes:
            for node_namespace in replicating_nodes:
                replicating_node = Node.objects.filter(namespace=node_namespace).first()
                if replicating_node is None:
                    raise ObjectDoesNotExist("Replicating node {0} does not exist".format(node_namespace))
                if not replicating_node in bag.replicating_nodes.all():
                    bag.replicating_nodes.add(replicating_node)


    # Update should not change uuid, local_id, version, ingest_node, etc.
    # Only the items set below may change.
    def update(self, instance, validated_data):
        # Someday, we'll allow changing admin_node... but not yet.
        # That should only happen if one node permanently drops out of DPN.
        # instance.admin_node = validated_data.get('admin_node', instance.admin_node)
        fixities, rights, interpretive, replicating_nodes = self._extract_relations(validated_data)
        self._assign_relations(instance, rights, interpretive, replicating_nodes)
        if instance.updated_at > validated_data.get('updated_at', instance.updated_at):
            return ValidationError(detail="The updated_at timestamp on the object you submitted is earlier than this system's timestamp for the same object. Your record is out of date and this system will not update the record.")
        instance.updated_at = timezone.now()
        instance.save()
        return instance

    def create(self, validated_data):
        # Assigning many-to-many relations in constructor is a problem,
        # so we create the bag first, then assign the relations.
        # http://bit.ly/1RcvTzZ
        fixities, rights, interpretive, replicating_nodes = self._extract_relations(validated_data)
        if fixities is None or len(fixities) == 0:
            raise serializers.ValidationError("Bag must have exactly one sha256 fixity value when created.")

        # Create the bag, then add the many-to-many relations
        bag = Bag.objects.create(**validated_data)
        self._assign_relations(bag, rights, interpretive, replicating_nodes)

        fixity_data = {}
        # Digest *should* be in the 'sha256' key, but when running tests,
        # we create key 'sha256' and we receive key 'digest'. Not sure
        # WTF is up with that.
        #
        # Also, this wonky nested dict, where the 'digest' or 'sha256' key
        # is inside the entry for 'first' is a side effect of the wierd
        # tricks we had to perform in the FixitySerializer to get it to
        # serialize a list as a hash.
        if 'digest' in fixities:
            fixity_data['digest'] = fixities.pop('digest')
        if 'sha256' in fixities:
            fixity_data['digest'] = fixities.pop('sha256')
        fixity_data['algorithm'] = FixityAlgorithm.objects.filter(name='sha256').first()
        Fixity.objects.create(bag=bag, **fixity_data)
        return bag
