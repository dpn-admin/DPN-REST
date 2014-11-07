import uuid
import random
from datetime import datetime

from django.utils import timezone
from django.conf import settings

from dpn.data.models import RegistryEntry, Node, Transfer, DATA, Protocol

# Provide ways to autogenerate data so we don't have to reply on fixtures.
def make_test_nodes(mynode=settings.DPN_NAMESPACE):
    # create rsync as protocol
        rsync = Protocol(name='rsync')
        rsync.save()

        storage_data = {
            "aptrust": {"region": 'VA', "type": "Amazon S3"},
            "tdr": {"region": 'TX', "type": "Solaris In Memory"},
            "sdr": {"region": 'CA', "type": "Stanford Superdisk"},
            "hathi": {"region": 'MI', "type": "Thumbdrive"},
            "chron": {"region": 'CA', "type": "CDROM under David's Desk"},
        }

        node_data = {
            "aptrust": {
                "name": "APTrust",
                "namespace": "aptrust",
                "api_root": "https://dpn-dev.aptrust.org/dpnrest/",
                "ssh_username": "aptdpn",
                "replicate_to": True,
            },
            "tdr": {
                "name": "TDR",
                "namespace": "tdr",
                "api_root": "https://dpn.utexas.edu/dpnrest/",
                "ssh_username": "tdrdpn",
                "replicate_from": True,
                "replicate_to": True,
            },
            "sdr": {
                "name": "SDR",
                "namespace": "sdr",
                "api_root": "https://dpn.stanford.edu/dpnrest/",
                "ssh_username": "sdrdpn",
                "replicate_from": True,
                "replicate_to": True,
            },
            "hathi": {
                "name": "HathiTrust",
                "namespace": "hathi",
                "api_root": "https://dpn.hathitrust.org/dpnrest/",
                "ssh_username": "hathidpn",
                "replicate_from": True,
                "replicate_to": True,
            },
            "chron": {
                "name": "Chronopolis",
                "namespace": "chron",
                "api_root": "https://dpn.chronopolis.org/dpnrest/",
                "ssh_username": "chrondpn",
                "replicate_from": True,
                "replicate_to": True,
            },
        }

        for k, v in node_data.items():
            node = Node(**v)
            if node.namespace == mynode:
                node.me = True
            node.save()

            node.port_set.create(**{"ip": "127.0.0.1", "port": "22"})
            node.port_set.create(**{"ip": "127.0.0.1", "port": "443"})
            node.protocols.add(rsync)
            node.storage_set.create(**storage_data[k])

# Makes some registry entries
def make_test_registry_entries(num=10):
    for i in range(num):
        id = uuid.uuid4()
        reg = RegistryEntry()
        reg.dpn_object_id = id
        reg.first_node = Node.objects.order_by('?')[0]
        reg.version_number = 1
        reg.fixity_algorithm = "sha256"
        reg.fixity_value = "%x" % random.getrandbits(128)
        reg.last_fixity_date = timezone.now()
        reg.creation_date = timezone.now()
        reg.last_modified_date = timezone.now()
        reg.object_type = DATA
        reg.first_version = id
        reg.bag_size = random.getrandbits(32)
        reg.published = True
        reg.save()


def make_test_transfers():
    for reg in RegistryEntry.objects.filter(first_node__me=True):
        data = {
            "registry_entry": reg,
            "size": reg.bag_size,
            "exp_fixity": "%x" % random.getrandbits(128)
        }
        for node in Node.objects.exclude(me=True).order_by('?')[:settings.DPN_COPY_TOTAL]:
            xf = Transfer(**data)
            xf.node = node
            xf.link = "%s@dpn.nodename.org:outgoing/%s.tar" % (
            node.ssh_username, xf.registry_entry.dpn_object_id)
            xf.save()