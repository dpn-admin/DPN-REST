import json
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dpn.data.models import Node
from dpn.client.tasks import pull_registry_entries

class Command(BaseCommand):
    help = 'Pulls registry entries from all nodes or named node only if ' \
           'specified.'

    option_list = BaseCommand.option_list + (
        make_option("--node",
            dest="namespace",
            default=None,
            help="Namespace of specific node to pull registry entries from."
        ),
    )

    def handle(self, *args, **options):
        nodes = Node.objects.exclude(api_root__isnull=True).exclude(
                api_root__exact='').exclude(namespace=settings.DPN_NAMESPACE)
        if options['namespace']:
            nodes.filter(namespace=options['namespace'])

        if not nodes:
            raise CommandError("No nodes found to query.")

        for node in nodes:
            pull_registry_entries(node)
            self.stdout.write("Done pulling entries from %s" % node.namespace)