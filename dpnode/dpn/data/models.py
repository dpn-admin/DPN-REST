from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from django.template.defaultfilters import slugify

# Status
PENDING = 'P'
ACCEPT = 'A'
REJECT = 'R'
CONFIRMED = 'C'
VALID = 'V'
STATE_CHOICES = (
    (PENDING, "Pending"),
    (ACCEPT, "Accept"),
    (REJECT, "Reject"),
    (CONFIRMED, "Confirmed"),
)
# Protocols
HTTPS = 'H'
RSYNC = 'R'
PROTOCOL_CHOICES = (
    (HTTPS, 'https'),
    (RSYNC, 'rsync')
)

# BAG TYPE INFORMATION
DATA = 'D'
RIGHTS = 'R'
BRIGHTENING = 'B'
TYPE_CHOICES = (
    (DATA, 'Data'),
    (RIGHTS, 'Rights'),
    (BRIGHTENING, 'Brightening')
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

class Node(models.Model):
    """
    Profile for a specific DPN Node.
    """
    name = models.CharField(max_length=20, unique=True)
    namespace = models.CharField(max_length=20, unique=True)
    api_endpoint = models.URLField(null=True, blank=True)
    ssh_username = models.CharField(max_length=20)
    ssh_pubkey = models.TextField(null=True, blank=True)
    pull_from = models.BooleanField(default=False)
    replicate_to = models.BooleanField(default=False)
    protocols = models.ManyToManyField(Protocol, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True, auto_now=True)

    def save(self, *args, **kwargs):
        if not self.namespace:
            self.namespace = slugify(self.name)
        super(Node, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return '%s' % self.__unicode__()

class Port(models.Model):
    """
    List of important IP numbers and ports needed for firewall rules.
    """
    node = models.ForeignKey(Node)
    ip = models.IPAddressField()
    port = models.PositiveIntegerField()
    note = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return '%s: %d' % (self.ip, self.port)

    def __str__(self):
        return '%s' % self.__unicode__()

    class Meta:
        unique_together = ("node", "ip", "port")

class Storage(models.Model):
    node = models.ForeignKey(Node)
    region = models.CharField(max_length=2, choices=US_STATE_CHOICES)
    type = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s [%s]" % (self.type, self.region)

    def __str__(self):
        return '%s' % self.__unicode__()

    class Meta:
        unique_together = ('node', 'region')

class RegistryManager(models.Manager):
    """
    Custom manager to return only published registry entries.
    """
    def get_queryset(self):
        return super(RegistryManager, self).get_queryset().filter(published=True)

class RegistryEntry(models.Model):
    """
    Data about DPN Bags.
    """
    dpn_object_id = models.CharField(max_length=64, primary_key=True)
    local_id = models.TextField(max_length=100, blank=True, null=True)
    first_node = models.ForeignKey(Node)
    version_number = models.PositiveIntegerField(default=1)
    fixity_algorithm = models.CharField(max_length=10)
    fixity_value = models.CharField(max_length=128)
    last_fixity_date = models.DateTimeField()
    creation_date = models.DateTimeField()
    last_modified_date = models.DateTimeField()
    bag_size = models.BigIntegerField()

    object_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=DATA)

    # Note in the future we should build lose validation.  We don't want to
    # make it a foreign key because we always want to record the registry entry
    # but we should set state to suspect if any of these don't have a match
    # in the registry.
    previous_version = models.CharField(max_length=64, null=True, blank=True)
    forward_version =  models.CharField(max_length=64, null=True, blank=True)
    first_version = models.CharField(max_length=64, null=True, blank=True)

    brightening_objects = models.ManyToManyField("self", null=True, blank=True)
    rights_objects = models.ManyToManyField("self", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, auto_now_add=True)
    published = models.BooleanField(default=False)

    # Custom manager to return only published records
    # published_objects = RegistryManager()

    class Meta:
        verbose_name_plural = "registry entries"
        ordering = ['-updated_on']

    def __unicode__(self):
        return '%s' % self.dpn_object_id

    def __str__(self):
        return '%s' % self.__unicode__()

#  Transfer Events
class Transfer(models.Model):
    dpn_object_id = models.CharField(max_length=64)
    event_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    protocol = models.CharField(max_length=1, choices=PROTOCOL_CHOICES)
    link = models.TextField(null=True, blank=True)
    node = models.ForeignKey(Node)
    status = models.CharField(max_length=1, choices=STATE_CHOICES, default=PENDING)
    size = models.BigIntegerField()
    receipt = models.CharField(max_length=128, null=True, blank=True)
    exp_fixity = models.CharField(max_length=128)
    fixity = models.NullBooleanField()
    valid = models.NullBooleanField()
    error = models.TextField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __unicode__(self):
        return '%s' % self.dpn_object_id

    def __str__(self):
        return '%s' % self.__unicode__()

    def save(self, *args, **kwargs):
        if self.exp_fixity == self.receipt:
            self.fixity = True
            self.status = CONFIRMED
        if self.exp_fixity != self.receipt and self.receipt is not None:
            self.fixity = False
        super(Transfer, self).save(args, kwargs)

def create_event_id(sender, instance, created, **kwargs):
    """
    Creates a namespaced id for the event based on the record id.
    """
    if created and not instance.event_id:
        instance.event_id = "%s-%d" % (settings.DPN_NAMESPACE, instance.pk)
        instance.save()
post_save.connect(create_event_id, sender=Transfer)

# Additional User Profile Info
class UserProfile(models.Model):
        user = models.OneToOneField(User)
        node = models.ForeignKey(Node, blank=True, null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)