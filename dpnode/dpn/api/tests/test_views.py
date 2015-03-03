"""
    I fantasize and idealize myself as Bugs Bunny, but I know deep down I'm
    Daffy Duck.
                    - Patton Oswalt

"""
import json
import random

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.test.utils import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from dpn.data.models import Node, Bag, ReplicationTransfer
from dpn.data.models import RestoreTransfer, UserProfile, REJECTED
from dpn.data.utils import dpn_strptime
from dpn.data.tests.utils import make_test_transfers, make_test_bags
from dpn.data.tests.utils import make_test_nodes, make_bag_postdata
from dpn.data.tests.utils import make_test_user


def _make_api_user():
    "Makes a user with a token in the api_user group."
    return make_test_user("apiuser", "apiuser", "me@email.com", "api_users")

def _make_api_admin():
    "Makes a user with a token in the api_admin group."
    return make_test_user("adminuser", "adminuser", "me@email.com",
                          "api_admins", superuser=True)

def _make_auth_user():
    "Makes a user with a token but no group."
    return make_test_user("authuser", "authuser", "auth@email.com", None)

# # List Views

@override_settings(DPN_NAMESPACE='aptrust')
class BagListViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json', ]

    def setUp(self):
        # Setup Test Data
        make_test_nodes()
        make_test_bags(100)
        make_test_transfers()

        self.url = reverse('api:bag-list')

        # setup Non API user
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()

    def test_get(self):
        # It should not authorize an unauthenticated user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # It should authorize an authenticated user.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="token %s" % token.key)
        response = self.client.get(self.url)

        bags = Bag.objects.all()

        # It should contain the right count of bags.
        self.assertEqual(response.data['count'], bags.count())

        # Bags should be ordered by updated_at desc
        previous = None
        for result in response.data['results']:
            current = dpn_strptime(result["updated_at"])
            if previous:
                self.assertTrue(current < previous)
            previous = current

    def test_put(self):
        # It should not allow this method. You can't update a bag.
        # You have to post a new version and increment the version
        # number.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.put(self.url, {})
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch(self):
        # It should not allow this method.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.patch(self.url, {})
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_post(self):
        data = make_bag_postdata()
        data['fixities'] = [
            {
                    "algorithm": "sha256",
                    "digest": "909090909078787878781234",
                    "created_at": "2015-02-25T15:27:40.383861Z"
            }]
        data['original_node'] = 'aptrust'
        data['admin_node'] = 'aptrust'

        # It should not allows api_users to create a bag
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN, rsp.data)

        # It should allow api_admins to create a bag.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data, format="json")
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED)

@override_settings(DPN_NAMESPACE='aptrust')
class NodeListViewTest(APITestCase):
    fixtures = ["../data/GroupPermissions.json", ]

    def setUp(self):
        make_test_nodes()
        self.url = reverse('api:node-list')
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()
        self.auth_user = _make_auth_user()

    def test_get(self):
        # It should deny access to anonomous users.
        rsp = self.client.get(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_401_UNAUTHORIZED)

        def _test_each_group(u):  # It should list nodes for authorized users
            token = Token.objects.get(user=u)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            rsp = self.client.get(self.url)
            self.assertEqual(rsp.data['count'], 5)

        _test_each_group(self.api_user)
        _test_each_group(self.api_admin)

    def test_post(self):
        data = {
            "name": "TestNode",
            "namespace": "testnode",
            "api_root": "https://test.api.org/",
            "storage": [{"region": "NJ", "type": "Test storage"},],
            # "ssh_username": "dpntestnode",
        }
        # It should deny an unauthorized user.
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_401_UNAUTHORIZED)

        # It should deny an api_user.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # It should allow api_admin to create a node.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED, rsp.content)

    def test_bad_requests(self):
        tokens = [Token.objects.get(user=self.api_admin),
                  Token.objects.get(user=self.api_user)]
        # these methods are not implemented, but you may get a 403
        # for api_user, since the permission check happens early in
        # the request.
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            # put not implemented
            rsp = self.client.put(self.url)
            self.assertIn(rsp.status_code,
                          [status.HTTP_403_FORBIDDEN,
                           status.HTTP_405_METHOD_NOT_ALLOWED])
            # patch not allowed
            rsp = self.client.patch(self.url)
            self.assertIn(rsp.status_code,
                          [status.HTTP_403_FORBIDDEN,
                           status.HTTP_405_METHOD_NOT_ALLOWED])

            # delete not allowed
            rsp = self.client.delete(self.url)
            self.assertIn(rsp.status_code,
                          [status.HTTP_403_FORBIDDEN,
                           status.HTTP_405_METHOD_NOT_ALLOWED])

@override_settings(DPN_NAMESPACE='aptrust')
class ReplicationTransferListViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json', ]

    def setUp(self):
        # Setup Test Data
        make_test_nodes()
        make_test_bags(100)
        make_test_transfers()
        self.url = reverse('api:replication-list')
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()

    def test_get(self):

        def _test_return_count(user, url, exp_count):
            # Tests for expected object count.
            token = Token.objects.get(user=user)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            rsp = self.client.get(url)
            self.assertEqual(rsp.data['count'], exp_count)
            self.assertEqual(rsp.status_code, status.HTTP_200_OK)

        # It should return all transfers if no filter is specified.
        xfers = ReplicationTransfer.objects.all()
        _test_return_count(self.api_user, self.url, xfers.count())

        # It should return all transfers for superusers.
        xfers = ReplicationTransfer.objects.all()
        _test_return_count(self.api_admin, self.url, xfers.count())

        mynode = Node.objects.get(namespace=settings.DPN_NAMESPACE)

        # It should filter transfers by bag uuid
        bag = Bag.objects.filter(original_node=mynode).order_by('?')[0]
        xfers = ReplicationTransfer.objects.filter(bag=bag)
        url = "%s?bag=%s" % (reverse('api:replication-list'),
                                       bag.uuid)
        _test_return_count(self.api_admin, url, xfers.count())

        # It should filter transfers by status
        xfer = ReplicationTransfer.objects.all().first()
        xfer.status = REJECTED
        xfer.save()
        url = "%s?status=%s" % (reverse('api:replication-list'), REJECTED)
        _test_return_count(self.api_user, url, 1)

        # It should filter based on bag uuid
        # Test data generator creates two transfer requests
        # for each bag.
        bag = ReplicationTransfer.objects.all().first().bag
        url = "%s?bag=%s" % (reverse('api:replication-list'), bag.uuid)
        _test_return_count(self.api_admin, url, 2)

        # It should filter based on to_node
        node = self.api_user.profile.node
        xfers = ReplicationTransfer.objects.filter(to_node=node)
        url = "%s?to_node=%s" % (reverse('api:replication-list'), node.namespace)
        _test_return_count(self.api_admin, url, xfers.count())

    def test_post(self):
        # It should not allow anoymous users from posting
        rsp = self.client.post(self.url, {})
        self.assertEqual(rsp.status_code, status.HTTP_401_UNAUTHORIZED)

        # It should not allow api_users to create transfers.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, {})
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # Create a test transfer post.
        bag = Bag.objects.filter(original_node__namespace=settings.DPN_NAMESPACE)[0]
        data = {
            "bag": bag.uuid,
            "link": "sshaccount@dpnserver.test.org:%s.tar" % bag.uuid,
            "to_node": Node.objects.exclude(namespace=settings.DPN_NAMESPACE)[0].namespace,
            "from_node": self.api_admin.profile.node.namespace,
            "fixity_algorithm": "sha256",
            "fixity_nonce": "1234ABC",
            "protocol": "R",
        }

        # It should allow api_admins to create replication transfers.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rsp.data, data)

    def test_put(self):
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.put(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


## Detail Views
@override_settings(DPN_NAMESPACE='aptrust')
class BagDetailViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json',]

    def setUp(self):
        make_test_nodes()
        make_test_bags(100)
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()
        bag = Bag.objects.filter(original_node__namespace=settings.DPN_NAMESPACE)[0]
        self.url = reverse('api:bag-detail',
                           kwargs={'uuid': bag.uuid})
    def test_get(self):
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION='token %s' % token.key)
        rsp = self.client.get(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_200_OK)

    def _test_status(self, usr, fn, exp_code):
        # It should not allow this method.
        token = Token.objects.get(user=usr)
        self.client.credentials(HTTP_AUTHORIZATION='Token %s' % token.key)
        rsp = fn(self.url, {})
        self.assertEqual(rsp.status_code, exp_code, rsp.data)

    def test_post(self):
        # You can't post to this endpoint
        self._test_status(self.api_admin, self.client.post,
                          status.HTTP_405_METHOD_NOT_ALLOWED)
        self._test_status(self.api_user, self.client.post,
                          status.HTTP_403_FORBIDDEN)

    def test_patch(self):
        #self._test_status(self.api_admin, self.client.patch,
                            # status.HTTP_405_METHOD_NOT_ALLOWED)
        self._test_status(self.api_user, self.client.patch,
                          status.HTTP_403_FORBIDDEN)

    def test_put(self):

        def _test_expected_codes(usr, exp_code):
            token = Token.objects.get(user=usr)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            rsp = self.client.get(self.url)
            data = rsp.data.copy()
            data["bag_size"] = "100"
            rsp = self.client.put(self.url, data)
            self.assertEqual(rsp.status_code, exp_code)

        # It should allow api_admins to update bags
        _test_expected_codes(self.api_user, status.HTTP_403_FORBIDDEN)
        _test_expected_codes(self.api_admin, status.HTTP_200_OK)

    def test_delete(self):

        def _test_expected_codes(usr, exp_code):
            token = Token.objects.get(user=usr)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % exp_code)
            rsp = self.client.delete(self.url)
            self.assertEqual(rsp.status_code, exp_code)

        # It should not allow deleting for api users or admins.
        _test_expected_codes(self.api_user, status.HTTP_401_UNAUTHORIZED)
        _test_expected_codes(self.api_admin, status.HTTP_401_UNAUTHORIZED)

@override_settings(DPN_NAMESPACE='aptrust')
class ReplicationTransferDetailViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json']

    def setUp(self):
        make_test_nodes()
        make_test_bags(100)
        make_test_transfers()

        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()
        self.superuser = User.objects.create_superuser(
            username="supertest",
            password="supertest",
            email="superuser@email.com"
        )

    def test_get(self):

        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        # It should allow authenticated users to see xfers from their own node
        # Test replication objects are generated randomly, so there may not
        # be one for our api_user's node. Let's make sure there is one...
        replication = ReplicationTransfer.objects.first()
        replication.from_node = self.api_user.profile.node
        replication.save()

        xfer = self.api_user.profile.node.transfers_out.all()[0]
        url = reverse('api:replication-detail',
                      kwargs={"replication_id": xfer.replication_id})
        rsp = self.client.get(url)

        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.content)

        # It should not allow authenticated user to see xfers from other nodes
        # xfer = ReplicationTransfer.objects.exlude(to_node=self.api_user.profile.node)[0]

        #_test_own_node(self.api_admin)

        # def _test_other_node(usr):
        #     xfer = ReplicationTransfer.objects.exclude(to_node=usr.profile.node)[0]
        #     url = reverse('api:transfer-detail',
        #                   kwargs={'event_id': xfer.event_id})
        #     token = Token.objects.get(user=usr)
        #     self.client.credentials(HTTP_AUTHORIZATION="Token %s"
        #                                                % token.key)
        #     rsp = self.client.get(url)
        #     self.assertEqual(rsp.status_code, status.HTTP_200_OK)

        # _test_other_node(self.api_user)
        # _test_other_node(self.api_admin)
