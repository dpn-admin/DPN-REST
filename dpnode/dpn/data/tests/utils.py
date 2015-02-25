"""
    'Turing Test Extra Credit: Convince the examiner that he is a computer.'
                        - xkcd
"""

import uuid
import random
import string
from datetime import datetime

from django.utils import timezone
from django.conf import settings
from django.test.utils import override_settings
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

from dpn.data.models import Bag, Node, ReplicationTransfer
from dpn.data.models import RestoreTransfer, Storage, Fixity
from dpn.data.models import UserProfile, DATA, RSYNC, SHA256, Protocol
from dpn.data.utils import dpn_strftime


# Provide ways to autogenerate data so we don't have to reply on fixtures.
def make_test_nodes():
    # create rsync as protocol
    rsync = Protocol(name='rsync')
    rsync.save()

    storage_data = {
        "aptrust": {"region": 'VA', "storage_type": "Amazon S3"},
        "tdr": {"region": 'TX', "storage_type": "Solaris In Memory"},
        "sdr": {"region": 'CA', "storage_type": "Stanford Superdisk"},
        "hathi": {"region": 'MI', "storage_type": "Thumbdrive"},
        "chron": {"region": 'CA', "storage_type": "CDROM under David's Desk"},
    }

    node_data = {
        "aptrust": {
            "name": "APTrust",
            "namespace": "aptrust",
            "api_root": "https://devops.aptrust.org/dpnode/",
            "ssh_username": "dpn.aptrust",
        },
        "tdr": {
            "name": "TDR",
            "namespace": "tdr",
            "api_root": "https://rest.lib.utexas.edu/",
            "ssh_username": "dpn.tdr",
        },
        "sdr": {
            "name": "SDR",
            "namespace": "sdr",
            "api_root": "https://dpn.stanford.edu/dpnrest/",
            "ssh_username": "dpn.sdr",
        },
        "hathi": {
            "name": "HathiTrust",
            "namespace": "hathi",
            "api_root": "https://dpn.hathitrust.org/dpnrest/",
            "ssh_username": "dpn.hathi",
        },
        "chron": {
            "name": "Chronopolis",
            "namespace": "chron",
            "api_root": "https://chronopolis01.umiacs.umd.edu/",
            "ssh_username": "dpn.chron",
        },
    }

    node_objs = []
    for k, v in node_data.items():
        node = Node(**v)
        node.save()
        node.protocols.add(rsync)
        node.storage.create(**storage_data[k])
        node.save()
        node_objs.append(node)

    for node in node_objs:
        current_node = node
        for other_node in node_objs:
            if other_node.namespace != current_node.namespace:
                current_node.replicate_to.add(other_node)
                current_node.replicate_from.add(other_node)
                current_node.restore_to.add(other_node)
                current_node.restore_from.add(other_node)


def make_test_user(uname, pwd, eml, groupname=None, nodename=None,
                   superuser=False):
    # setup API user

    create_method = User.objects.create_user
    if superuser:
        create_method = User.objects.create_superuser

    api_user = create_method(
        username=uname,
        password=pwd,
        email=eml
    )

    api_user.profile.node = Node.objects.exclude(namespace=settings.DPN_NAMESPACE).order_by('?')[0]
    if nodename:
        api_user.profile.node = Node.objects.get(namespace=nodename)

    api_user.profile.save()

    Token.objects.create(user=api_user)

    if groupname:
        group = Group.objects.get(name=groupname)
        group.user_set.add(api_user)

    return api_user


# Makes some registry entries
def make_bag_data():
    id = "%s" % uuid.uuid4()
    return {
        "uuid": id,
        "original_node": Node.objects.order_by('?')[0],
        "version": 1,
        "created_at": timezone.now(),
        "updated_at": timezone.now(),
        "bag_type": DATA,
        "first_version_uuid": id,
        "size": random.getrandbits(32),
    }


def make_bag_postdata():
    data = make_bag_data()
    data["original_node"] = data["original_node"]
    data["admin_node"] = data["original_node"]
    data["created_at"] = dpn_strftime(data["created_at"])
    data["updated_at"] = dpn_strftime(data["updated_at"])
    return data


def make_test_bags(num=10):
    for i in range(num):
        bag = Bag(**make_bag_postdata())
        bag.save()
        fixity = Fixity(
            algorithm=SHA256,
            digest=random.getrandbits(64),
            bag=bag
        )
        bag.fixities.add(fixity)


def make_test_transfers():
    for bag in Bag.objects.filter(
            original_node__namespace=settings.DPN_NAMESPACE):
        data = {
            "bag": bag,
            "fixity_algorithm": "sha256",
            "protocol": RSYNC,
        }
        restore_data = data.copy()
        del restore_data["fixity_algorithm"]
        this_node = Node.objects.filter(namespace=settings.DPN_NAMESPACE).first()
        for node in Node.objects.exclude(
                namespace=settings.DPN_NAMESPACE).order_by('?')[
                    :settings.DPN_COPY_TOTAL]:
            nonce = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            repl_transfer = ReplicationTransfer(**data)
            repl_transfer.to_node = node
            repl_transfer.from_node = this_node
            repl_transfer.fixity_nonce = nonce
            repl_transfer.link = "%s@dpn.nodename.org:outgoing/%s.tar" % (
                node.ssh_username, repl_transfer.bag.uuid)
            repl_transfer.save()


            restore_transfer = RestoreTransfer(**restore_data)
            restore_transfer.from_node = node
            restore_transfer.to_node = this_node
            restore_transfer.save()
