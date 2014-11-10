"""
    I asked God for a bike, but I know God doesn't work that way. So I stole a
    bike and asked for forgiveness.
            - Emo Philips
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dpn.data.models import  Node, DATA, RSYNC, PENDING
from dpn.data.models import RegistryEntry, Transfer
from dpn.data.tests.utils import make_test_registry_entries, make_test_transfers
from dpn.data.tests.utils import make_test_nodes

class Command(BaseCommand):
    help = 'Populates the DB with test data'

    def handle(self, *args, **options):
        if not settings.DEV:
            raise CommandError("ABORTING: This command should only be run in development!")

        make_test_nodes()
        if not Node.objects.get(name="APTrust"):
            raise CommandError("No node named APTrust")

        # Clear Bag Data = funny pattern due to sqlite3
        for reg in RegistryEntry.objects.all():
            reg.delete()
        for xfer in Transfer.objects.all():
            xfer.delete()

        # Make some registry entries
        make_test_registry_entries(1000)

        # Create Ingest Transfers
        make_test_transfers()
