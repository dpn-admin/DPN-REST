"""
    I don't stop eating when I'm full. The meal isn't over when I'm full.
    It's over when I hate myself.
                                    - Louis C. K.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.template.defaultfilters import slugify

# Replication/Restore Status
ACCEPTED  = 'Accepted'
CONFIRMED = 'Confirmed'
CANCELLED = 'Cancelled'
FINISHED  = 'Finished'
PREPARED  = 'Prepared'
REQUESTED = 'Requested'
REJECTED  = 'Rejected'
RECEIVED  = 'Received'
STORED    = 'Stored'
REPL_STATUS_CHOICES = (
    (REQUESTED,REQUESTED),
    (REJECTED, REJECTED),
    (RECEIVED, RECEIVED),
    (CONFIRMED, CONFIRMED),
    (STORED, STORED),
    (CANCELLED, CANCELLED))
RESTORE_STATUS_CHOICES = (
    (REQUESTED, REQUESTED),
    (ACCEPTED, ACCEPTED),
    (REJECTED, REJECTED),
    (PREPARED, PREPARED),
    (FINISHED, FINISHED),
    (CANCELLED, CANCELLED))

# Protocols
HTTPS = 'H'
RSYNC = 'R'
PROTOCOL_CHOICES = (
    (HTTPS, 'https'),
    (RSYNC, 'rsync'),
)

# BAG TYPE INFORMATION
DATA = 'D'
RIGHTS = 'R'
INTERPRETIVE = 'I'
TYPE_CHOICES = (
    (DATA, 'Data'),
    (RIGHTS, 'Rights'),
    (INTERPRETIVE, 'Interpretive')
)
US_STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
US_STATE_CHOICES = ((code, code) for code in US_STATES)


class Protocol(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return '%s' % self.__unicode__()


class FixityAlgorithm(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return '%s' % self.__unicode__()


class Node(models.Model):
    """
    Profile for a specific DPN Node.
    """
    name = models.CharField(max_length=20, unique=True)
    namespace = models.CharField(max_length=20, unique=True)
    api_root = models.URLField(null=True, blank=True)
    ssh_username = models.CharField(max_length=20)
    ssh_pubkey = models.TextField(null=True, blank=True)
    replicate_from = models.ManyToManyField(
        "self", null=True, blank=True, related_name='+')
    replicate_to = models.ManyToManyField(
        "self", null=True, blank=True, related_name='+')
    restore_from = models.ManyToManyField(
        "self", null=True, blank=True, related_name='+')
    restore_to = models.ManyToManyField(
        "self", null=True, blank=True, related_name='+')
    fixity_algorithms = models.ManyToManyField(
        FixityAlgorithm, null=True, blank=True, related_name='+')
    protocols = models.ManyToManyField(Protocol, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_pull_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.namespace:
            self.namespace = slugify(self.name)
        super(Node, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.namespace

    def __str__(self):
        return '%s' % self.__unicode__()


class Storage(models.Model):
    node = models.ForeignKey(Node, related_name='storage')
    region = models.CharField(max_length=2, choices=US_STATE_CHOICES)
    storage_type = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s [%s]" % (self.storage_type, self.region)

    def __str__(self):
        return '%s' % self.__unicode__()

    class Meta:
        unique_together = ('node', 'region')


class Bag(models.Model):
    """
    Data about DPN Bags.
    """
    uuid = models.CharField(max_length=64, primary_key=True)
    local_id = models.TextField(max_length=100, blank=True, null=True)
    size = models.BigIntegerField(blank=False, null=False)
    first_version_uuid = models.CharField(max_length=64, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    ingest_node = models.ForeignKey(Node, related_name="ingest_node")
    bag_type = models.CharField(max_length=1, choices=TYPE_CHOICES,
                                default=DATA)
    rights = models.ManyToManyField(
        "self", null=True, blank=True, related_name="rights_for")
    interpretive = models.ManyToManyField(
        "self", null=True, blank=True, related_name="interpretive_for")
    replicating_nodes = models.ManyToManyField(
        Node, related_name="replicated_bags",
        help_text="Nodes that have confirmed successful transfers.")
    admin_node = models.ForeignKey(
        Node, related_name="administered_bags",
        help_text="The current admin_node for this bag.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def original_fixity(self, algorithm="sha256"):
        """
        Returns the original fixity value for this object.
        """
        return self.fixities.filter(algorithm__name=algorithm).order_by("created_at").first()

    class Meta:
        ordering = ['-updated_at']

    def __unicode__(self):
        return '%s' % self.uuid

    def __str__(self):
        return self.__unicode__()


class Fixity(models.Model):
    """
    Info about bag fixity/checksums. These records are add-only,
    and cannot be updated.
    """
    bag = models.ForeignKey(Bag, related_name="fixities")
    algorithm = models.ForeignKey(FixityAlgorithm, null=False, blank=False)
    digest = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def alg_and_digest(self):
        return "%s:%s" % (self.algorithm.name, self.digest)

    def __unicode__(self):
        return "%s:%s" % (self.algorithm.name, self.digest)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ['created_at']


# Transfer Events
class ReplicationTransfer(models.Model):
    replication_id = models.CharField(
        max_length=20, blank=True, null=True, unique=True)
    from_node = models.ForeignKey(
        Node, null=False, related_name="transfers_out")
    to_node = models.ForeignKey(
        Node, null=False, related_name="transfers_in")
    bag = models.ForeignKey(Bag, related_name="replication_transfers")
    fixity_algorithm = models.ForeignKey(
        FixityAlgorithm, null=False, related_name='+')
    fixity_nonce = models.CharField(max_length=128, null=True, blank=True)
    fixity_value = models.CharField(max_length=128, null=True, blank=True)
    fixity_accept = models.NullBooleanField()
    bag_valid = models.NullBooleanField()
    status = models.CharField(max_length=10, choices=REPL_STATUS_CHOICES,
                              default=REQUESTED)
    protocol = models.CharField(max_length=1, choices=PROTOCOL_CHOICES,
                                default=RSYNC)
    link = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return '%s' % self.replication_id

    def __str__(self):
        return '%s' % self.__unicode__()

    def _fixity_matches(self):
        expected_fixity = self.bag.original_fixity(self.fixity_algorithm.name)
        return (expected_fixity is not None and
                self.fixity_value and
                self.fixity_value == expected_fixity.digest)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            if self._fixity_matches():
                self.fixity_accept = True
                self.status = CONFIRMED
            elif self.fixity_value:
                self.fixity_accept = False
                self.status = CANCELLED
        super(ReplicationTransfer, self).save(*args, **kwargs)


class RestoreTransfer(models.Model):
    restore_id = models.CharField(
        max_length=20, blank=True, null=True, unique=True)
    from_node = models.ForeignKey(
        Node, null=False, related_name="restorations_requested")
    to_node = models.ForeignKey(
        Node, null=False, related_name="restorations_performed")
    bag = models.ForeignKey(Bag)
    status = models.CharField(max_length=10, choices=RESTORE_STATUS_CHOICES,
                              default=REQUESTED)
    protocol = models.CharField(max_length=1, choices=PROTOCOL_CHOICES,
                                default=RSYNC)
    link = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserProfile(models.Model):
    """
    Additional Profile information.
    """
    user = models.OneToOneField(User, related_name="profile")
    # Connects a user to a node for authorization.
    node = models.ForeignKey(Node, blank=True, null=True)


# ********** SIGNALS ***************************
# see: https://docs.djangoproject.com/en/dev/ref/signals/

def _register_node_xfer(sender, instance, created, **kwargs):
    """
    If a transfer is marked as CONFIRMED it should add that node to the
    registry entry for replicating nodes.
    """
    if instance.status == CONFIRMED:
        instance.bag.replicating_nodes.add(instance.to_node)

post_save.connect(_register_node_xfer, sender=ReplicationTransfer)


def create_replication_id(sender, instance, created, **kwargs):
    """
    Creates a namespaced id for the replication transfer based on
    the record id.
    """
    if created and not instance.replication_id:
        instance.replication_id = "%s-%d" % (
            settings.DPN_NAMESPACE, instance.pk)
        instance.save()

post_save.connect(create_replication_id, sender=ReplicationTransfer)


def create_restore_id(sender, instance, created, **kwargs):
    """
    Creates a namespaced id for the restore transfer based on
    the record id.
    """
    if created and not instance.restore_id:
        instance.restore_id = "%s-%d" % (settings.DPN_NAMESPACE, instance.pk)
        instance.save()

post_save.connect(create_restore_id, sender=RestoreTransfer)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
