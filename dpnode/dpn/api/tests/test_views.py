"""
    I fantasize and idealize myself as Bugs Bunny, but I know deep down I'm
    Daffy Duck.
                    - Patton Oswalt

"""
import json
from unittest import expectedFailure
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from dpn.data.models import Node, RegistryEntry, Transfer, UserProfile
from dpn.data.tests.utils import make_test_transfers, make_test_registry_entries
from dpn.data.tests.utils import make_test_nodes, make_registry_postdata

def _make_user(uname, pwd, eml, groupname):
    # setup API user

    api_user = User(
        username=uname,
        password=pwd,
        email=eml
    )
    api_user.save()

    profile = UserProfile.objects.get(user=api_user)
    profile.node = Node.objects.exclude(me=True)[0]
    profile.save()

    group = Group.objects.get(name=groupname)
    group.user_set.add(api_user)
    Token.objects.create(user=api_user)
    return api_user

def _make_api_user():
    return _make_user("apiuser", "apiuser", "me@email.com", "api_users")

def _make_api_admin():
    return _make_user("adminuser", "adminuser", "me@email.com", "api_admins")

class RegistryView(APITestCase):

    fixtures = ['../data/GroupPermissions.json',]

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

    def test_put(self):
        # It should not allow this method.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.put(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        # It should not allow this method.
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.put(self.url)
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @expectedFailure # TODO get post method to take expected dict
    def test_post(self):
        data = make_registry_postdata()
        # It should forbid api_users from creating record
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # It should allow api_admins to create a record.
        token = Token.objects.get(user=self.api_admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.post(self.url, data)
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED)

class TransferListView(APITestCase):

    fixtures = ['../data/GroupPermissions.json',]

    def setUp(self):
        # Setup Test Data
        make_test_nodes()
        make_test_registry_entries(100)
        make_test_transfers()

        self.url = reverse('api:transfer-list')

        self.api_user = _make_api_user()

    def test_get(self):
        profile = UserProfile.objects.get(user=self.api_user)
        xfers = Transfer.objects.filter(node=profile.node)
        token = Token.objects.get(user=self.api_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" % token.key)
        rsp = self.client.get(self.url)
        data = json.loads(rsp.content.decode('utf8'))
        self.assertEqual(data['count'], xfers.count())
        self.assertEqual(rsp.status_code, status.HTTP_200_OK)

    def test_post(self):
        pass

    def test_put(self):
        pass

    def test_patch(self):
        pass