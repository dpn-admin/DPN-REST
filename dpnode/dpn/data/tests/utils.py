"""
    'Turing Test Extra Credit: Convince the examiner that he's a computer.'
                        - xkcd
"""

import uuid
import random
from datetime import datetime

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group

from rest_framework.authtoken.models import Token

from dpn.data.models import RegistryEntry, Node, Transfer, DATA, Protocol
from dpn.data.models import UserProfile
from dpn.data.utils import dpn_strftime

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
                "replicate_from": True,
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

def make_test_user(uname, pwd, eml, groupname=None, nodename=None):
    # setup API user

    api_user = User(
        username=uname,
        password=pwd,
        email=eml
    )
    api_user.save()

    profile = UserProfile.objects.get(user=api_user)
    if nodename:
        profile.node = Node.objects.get(namespace=nodename)
    else:
        profile.node = Node.objects.exclude(me=True)[0]
    profile.save()

    Token.objects.create(user=api_user)

    if groupname:
        group = Group.objects.get(name=groupname)
        group.user_set.add(api_user)

    return api_user

# Makes some registry entries
def make_registry_data():
    id = "%s" % uuid.uuid4()
    return {
        "dpn_object_id": id,
        "first_node": Node.objects.order_by('?')[0],
        "version_number": 1,
        "fixity_algorithm": "sha256",
        "fixity_value": "%x" % random.getrandbits(128),
        "last_fixity_date": timezone.now(),
        "creation_date": timezone.now(),
        "last_modified_date": timezone.now(),
        "object_type": DATA,
        "first_version": id,
        "bag_size": random.getrandbits(32),
    }

def make_registry_postdata():
    data = make_registry_data()
    data["first_node"] = data["first_node"].namespace
    data["last_fixity_date"] = dpn_strftime(data["last_fixity_date"])
    data["creation_date"] = dpn_strftime(data["creation_date"])
    data["last_modified_date"] = dpn_strftime(data["last_modified_date"])
    data["rights_objects"] = []
    data["brightening_objects"] = []
    data["replicating_nodes"] = []
    return data

def make_test_registry_entries(num=10):
    for i in range(num):
        reg = RegistryEntry(**make_registry_data())
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
