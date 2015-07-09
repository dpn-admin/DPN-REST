"""
    'The trouble with having an open mind, of course, is that people will insist
     on coming along and trying to put things in it.'

                    - Terry Pratchett
"""

import json
import random
from django.test import TestCase
from dpn.api.serializers import CreateReplicationSerializer
from dpn.api.serializers import CreateRestoreSerializer
from dpn.api.serializers import BasicReplicationSerializer, NodeSerializer
from dpn.api.serializers import BagSerializer, BasicRestoreSerializer

from dpn.data.models import Bag, Node, Protocol, Fixity, FixityAlgorithm
from dpn.data.tests.utils import make_bag_data, make_test_nodes
from dpn.data.tests.utils import make_fixity_algs, sha256_algorithm

# Data Fixtures
# The point here is to use the exact same structures posted to the Wiki
# so we can be sure our documented data structures always pass.

# https://github.com/APTrust/EarthDiver/wiki/API-Endpoint:-Transfer#post-operation-internal
REPL_POST = json.loads("""{
    "uuid":"8044ea1a-cba5-44e7-a4d5-122f649f81a4",
    "link":"sshaccount@dpnserver.test.org:8044ea1a-cba5-44e7-a4d5-122f649f81a4.tar",
    "to_node":"chron",
    "from_node":"aptrust",
    "size":3239653228,
    "fixity_algorithm": "sha256",
    "protocol": "R"
}""")

# https://github.com/APTrust/EarthDiver/wiki/API-Endpoint:-Transfer#get-operation-external
REPL_DATA = json.loads("""{
            "from_node":"aptrust",
            "to_node": "tdr",
            "uuid":"8287ee9e-74f1-490b-8209-800985361134",
            "status":"Requested",
            "replication_id":"aptrust-1665",
            "protocol":"R",
            "link":"chrondpn@dpn.nodename.org:outgoing/8287ee9e-74f1-490b-8209-800985361134.tar",
            "fixity_algorithm": "sha256",
            "fixity_value":null,
            "fixity_accept":null,
            "bag_valid":null,
            "created_on":"2014-11-11T00:27:20.295603Z",
            "updated_on":"2014-11-11T00:27:20.297468Z"
        }""")


RESTORE_POST = json.loads("""{
    "uuid":"8044ea1a-cba5-44e7-a4d5-122f649f81a4",
    "to_node":"chron",
    "from_node":"aptrust",
    "protocol": "R"
}""")

RESTORE_DATA = json.loads("""{
            "from_node":"aptrust",
            "to_node": "tdr",
            "uuid":"8287ee9e-74f1-490b-8209-800985361134",
            "status":"Requested",
            "replication_id":"aptrust-1665",
            "protocol":"R",
            "link":"chrondpn@dpn.nodename.org:outgoing/8287ee9e-74f1-490b-8209-800985361134.tar",
            "fixity_algorithm": "sha256",
            "fixity_value":null,
            "fixity_accept":null,
            "bag_valid":null,
            "created_on":"2014-11-11T00:27:20.295603Z",
            "updated_on":"2014-11-11T00:27:20.297468Z"
        }""")


# https://github.com/APTrust/EarthDiver/wiki/API-Endpoint:-Node
NODE_DATA = json.loads("""{
    "storage":[
        {
            "region":"VA",
            "type":"Amazon S3"
        }
    ],
    "protocols":[
        "rsync"
    ],
    "name":"APTrust",
    "namespace":"aptrust",
    "api_root":"https://dpn-dev.aptrust.org/dpnrest/",
    "ssh_pubkey":null,
    "replicate_from": ["tdr", "sdr", "chron", "hathi"],
    "replicate_to": ["tdr", "sdr", "chron", "hathi"],
    "restore_from": ["tdr", "sdr", "chron", "hathi"],
    "restore_to": ["tdr", "sdr", "chron", "hathi"],
    "created_on":"2014-11-11T00:27:16.093555Z",
    "updated_on":"2014-11-11T00:27:16.093586Z"
}""")

BAG_DATA = json.loads("""{
    "ingest_node":"sdr",
    "admin_node":"sdr",
    "interpretive":[],
    "rights":[],
    "replicating_nodes":[],
    "uuid":"892c3cca-4e18-4873-9c7e-758f5d17a5e9",
    "local_id":null,
    "version_number":1,
    "creation_date":"2014-11-11T00:27:16.206545Z",
    "last_modified_date":"2014-11-11T00:27:16.206550Z",
    "bag_size":2158502848,
    "object_type":"D",
    "first_version_uuid":"892c3cca-4e18-4873-9c7e-758f5d17a5e9",
    "size": 78776,
    "fixities":
        {
          "sha256": "765765765765"
        }
}""")

#****** TESTS ******#

class CreateReplicationSerializerTest(TestCase):

    def test_data(self):
        repl = CreateReplicationSerializer(data=REPL_POST)
        # It should fail to validate if related objects not created.
        self.assertFalse(repl.is_valid(), "Did not expect this to validate!")

        make_test_nodes()
        make_fixity_algs()
        data = make_bag_data()
        data['uuid'] = REPL_POST["uuid"]
        data['ingest_node'] = Node.objects.get(namespace=REPL_POST["from_node"])
        data['admin_node'] = Node.objects.get(namespace=REPL_POST["from_node"])
        re = Bag(**data)
        re.save()

        # It should validate with good data.
        repl = CreateReplicationSerializer(data=REPL_POST)
        self.assertTrue(repl.is_valid(), repl._errors)

class BasicReplicationSerializerTest(TestCase):

    def test_data(self):
        # It should validate based on this structure.
        repl = BasicReplicationSerializer(data=REPL_DATA)
        self.assertTrue(repl.is_valid(), repl._errors)

class CreateRestoreSerializerTest(TestCase):

    def test_data(self):
        restore = CreateRestoreSerializer(data=RESTORE_POST)
        # It should fail to validate if related objects not created.
        self.assertFalse(restore.is_valid(), "Did not expect this to validate!")

        # Set up data for this test...
        make_test_nodes()
        make_fixity_algs()
        data = make_bag_data()
        data['uuid'] = RESTORE_POST["uuid"]
        data['ingest_node'] = Node.objects.get(namespace=RESTORE_POST["from_node"])
        data['admin_node'] = Node.objects.get(namespace=RESTORE_POST["from_node"])
        bag = Bag(**data)
        bag.save()
        fixity = Fixity(
            algorithm=sha256_algorithm(),
            digest=random.getrandbits(64),
            bag=bag
        )
        bag.fixities.add(fixity)


        # It should validate with good data.
        restore = CreateRestoreSerializer(data=RESTORE_POST)
        self.assertTrue(restore.is_valid(), restore._errors)

class BasicRestoreSerializerTest(TestCase):

    def test_data(self):
        # It should validate based on this structure.
        make_test_nodes()
        data = make_bag_data()
        data['uuid'] = RESTORE_DATA["uuid"]
        data['ingest_node'] = Node.objects.get(namespace=RESTORE_POST["from_node"])
        data['admin_node'] = Node.objects.get(namespace=RESTORE_POST["from_node"])
        bag = Bag(**data)
        bag.save()

        restore = BasicRestoreSerializer(data=RESTORE_DATA)
        self.assertTrue(restore.is_valid(), restore._errors)

class NodeSerializerTest(TestCase):

    def test_data(self):
        node = NodeSerializer(data=NODE_DATA)
        ptcl = Protocol(name='rsync')
        ptcl.save()
        self.assertTrue(node.is_valid(), node._errors)

class BagSerializerTest(TestCase):

    def test_data(self):
        make_test_nodes()
        make_fixity_algs()
        reg = BagSerializer(data=BAG_DATA)
        self.assertTrue(reg.is_valid(), reg._errors)
