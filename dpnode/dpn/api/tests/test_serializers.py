"""
    'The trouble with having an open mind, of course, is that people will insist
     on coming along and trying to put things in it.'

                    - Terry Pratchett
"""

import json
from django.test import TestCase
from dpn.api.serializers import CreateTransferSerializer
from dpn.api.serializers import BasicTransferSerializer, NodeSerializer
from dpn.api.serializers import RegistryEntrySerializer


from dpn.data.models import RegistryEntry, Node, Protocol
from dpn.data.tests.utils import make_registry_data, make_test_nodes

# Data Fixtures
# The point here is to use the exact same structures posted to the Wiki
# so we can be sure our documented data structures always pass.

# https://github.com/APTrust/EarthDiver/wiki/API-Endpoint:-Transfer#post-operation-internal
XFER_POST = json.loads("""{
    "dpn_object_id":"8044ea1a-cba5-44e7-a4d5-122f649f81a4",
    "link":"sshaccount@dpnserver.test.org:8044ea1a-cba5-44e7-a4d5-122f649f81a4.tar",
    "node":"chron",
    "size":3239653228,
    "exp_fixity":"eced7e98269750587531381811b2a59f"
}""")

# https://github.com/APTrust/EarthDiver/wiki/API-Endpoint:-Transfer#get-operation-external
XFER_DATA = json.loads("""{
            "node":"chron",
            "dpn_object_id":"8287ee9e-74f1-490b-8209-800985361134",
            "status":"P",
            "event_id":"aptrust-1665",
            "protocol":"R",
            "link":"chrondpn@dpn.nodename.org:outgoing/8287ee9e-74f1-490b-8209-800985361134.tar",
            "size":543891175,
            "fixity_type": "sha256",
            "receipt":null,
            "fixity":null,
            "valid":null,
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
    "replicate_from":true,
    "replicate_to":true,
    "restore_from":false,
    "restore_to":false,
    "created_on":"2014-11-11T00:27:16.093555Z",
    "updated_on":"2014-11-11T00:27:16.093586Z"
}""")

REGISTRY_DATA = json.loads("""{
    "first_node":"sdr",
    "brightening_objects":[],
    "rights_objects":[],
    "replicating_nodes":[],
    "dpn_object_id":"892c3cca-4e18-4873-9c7e-758f5d17a5e9",
    "local_id":null,
    "version_number":1,
    "creation_date":"2014-11-11T00:27:16.206545Z",
    "last_modified_date":"2014-11-11T00:27:16.206550Z",
    "bag_size":2158502848,
    "object_type":"D",
    "previous_version":null,
    "forward_version":null,
    "first_version":"892c3cca-4e18-4873-9c7e-758f5d17a5e9"
}""")

#****** TESTS ******#

class CreateTransferSerializerTest(TestCase):

    def test_data(self):
        xfer = CreateTransferSerializer(data=XFER_POST)
        # It should fail to validate if related objects not created.
        self.assertFalse(xfer.is_valid(), "Did not expect this to validate!")

        make_test_nodes()
        data = make_registry_data()
        data['dpn_object_id'] = XFER_POST["dpn_object_id"]
        data['first_node'] = Node.objects.get(namespace=XFER_POST["node"])
        re = RegistryEntry(**data)
        re.save()

        # It should validate with good data.
        xfer = CreateTransferSerializer(data=XFER_POST)
        self.assertTrue(xfer.is_valid(), xfer._errors)

class BasicTransferSerializerTest(TestCase):

    def test_data(self):
        # It should validate based on this structure.
        xfer = BasicTransferSerializer(data=XFER_DATA)
        self.assertTrue(xfer.is_valid())

class NodeSerializerTest(TestCase):

    def test_data(self):
        node = NodeSerializer(data=NODE_DATA)
        ptcl = Protocol(name='rsync')
        ptcl.save()
        self.assertTrue(node.is_valid(), node._errors)

class RegistrySerializerTest(TestCase):

    def test_data(self):
        make_test_nodes()
        reg = RegistryEntrySerializer(data=REGISTRY_DATA)
        self.assertTrue(reg.is_valid(), reg._errors)