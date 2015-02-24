"""
    Do not argue with an idiot. He will drag you down to his level and beat you
    with experience.
            - Unknown
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from dpn.data.models import Node, Protocol, Storage
from dpn.data.tests.utils import make_test_nodes

class Command(BaseCommand):
    help = 'Populates the DB with stub Node data'

    def handle(self, *args, **options):
        if not settings.DEV:
            raise CommandError("ABORTING: This command should only be run in development!")
        # Clear Everything out
        Storage.objects.all().delete()
        Node.objects.all().delete()

        make_test_nodes()
