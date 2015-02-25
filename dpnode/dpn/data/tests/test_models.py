"""
    I'm an idealist. I don't know where I'm going, but I'm on my way.
    - Carl Sandburg
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.test.utils import override_settings

from dpn.data.models import ReplicationTransfer, RestoreTransfer
from dpn.data.tests.utils import make_test_nodes, make_test_transfers, \
    make_test_bags

@override_settings(DPN_NAMESPACE='aptrust')
class ReplicationTransferTest(TestCase):
    def setUp(self):
        make_test_nodes()
        make_test_bags(30)
        make_test_transfers()

    def test_save(self):
        xfer = ReplicationTransfer.objects.all().order_by('?')[0]
        xfer.save()

        # It should have a proper format replication_id
        exp = "%s-%d" % (settings.DPN_NAMESPACE, xfer.id)
        self.failUnlessEqual(exp, xfer.replication_id)

        # It should still read fixty None.
        self.assertTrue(xfer.fixity_value is None,
                        "Expected None on fixity but returned %s" % xfer.fixity_value)

        # It should read fixity false.
        xfer.receipt = "lknalkndlfknsfdsf"
        xfer.save()
        self.assertFalse(xfer.fixity_value,
                         "Expected False fixity but returned %s" % xfer.fixity_value)

        # It should read fixity_accept == True.
        xfer.fixity_value = xfer.bag.original_fixity().digest
        xfer.save()
        self.assertTrue(xfer.fixity_accept,
                        "Expected True fixity but returned %s" % xfer.fixity_accept)

        # It should list the node in the registry entry.
        nodes = xfer.bag.replicating_nodes.all()
        self.assertTrue(xfer.to_node in nodes,
                        "%s not listed as replication node!" % xfer.to_node)

@override_settings(DPN_NAMESPACE='aptrust')
class TestUserProfile(TestCase):
    def test_create_user_profile(self):
        u = User(username="testuser", password="nothing", email="me@email.com")
        u.save()

        profile = u.profile
        self.assertTrue(profile is not None, "User profile not found!")
