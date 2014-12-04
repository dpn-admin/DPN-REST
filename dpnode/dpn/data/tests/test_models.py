"""
    I'm an idealist. I don't know where I'm going, but I'm on my way.
    - Carl Sandburg
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.test.utils import override_settings

from dpn.data.models import Transfer
from dpn.data.tests.utils import make_test_nodes, make_test_transfers, \
    make_test_registry_entries

@override_settings(DPN_NAMESPACE='aptrust')
class TransferTest(TestCase):
    def setUp(self):
        make_test_nodes()
        make_test_registry_entries(30)
        make_test_transfers()

    def test_save(self):
        xfer = Transfer.objects.all().order_by('?')[0]
        xfer.save()

        # It should have a proper format event_id
        exp = "%s-%d" % (settings.DPN_NAMESPACE, xfer.id)
        self.failUnlessEqual(exp, xfer.event_id)

        # It should still read fixty None.
        self.assertTrue(xfer.fixity is None,
                        "Expected None on fixity but returned %s" % xfer.fixity)

        # It should read fixity false.
        xfer.receipt = "lknalkndlfknsfdsf"
        xfer.save()
        self.assertFalse(xfer.fixity,
                         "Expected False fixity but returned %s" % xfer.fixity)

        # It should read fixity true.
        xfer.receipt = xfer.exp_fixity
        xfer.receipt_type = xfer.fixity_type
        xfer.save()
        self.assertTrue(xfer.fixity,
                        "Expected True fixity but returned %s" % xfer.fixity)

        # It should list the node in the registry entry.
        nodes = xfer.registry_entry.replicating_nodes.all()
        self.assertTrue(xfer.node in nodes,
                        "%s not listed as replication node!" % xfer.node)

@override_settings(DPN_NAMESPACE='aptrust')
class TestUserProfile(TestCase):
    def test_create_user_profile(self):
        u = User(username="testuser", password="nothing", email="me@email.com")
        u.save()

        profile = u.profile
        self.assertTrue(profile is not None, "User profile not found!")