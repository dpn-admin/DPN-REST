import uuid, random, hashlib
from datetime import datetime

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from dpn.data.models import  Node, DATA, SEND, RSYNC, PENDING
from dpn.data.models import RegistryEntry, Transfer

class Command(BaseCommand):
    help = 'Populates the DB with test data'

    def handle(self, *args, **options):
        if not Node.objects.get(name="APTrust"):
            raise CommandError("No node named APTrust")

        # Clear Bag Data = funny pattern due to sqlite3
        for reg in RegistryEntry.objects.all():
            reg.delete()
        for xfer in Transfer.objects.all():
            xfer.delete()

        # Make some registry entries
        for i in range(1000):
            id = uuid.uuid4()
            reg = RegistryEntry()
            reg.dpn_object_id = id
            reg.first_node = Node.objects.order_by('?')[0].name
            reg.version_number = 1
            reg.fixity_algorithm = "sha256"
            reg.fixity_value = "%x" % random.getrandbits(128)
            reg.last_fixity_date = timezone.now()
            reg.creation_date = datetime.now()
            reg.last_modified_date = timezone.now()
            reg.object_type = DATA
            reg.first_version = id
            reg.bag_size = random.getrandbits(32)
            reg.published = True
            reg.save()

        # Create Ingest Transfers
        for reg in RegistryEntry.objects.filter(first_node="APTrust"):
            data = {
                "dpn_object_id": reg.dpn_object_id,
                "action": SEND,
                "protocol": RSYNC,
                "status": PENDING,
                "size": reg.bag_size,
                "exp_fixity": "%x" % random.getrandbits(128)
            }
            for node in Node.objects.exclude(name="APTrust").order_by('?')[:3]:
                xf = Transfer(**data)
                xf.node = node
                xf.link = "%s@dpn-dev.aptrust.org:outgoing/%s.tar" % (node.ssh_username, data["dpn_object_id"])
                xf.save()
