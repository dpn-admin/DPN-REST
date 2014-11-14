"""
    I fantasize and idealize myself as Bugs Bunny, but I know deep down I'm
    Daffy Duck.
                    - Patton Oswalt

"""
import json
import random

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from dpn.data.models import Node, RegistryEntry, Transfer, UserProfile
from dpn.data.utils import dpn_strptime
from dpn.data.tests.utils import make_test_transfers, make_test_registry_entries
from dpn.data.tests.utils import make_test_nodes, make_registry_postdata
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

class RegistryListViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json', ]

    def setUp(self):
        # Setup Test Data
        make_test_nodes()
        make_test_registry_entries(100)
        make_test_transfers()

        self.url = reverse('api:registry-list')

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

        entries = RegistryEntry.objects.all()
        data = json.loads(response.content.decode('utf8'))

        # It should contain the right count of registry entries.
        self.assertEqual(data['count'], entries.count())
        previous = None
        for result in data['results']:
            current = dpn_strptime(result["last_modified_date"])
            if previous:
                self.assertTrue(current > previous)
            previous = current

    def test_put(self):
        # It should not allow this method.
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
        data = make_registry_postdata()

        # It should not allows api_users to create a record
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # It should allow api_admins to create a record.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data, format="json")
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED)


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
            profile = UserProfile.objects.get(user=u)
            token = Token.objects.get(user=u)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            rsp = self.client.get(self.url)
            data = json.loads(rsp.content.decode('utf8'))
            self.assertEqual(data['count'], 5)

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
        for token in tokens:
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            # put not allowed
            rsp = self.client.put(self.url)
            self.assertEqual(rsp.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)
            # patch not allowed
            rsp = self.client.patch(self.url)
            self.assertEqual(rsp.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)
            # delete not allowed
            rsp = self.client.delete(self.url)
            self.assertEqual(rsp.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)


class TransferListViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json', ]

    def setUp(self):
        # Setup Test Data
        make_test_nodes()
        make_test_registry_entries(100)
        make_test_transfers()
        self.url = reverse('api:transfer-list')
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()

    def test_get(self):

        def _test_return_count(user, url, exp_count):
            # Tests for expected object count.
            token = Token.objects.get(user=user)
            self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
            rsp = self.client.get(url)
            data = json.loads(rsp.content.decode('utf8'))
            self.assertEqual(data["count"], exp_count, "%s" % data["count"])
            self.assertEqual(rsp.status_code, status.HTTP_200_OK)

        # It should return only transfers for the users node.
        xfers = Transfer.objects.filter(node=self.api_user.profile.node)
        _test_return_count(self.api_user, self.url, xfers.count())

        # It should return all transfers for superusers.
        xfers = Transfer.objects.all()
        _test_return_count(self.api_admin, self.url, xfers.count())

        mynode = Node.objects.get(me=True)
        # It should filter transfers by dpn_object_id
        reg = RegistryEntry.objects.filter(first_node=mynode).order_by('?')[0]
        xfers = Transfer.objects.filter(registry_entry=reg)
        url = "%s?dpn_object_id=%s" % (reverse('api:transfer-list'),
                                       reg.dpn_object_id)
        _test_return_count(self.api_admin, url, xfers.count())

        # It should filter transfers by status
        xfer = Transfer.objects.filter(node=self.api_user.profile.node)[0]
        xfer.status = "A"
        xfer.save()
        url = "%s?status=A" % reverse('api:transfer-list')
        _test_return_count(self.api_user, url, 1)

        # It should filter based on Fixity.
        xfer.receipt = xfer.exp_fixity
        xfer.save()
        url = "%s?fixity=True" % reverse('api:transfer-list')
        _test_return_count(self.api_user, url, 1)

        # It should filter based on Node
        node = self.api_user.profile.node
        xfers = Transfer.objects.filter(node=node)
        url = "%s?node=%s" % (reverse('api:transfer-list'), node.namespace)
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
        reg = RegistryEntry.objects.filter(first_node__me=True)[0]
        data = {
            "dpn_object_id": reg.dpn_object_id,
            "link": "sshaccount@dpnserver.test.org:%s.tar" % reg.dpn_object_id,
            "node": Node.objects.exclude(me=True)[0].namespace,
            "size": random.getrandbits(32),
            "exp_fixity": "%x" % random.getrandbits(128),
        }

        # It should allow api_admins  to create transfers.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data, format="json")
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(rsp.data, data)

    def test_put(self):
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.put(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


## Detail Views
class RegistryDetailViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json',]

    def setUp(self):
        make_test_nodes()
        make_test_registry_entries(100)
        self.api_user = _make_api_user()
        self.api_admin = _make_api_admin()
        entry = RegistryEntry.objects.filter(first_node__me=True)[0]
        self.url = reverse('api:registry-detail',
                           kwargs={'dpn_object_id': entry.dpn_object_id})
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
        self.assertEqual(rsp.status_code, exp_code)

    def test_post(self):
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

        # It should allow api_admins to update entries
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

class TransferDetailViewTest(APITestCase):

    fixtures = ['../data/GroupPermissions.json']

    def setUp(self):
        make_test_nodes()
        make_test_registry_entries(100)
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
        xfer = self.api_user.profile.node.transfer_set.all()[0]
        url = reverse('api:transfer-detail',
                      kwargs={"event_id": xfer.event_id})
        rsp = self.client.get(url)

        self.assertEqual(rsp.status_code, status.HTTP_200_OK,  rsp.content)

        # It should not allow authenticated user to see xfers from other nodes
        # xfer = Transfer.objects.exlude(node=self.api_user.profile.node)[0]

        #_test_own_node(self.api_admin)

        # def _test_other_node(usr):
        #     xfer = Transfer.objects.exclude(node=usr.profile.node)[0]
        #     url = reverse('api:transfer-detail',
        #                   kwargs={'event_id': xfer.event_id})
        #     token = Token.objects.get(user=usr)
        #     self.client.credentials(HTTP_AUTHORIZATION="Token %s"
        #                                                % token.key)
        #     rsp = self.client.get(url)
        #     self.assertEqual(rsp.status_code, status.HTTP_200_OK)

        # _test_other_node(self.api_user)
        # _test_other_node(self.api_admin)