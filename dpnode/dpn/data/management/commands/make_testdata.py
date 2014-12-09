"""
    I asked God for a bike, but I know God doesn't work that way. So I stole a
    bike and asked for forgiveness.
            - Emo Philips
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from dpn.data.models import  Node, DATA, RSYNC, PENDING
from dpn.data.models import RegistryEntry, Transfer
from dpn.data.tests.utils import make_test_registry_entries, make_test_transfers
from dpn.data.tests.utils import make_test_nodes, make_test_user

class Command(BaseCommand):
    help = 'Wipes the database and reloads with test data.  USE WITH CAUTION!'

    def handle(self, *args, **options):
        if not settings.DEV:
            raise CommandError("ABORTING: This command should only be run in development!")

        print("Creating Test Nodes...")
        for node in Node.objects.all():
            node.delete()
        make_test_nodes()
        if not Node.objects.get(namespace=settings.DPN_NAMESPACE):
            raise CommandError("No %s node!" % settings.DPN_NAMESPACE)

        print("Importing usergroups...")
        call_command('loaddata', '../data/GroupPermissions.json')
        print("Creating Test Users...")
        for u in User.objects.all():
            u.delete()
        for node in Node.objects.exclude(namespace=settings.DPN_NAMESPACE):
            usr = make_test_user(
                    "%s_user" % node.namespace,
                    node.namespace,
                    "node@email.com",
                    groupname="api_users",
                    nodename=node.namespace
                    )

        # Clear Bag Data = funny pattern due to sqlite3
        for reg in RegistryEntry.objects.all():
            reg.delete()
        for xfer in Transfer.objects.all():
            xfer.delete()

        print("Creating Registry Entries...")
        make_test_registry_entries(1000)

        print("Creating Transfers...")
        make_test_transfers()

        print("Creating Superuser...")
        call_command("createsuperuser")
